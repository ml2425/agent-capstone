"""Tavily search tool wrapper for ChatGPT flow."""
from __future__ import annotations

import os
from typing import Dict

import requests
from google.adk.tools import FunctionTool

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
TAVILY_API_URL = "https://api.tavily.com/search"


def tavily_search(query: str, max_results: int = 5) -> Dict:
    """Perform a web search via Tavily API."""
    if not TAVILY_API_KEY:
        return {
            "error": "TAVILY_API_KEY not set. Please configure it in the environment."
        }
    payload = {
        "api_key": TAVILY_API_KEY,
        "query": query,
        "max_results": max_results,
        "include_answer": False,
    }
    try:
        response = requests.post(TAVILY_API_URL, json=payload, timeout=15)
        response.raise_for_status()
        data = response.json()
        results = data.get("results", [])
        snippets = [
            {"title": item.get("title"), "content": item.get("content")}
            for item in results
        ]
        return {"snippets": snippets}
    except Exception as exc:
        return {"error": f"Tavily search failed: {exc}"}


tavily_search_tool = FunctionTool(tavily_search)

