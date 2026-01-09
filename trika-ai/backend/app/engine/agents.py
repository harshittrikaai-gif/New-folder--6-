"""LangGraph multi-agent orchestrator."""
from typing import List, Dict, Any, AsyncGenerator, TypedDict, Annotated
import operator

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, END

from ..core.config import get_settings

settings = get_settings()


class AgentState(TypedDict):
    """State passed between agents."""
    messages: Annotated[List[Any], operator.add]
    context: str
    current_agent: str
    output: str


class AgentOrchestrator:
    """Multi-agent orchestration using LangGraph."""
    
    def __init__(self, model_name: str = None):
        self.model_name = model_name or settings.openai_model
        
        if "claude" in self.model_name:
            from langchain_anthropic import ChatAnthropic
            self.llm = ChatAnthropic(
                model_name=self.model_name,
                anthropic_api_key=settings.anthropic_api_key,
                streaming=True
            )
        else:
            self.llm = ChatOpenAI(
                model=self.model_name,
                api_key=settings.openai_api_key,
                streaming=True
            )
        
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the agent graph."""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("router", self._router_agent)
        workflow.add_node("researcher", self._researcher_agent)
        workflow.add_node("responder", self._responder_agent)
        
        # Add edges
        workflow.set_entry_point("router")
        workflow.add_conditional_edges(
            "router",
            self._route_decision,
            {
                "research": "researcher",
                "respond": "responder"
            }
        )
        workflow.add_edge("researcher", "responder")
        workflow.add_edge("responder", END)
        
        return workflow.compile()
    
    async def _router_agent(self, state: AgentState) -> AgentState:
        """Route to appropriate agent based on query."""
        messages = state["messages"]
        context = state.get("context", "")
        
        # Simple routing logic - if context exists, go to researcher
        if context:
            return {"current_agent": "research"}
        return {"current_agent": "respond"}
    
    def _route_decision(self, state: AgentState) -> str:
        """Determine next agent."""
        if state.get("context"):
            return "research"
        return "respond"
    
    async def _researcher_agent(self, state: AgentState) -> AgentState:
        """Research agent that processes context."""
        context = state.get("context", "")
        
        system_prompt = """You are a research assistant. Analyze the provided context 
        and extract key information relevant to the user's question. Be concise and factual."""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Context:\n{context}\n\nExtract key insights.")
        ]
        
        response = await self.llm.ainvoke(messages)
        
        return {
            "messages": [response],
            "current_agent": "researcher"
        }
    
    async def _responder_agent(self, state: AgentState) -> AgentState:
        """Final responder agent."""
        messages = state["messages"]
        
        system_prompt = """You are Trika, a helpful AI assistant. 
        Provide clear, accurate, and helpful responses. 
        If context or research was provided, use it to inform your response."""
        
        # Build message history
        formatted_messages = [SystemMessage(content=system_prompt)]
        for msg in messages:
            if isinstance(msg, dict):
                if msg["role"] == "user":
                    formatted_messages.append(HumanMessage(content=msg["content"]))
                elif msg["role"] == "assistant":
                    formatted_messages.append(AIMessage(content=msg["content"]))
            else:
                formatted_messages.append(msg)
        
        response = await self.llm.ainvoke(formatted_messages)
        
        return {
            "output": response.content,
            "current_agent": "responder"
        }
    
    async def stream_response(
        self,
        message: str,
        context: str = "",
        history: List[Dict[str, str]] = None
    ) -> AsyncGenerator[str, None]:
        """Stream response using the agent graph."""
        history = history or []
        
        # Initial state
        initial_state = {
            "messages": [HumanMessage(content=message)],
            "context": context,
            "current_agent": "router",
            "output": ""
        }
        
        # Add history to messages if needed (simplified for graph state)
        # Note: In a real complex graph, we might want to load full history
        
        # Execute graph
        async for event in self.graph.astream_events(initial_state, version="v1"):
            kind = event["event"]
            
            # Stream tokens from the LLM
            if kind == "on_chat_model_stream":
                content = event["data"]["chunk"].content
                if content:
                    yield content
                    
    async def generate_response(
        self,
        message: str,
        context: str = "",
        history: List[Dict[str, str]] = None
    ) -> str:
        """Generate a complete response using the agent graph."""
        full_response = ""
        async for chunk in self.stream_response(message, context, history):
            full_response += chunk
        return full_response
