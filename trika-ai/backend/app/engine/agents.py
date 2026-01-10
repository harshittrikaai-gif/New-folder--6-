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
        workflow.add_node("coder", self._coder_agent)
        workflow.add_node("responder", self._responder_agent)
        
        # Add edges
        workflow.set_entry_point("router")
        workflow.add_conditional_edges(
            "router",
            self._route_decision,
            {
                "research": "researcher",
                "code": "coder",
                "respond": "responder"
            }
        )
        workflow.add_edge("researcher", "responder")
        workflow.add_edge("coder", "responder")
        workflow.add_edge("responder", END)
        
        return workflow.compile()
    
    async def _router_agent(self, state: AgentState) -> AgentState:
        """Route to appropriate agent based on query."""
        messages = state["messages"]
        last_message = messages[-1]
        
        content = ""
        if isinstance(last_message, str):
            content = last_message.lower()
        elif hasattr(last_message, "content"):
            content = last_message.content.lower()
            
        # Code detection
        if any(w in content for w in ["code", "script", "function", "implement", "fix class", "write a program"]):
            return {"current_agent": "code"}
            
        # Research detection
        if any(w in content for w in ["search", "find", "look up", "latest news", "current event"]):
            return {"current_agent": "research"}
        
        # RAG context check
        if state.get("context"):
            return {"current_agent": "research"}
            
        return {"current_agent": "respond"}
    
    def _route_decision(self, state: AgentState) -> str:
        """Determine next agent."""
        return state["current_agent"]
    
    async def _researcher_agent(self, state: AgentState) -> AgentState:
        """Research agent that uses tools."""
        from ..tools.search import search_web
        
        messages = state["messages"]
        last_message = messages[-1]
        content = last_message.content if hasattr(last_message, "content") else str(last_message)
        
        # Extract query (simplified)
        search_query = content
        
        try:
            # We only search if it was explicitly a search request, 
            # otherwise this might be RAG processing
            if "search" in content.lower() or "find" in content.lower():
                # In a real app, use an LLM to extract the keyword
                search_result = search_web.invoke(search_query)
                research_summary = f"Search Results for '{search_query[:50]}...':\n\n{search_result}"
                
                return {
                    "messages": [SystemMessage(content=research_summary)],
                    "current_agent": "researcher"
                }
        except Exception:
            pass
            
        # Fallback or RAG processing
        context = state.get("context", "")
        if context:
            return {
                "messages": [SystemMessage(content=f"Context for analysis:\n{context}")],
                "current_agent": "researcher"
            }
            
        return {"current_agent": "researcher"}

    async def _coder_agent(self, state: AgentState) -> AgentState:
        """Specialized coding agent."""
        messages = state["messages"]
        
        system_prompt = """You are an expert software engineer.
        Write clean, efficient, and well-documented code.
        Explain your solution briefly before providing the code block.
        Always use markdown code blocks with the appropriate language tag."""
        
        # We invoke the LLM to generate the code/plan
        # In a more advanced version, this could use tools to run code
        
        # For now, we behave like a specialized responder
        # We wrap the response in a way that the final responder can use or refine it
        # Actually, let's just generate the code here and pass it to responder 
        # or let the responder do the final formatting.
        
        # Let's add a system message to guide the final response
        return {
            "messages": [SystemMessage(content=system_prompt)],
            "current_agent": "coder"
        }
    
    async def _responder_agent(self, state: AgentState) -> AgentState:
        """Final responder agent."""
        messages = state["messages"]
        current_agent = state.get("current_agent")
        
        system_prompt = """You are Trika, a helpful AI assistant. 
        Provide clear, accurate, and helpful responses."""
        
        if current_agent == "researcher":
            system_prompt += "\nSynthesize the provided research/context into a coherent answer. Cite sources."
        elif current_agent == "coder":
            system_prompt += "\nReview the code requirements and provide the solution. Ensure code is correct."
        
        # Build message history
        formatted_messages = [SystemMessage(content=system_prompt)]
        
        for msg in messages:
            if isinstance(msg, dict):
                continue
            formatted_messages.append(msg)
        
        response = await self.llm.ainvoke(formatted_messages)
        
        return {
            "output": response.content,
            "current_agent": "responder"
        }
    
    def _determine_intent(self, message: str) -> str:
        """Quick heuristic to determine intent."""
        msg_lower = message.lower()
        if any(w in msg_lower for w in ["search", "find", "look up", "latest"]):
            return "research"
        if any(w in msg_lower for w in ["code", "script", "function", "write a program", "implement"]):
            return "code"
        return "chat"

    async def stream_response(
        self,
        message: str,
        context: str = "",
        history: List[Dict[str, str]] = None
    ) -> AsyncGenerator[str, None]:
        """Stream response using hybrid routing (Fast Path vs Smart Path)."""
        history = history or []
        intent = self._determine_intent(message)
        
        # FAST PATH: Simple Chat
        if intent == "chat" and not context:
            # Build system prompt
            system_prompt = """You are Trika, a helpful AI assistant. 
            Provide clear, accurate, and helpful responses. 
            Be conversational and engaging."""
            
            messages = [{"role": "system", "content": system_prompt}]
            for hist_msg in history:
                messages.append(hist_msg)
            messages.append({"role": "user", "content": message})
            
            try:
                async for chunk in self.llm.astream(messages):
                    if hasattr(chunk, 'content') and chunk.content:
                        yield chunk.content
                return
            except Exception:
                # Fallback to Smart Path logic if fast path fails for some reason
                pass

        # SMART PATH: Complex-Agentic Workflow
        # We manually construct the initial state
        initial_messages = []
        for hist_msg in history:
             initial_messages.append(HumanMessage(content=hist_msg.get("content", "")) if hist_msg.get("role") == "user" else AIMessage(content=hist_msg.get("content", "")))
        initial_messages.append(HumanMessage(content=message))

        initial_state = {
            "messages": initial_messages,
            "context": context,
            "current_agent": "router",
            "output": ""
        }

        # For the smart path, we await the full result then yield it.
        # Ideally we would stream events from the graph, but for simplicity/stability
        # we'll wait for the graph to finish.
        # To make it feel responsive, we could yield a "Thinking..." status if the frontend supported it,
        # but for now we'll just yield the final result chunk-by-chunk or all at once.
        
        try:
            result = await self.graph.ainvoke(initial_state)
            final_output = result.get("output", "")
            
            # Simulate streaming for the frontend
            # (or we could just yield the whole thing, but yielding chunks is safer commonly)
            yield final_output
            
        except Exception as e:
            yield f"I encountered an error processing your request: {str(e)}"

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
