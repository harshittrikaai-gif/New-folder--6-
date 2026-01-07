"""Workflow execution engine."""
from typing import Dict, Any, List
from collections import defaultdict

from ..models.workflow import Workflow, WorkflowNode, NodeType
from .nodes import create_node


class WorkflowExecutor:
    """Execute workflows with topological ordering."""
    
    def __init__(self):
        self.node_outputs: Dict[str, Any] = {}
    
    def _build_graph(self, workflow: Workflow) -> Dict[str, List[str]]:
        """Build adjacency list from workflow edges."""
        graph = defaultdict(list)
        for edge in workflow.edges:
            graph[edge.source].append(edge.target)
        return graph
    
    def _topological_sort(
        self, 
        workflow: Workflow
    ) -> List[str]:
        """Get execution order using topological sort."""
        graph = self._build_graph(workflow)
        node_ids = {node.id for node in workflow.nodes}
        
        # Calculate in-degrees
        in_degree = {node_id: 0 for node_id in node_ids}
        for source, targets in graph.items():
            for target in targets:
                if target in in_degree:
                    in_degree[target] += 1
        
        # Start with nodes that have no incoming edges
        queue = [node_id for node_id, degree in in_degree.items() if degree == 0]
        order = []
        
        while queue:
            node_id = queue.pop(0)
            order.append(node_id)
            
            for target in graph[node_id]:
                in_degree[target] -= 1
                if in_degree[target] == 0:
                    queue.append(target)
        
        return order
    
    def _get_node_input(
        self, 
        node: WorkflowNode, 
        workflow: Workflow,
        initial_input: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get input for a node from predecessors."""
        # Find edges pointing to this node
        input_data = {}
        
        for edge in workflow.edges:
            if edge.target == node.id:
                source_output = self.node_outputs.get(edge.source, {})
                input_data.update(source_output)
        
        # If no input from edges, use initial input (for entry nodes)
        if not input_data:
            input_data = initial_input
        
        return input_data
    
    async def execute(
        self, 
        workflow: Workflow, 
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute the workflow."""
        self.node_outputs = {}
        
        # Get execution order
        execution_order = self._topological_sort(workflow)
        
        # Map node IDs to nodes
        node_map = {node.id: node for node in workflow.nodes}
        
        # Execute nodes in order
        final_output = {}
        
        for node_id in execution_order:
            node = node_map.get(node_id)
            if not node:
                continue
            
            # Get node input
            node_input = self._get_node_input(node, workflow, input_data)
            
            # Create and execute node
            node_instance = create_node(
                node.config.type.value,
                node.config.model_dump()
            )
            
            output = await node_instance.execute(node_input)
            self.node_outputs[node_id] = output
            
            # If this is an output node, capture as final output
            if node.config.type == NodeType.OUTPUT:
                final_output = output
        
        return {
            "output": final_output,
            "node_outputs": self.node_outputs
        }
