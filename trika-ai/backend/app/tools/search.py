from typing import List, Dict, Any
from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun

@tool
def search_web(query: str) -> str:
    """Search the web for real-time information using DuckDuckGo.
    Use this tool when you need current events, news, or specific facts not in your training data."""
    search = DuckDuckGoSearchRun()
    return search.run(query)
