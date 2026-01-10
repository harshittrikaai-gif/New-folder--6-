"""Workflow node type implementations."""
from abc import ABC, abstractmethod
from typing import Dict, Any
import httpx
import json
import logging

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

from ..core.config import get_settings
from ..engine.rag import RAGEngine

settings = get_settings()
logger = logging.getLogger(__name__)


class BaseNode(ABC):
    """Base class for workflow nodes."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.params = config.get("params", {})
        self.label = config.get("label", "Node")
    
    @abstractmethod
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the node with input data."""
        pass
    
    async def _safe_execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Safe execution with error handling."""
        try:
            return await self.execute(input_data)
        except Exception as e:
            logger.error(f"Error in {self.label}: {str(e)}")
            return {
                "error": str(e),
                "node": self.label,
                "success": False
            }


class LLMNode(BaseNode):
    """LLM node for text generation with template support."""
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute LLM node."""
        prompt_template = self.params.get("prompt", "{input}")
        model = self.params.get("model", settings.openai_model)
        temperature = float(self.params.get("temperature", 0.7))
        max_tokens = int(self.params.get("max_tokens", 1000))
        
        try:
            # Format prompt with input data
            prompt = prompt_template.format(**input_data) if "{" in prompt_template else prompt_template
        except KeyError as e:
            return {
                "error": f"Missing variable in prompt: {str(e)}",
                "success": False
            }
        
        try:
            llm = ChatOpenAI(
                model=model,
                api_key=settings.openai_api_key,
                temperature=temperature,
                max_tokens=max_tokens
            )
            response = await llm.ainvoke([HumanMessage(content=prompt)])
            
            return {
                "output": response.content,
                "model": model,
                "success": True
            }
        except Exception as e:
            return {
                "error": str(e),
                "success": False
            }


class CodeNode(BaseNode):
    """Code execution node (sandboxed Python)."""
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Python code with sandboxed environment."""
        code = self.params.get("code", "output = input_data")
        
        # Create safe execution environment
        safe_globals = {
            "input_data": input_data,
            "json": json,
            "__builtins__": {
                "len": len,
                "str": str,
                "int": int,
                "float": float,
                "list": list,
                "dict": dict,
                "bool": bool,
                "range": range,
                "enumerate": enumerate,
                "zip": zip,
                "map": map,
                "filter": filter,
                "sum": sum,
                "min": min,
                "max": max,
                "sorted": sorted,
                "reversed": reversed,
                "abs": abs,
                "all": all,
                "any": any,
                "isinstance": isinstance,
                "type": type,
            }
        }
        local_vars = {}
        
        try:
            exec(code, safe_globals, local_vars)
            
            return {
                "output": local_vars.get("output", local_vars),
                "success": True
            }
        except Exception as e:
            return {
                "error": str(e),
                "success": False,
                "code": code
            }


class HTTPNode(BaseNode):
    """HTTP request node with template support."""
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute HTTP request."""
        method = self.params.get("method", "GET").upper()
        url = self.params.get("url", "")
        headers = self.params.get("headers", {})
        body = self.params.get("body")
        timeout = float(self.params.get("timeout", 30))
        
        try:
            # Format URL with input data
            if "{" in url:
                url = url.format(**input_data)
            
            # Format body if present
            if body:
                if isinstance(body, dict):
                    body_str = json.dumps(body)
                else:
                    body_str = str(body)
                
                if "{" in body_str:
                    body_str = body_str.format(**input_data)
                body = body_str
            
            # Format headers
            formatted_headers = {}
            for key, value in headers.items():
                if isinstance(value, str) and "{" in value:
                    formatted_headers[key] = value.format(**input_data)
                else:
                    formatted_headers[key] = value
            
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=formatted_headers,
                    content=body
                )
                
                try:
                    data = response.json()
                except json.JSONDecodeError:
                    data = response.text
                
                return {
                    "status_code": response.status_code,
                    "data": data,
                    "headers": dict(response.headers),
                    "success": 200 <= response.status_code < 300
                }
        except Exception as e:
            return {
                "error": str(e),
                "success": False,
                "url": url,
                "method": method
            }


class ConditionNode(BaseNode):
    """Conditional branching node."""
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate condition and return branch."""
        condition = self.params.get("condition", "True")
        
        try:
            # Evaluate condition with input data available
            result = eval(condition, {
                "input": input_data,
                **input_data,
                # Common comparison functions
                "len": len,
                "str": str,
                "int": int,
                "float": float,
                "bool": bool,
            })
            
            return {
                "result": bool(result),
                "branch": "true" if result else "false",
                "condition": condition,
                "success": True
            }
        except Exception as e:
            return {
                "error": str(e),
                "success": False,
                "condition": condition
            }


class RAGNode(BaseNode):
    """RAG query node for document retrieval."""
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Query RAG engine for documents."""
        query_template = self.params.get("query", "{input}")
        k = int(self.params.get("k", 5))
        
        try:
            # Format query with input data
            if "{" in query_template:
                query = query_template.format(**input_data)
            else:
                query = query_template
            
            rag_engine = RAGEngine()
            results = await rag_engine.query(query, k=k)
            
            return {
                "documents": results.get("documents", []),
                "sources": results.get("sources", []),
                "query": query,
                "success": True
            }
        except Exception as e:
            logger.warning(f"RAG query failed: {str(e)}")
            return {
                "documents": [],
                "sources": [],
                "warning": str(e),
                "success": False
            }


class TransformNode(BaseNode):
    """Data transformation node with multiple strategies."""
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform input data."""
        transform_type = self.params.get("type", "passthrough")
        
        try:
            if transform_type == "passthrough":
                return input_data
            
            elif transform_type == "extract":
                key = self.params.get("key")
                if not key:
                    return {"error": "Missing 'key' parameter", "success": False}
                
                value = input_data.get(key)
                return {
                    "output": value,
                    "key": key,
                    "success": True
                }
            
            elif transform_type == "merge":
                merge_data = self.params.get("merge", {})
                return {
                    "output": {**input_data, **merge_data},
                    "success": True
                }
            
            elif transform_type == "template":
                template = self.params.get("template", "{}")
                output = template.format(**input_data)
                return {
                    "output": output,
                    "success": True
                }
            
            elif transform_type == "map":
                mapping = self.params.get("mapping", {})
                output = {}
                for key, source_key in mapping.items():
                    output[key] = input_data.get(source_key)
                return {
                    "output": output,
                    "success": True
                }
            
            elif transform_type == "filter":
                filters = self.params.get("filters", {})
                output = {k: v for k, v in input_data.items() if k in filters.get("keys", [])}
                return {
                    "output": output,
                    "success": True
                }
            
            else:
                return {
                    "error": f"Unknown transform type: {transform_type}",
                    "success": False
                }
        
        except Exception as e:
            return {
                "error": str(e),
                "success": False,
                "type": transform_type
            }


class InputNode(BaseNode):
    """Workflow input node."""
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Pass through input data."""
        return {**input_data, "success": True}


class OutputNode(BaseNode):
    """Workflow output node."""
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Finalize output."""
        output_key = self.params.get("output_key", "result")
        return {
            output_key: input_data,
            "success": True
        }


class LoopNode(BaseNode):
    """Loop node for iterating over data."""
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute loop over data."""
        items_key = self.params.get("items_key", "items")
        items = input_data.get(items_key, [])
        
        if not isinstance(items, list):
            return {
                "error": f"Expected list for {items_key}, got {type(items).__name__}",
                "success": False
            }
        
        return {
            "items": items,
            "count": len(items),
            "success": True
        }


class SearchNode(BaseNode):
    """Web search node."""
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform web search."""
        from ..tools.search import search_web
        
        query_template = self.params.get("query", "{input}")
        num_results = int(self.params.get("num_results", 5))
        
        try:
            # Format query
            if "{" in query_template:
                query = query_template.format(**input_data)
            else:
                query = query_template
            
            # Perform search
            results = await search_web.ainvoke(query)
            
            return {
                "results": results,
                "query": query,
                "count": len(results),
                "success": True
            }
        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            return {
                "error": str(e),
                "success": False
            }


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
    "loop": LoopNode,
    "search": SearchNode,
}


def create_node(node_type: str, config: Dict[str, Any]) -> BaseNode:
    """Factory function to create nodes."""
    node_class = NODE_TYPES.get(node_type)
    if not node_class:
        raise ValueError(f"Unknown node type: {node_type}. Available: {list(NODE_TYPES.keys())}")
    return node_class(config)
