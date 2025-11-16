"""
Custom Web Search Tool for Google ADK

This module provides a web search functionality using DuckDuckGo.
"""

from typing import Dict, List
from duckduckgo_search import DDGS


def web_search(query: str, max_results: int = 5) -> Dict[str, List[Dict[str, str]]]:
    """
    Search the web for information using DuckDuckGo.

    Use this tool when you need to find current information, recent news,
    or any data that requires searching the internet.

    Args:
        query: The search query string
        max_results: Maximum number of search results to return (default: 5)

    Returns:
        A dictionary containing a list of search results with title, URL, and snippet
    """
    try:
        # Perform the search using DuckDuckGo
        ddgs = DDGS()
        results = ddgs.text(query, max_results=max_results)

        # Format the results
        formatted_results = []
        for result in results:
            formatted_results.append({
                "title": result.get("title", ""),
                "url": result.get("href", ""),
                "snippet": result.get("body", "")
            })

        return {
            "query": query,
            "results": formatted_results
        }

    except Exception as e:
        return {
            "query": query,
            "error": f"Search failed: {str(e)}",
            "results": []
        }
