"""Workflow node type implementations."""
from abc import ABC, abstractmethod
from typing import Dict, Any
import httpx
import json

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

from ..core.config import get_settings
from ..engine.rag import RAGEngine

settings = get_settings()


class BaseNode(ABC):
    """Base class for workflow nodes."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.params = config.get("params", {})
    
    @abstractmethod
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the node with input data."""
        pass


class LLMNode(BaseNode):
    """LLM node for text generation."""
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        prompt_template = self.params.get("prompt", "{input}")
        model = self.params.get("model", settings.openai_model)
        
        # Format prompt with input data
        prompt = prompt_template.format(**input_data)
        
        llm = ChatOpenAI(model=model, api_key=settings.openai_api_key)
        response = await llm.ainvoke([HumanMessage(content=prompt)])
        
        return {"output": response.content}


class CodeNode(BaseNode):
    """Code execution node (sandboxed Python)."""
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        code = self.params.get("code", "output = input_data")
        
        # Create safe execution environment
        safe_globals = {
            "input_data": input_data,
            "json": json,
            "__builtins__": {
                "len": len, "str": str, "int": int, "float": float,
                "list": list, "dict": dict, "bool": bool,
                "range": range, "enumerate": enumerate,
                "zip": zip, "map": map, "filter": filter,
                "sum": sum, "min": min, "max": max,
                "sorted": sorted, "reversed": reversed,
            }
        }
        local_vars = {}
        
        exec(code, safe_globals, local_vars)
        
        return {"output": local_vars.get("output", local_vars)}


class HTTPNode(BaseNode):
    """HTTP request node."""
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        method = self.params.get("method", "GET").upper()
        url = self.params.get("url", "").format(**input_data)
        headers = self.params.get("headers", {})
        body = self.params.get("body")
        
        if body:
            body = json.dumps(body) if isinstance(body, dict) else body
            body = body.format(**input_data)
        
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=method,
                url=url,
                headers=headers,
                content=body
            )
            
            try:
                data = response.json()
            except json.JSONDecodeError:
                data = response.text
            
            return {
                "status_code": response.status_code,
                "data": data
            }


class ConditionNode(BaseNode):
    """Conditional branching node."""
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        condition = self.params.get("condition", "True")
        
        # Evaluate condition
        result = eval(condition, {"input": input_data})
        
        return {
            "result": bool(result),
            "branch": "true" if result else "false"
        }


class RAGNode(BaseNode):
    """RAG query node."""
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        query = self.params.get("query", "{input}").format(**input_data)
        k = self.params.get("k", 5)
        
        rag_engine = RAGEngine()
        results = await rag_engine.query(query, k=k)
        
        return {
            "documents": results["documents"],
            "sources": results["sources"]
        }


class TransformNode(BaseNode):
    """Data transformation node."""
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        transform_type = self.params.get("type", "passthrough")
        
        if transform_type == "passthrough":
            return input_data
        elif transform_type == "extract":
            key = self.params.get("key")
            return {"output": input_data.get(key)}
        elif transform_type == "merge":
            return {"output": {**input_data}}
        elif transform_type == "template":
            template = self.params.get("template", "{}")
            return {"output": template.format(**input_data)}
        
        return input_data


class InputNode(BaseNode):
    """Workflow input node."""
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        return input_data


class OutputNode(BaseNode):
    """Workflow output node."""
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        return input_data


# Node type registry
NODE_TYPES = {
    "llm": LLMNode,
    "code": CodeNode,
    "http": HTTPNode,
    "condition": ConditionNode,
    "rag": RAGNode,
    "transform": TransformNode,
    "input": InputNode,
    "output": OutputNode,
}


def create_node(node_type: str, config: Dict[str, Any]) -> BaseNode:
    """Factory function to create nodes."""
    node_class = NODE_TYPES.get(node_type)
    if not node_class:
        raise ValueError(f"Unknown node type: {node_type}")
    return node_class(config)
