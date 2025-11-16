"""
Shared Tools for Multi-Agent System

This module provides tools used by various sub-agents.
"""

import math
from typing import Dict, List, Union
from ddgs import DDGS


def web_search(query: str, max_results: int = 5) -> Dict[str, List[Dict[str, str]]]:
    """
    Search the web for information using DuckDuckGo.

    Args:
        query: The search query string
        max_results: Maximum number of search results to return

    Returns:
        A dictionary containing search results
    """
    try:
        ddgs = DDGS()
        results = ddgs.text(query, max_results=max_results)

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


def calculate(expression: str) -> Dict[str, Union[str, float]]:
    """
    Evaluate a mathematical expression safely.

    Args:
        expression: A mathematical expression as a string

    Returns:
        A dictionary with the result
    """
    try:
        safe_dict = {
            "sqrt": math.sqrt,
            "sin": math.sin,
            "cos": math.cos,
            "tan": math.tan,
            "log": math.log10,
            "ln": math.log,
            "abs": abs,
            "round": round,
            "pow": pow,
            "exp": math.exp,
            "pi": math.pi,
            "e": math.e,
        }

        result = eval(expression, {"__builtins__": {}}, safe_dict)

        return {
            "expression": expression,
            "result": float(result),
            "success": True
        }

    except Exception as e:
        return {
            "expression": expression,
            "error": f"Calculation error: {str(e)}",
            "success": False
        }


def format_text(text: str, style: str = "paragraph") -> Dict[str, str]:
    """
    Format text in different styles.

    Args:
        text: The text to format
        style: The formatting style (paragraph, bullet, numbered)

    Returns:
        A dictionary with the formatted text
    """
    try:
        if style == "bullet":
            lines = text.strip().split('\n')
            formatted = '\n'.join([f"• {line.strip()}" for line in lines if line.strip()])
        elif style == "numbered":
            lines = text.strip().split('\n')
            formatted = '\n'.join([f"{i+1}. {line.strip()}" for i, line in enumerate(lines) if line.strip()])
        else:  # paragraph
            formatted = text.strip()

        return {
            "original_text": text,
            "formatted_text": formatted,
            "style": style,
            "success": True
        }

    except Exception as e:
        return {
            "error": f"Formatting error: {str(e)}",
            "success": False
        }
