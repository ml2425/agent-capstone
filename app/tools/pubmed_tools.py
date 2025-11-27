"""PubMed search tool for agents."""
from google.adk.tools import FunctionTool
from app.services.pubmed_service import search_pubmed, fetch_pubmed_article
from typing import Dict, List


def pubmed_search(keywords: str, max_results: int = 10) -> Dict:
    """
    Search PubMed by keywords.
    
    Args:
        keywords: Search query string
        max_results: Maximum number of results (default: 10)
    
    Returns:
        Dict with 'articles' list
    """
    try:
        articles = search_pubmed(keywords, max_results)
        return {
            "articles": articles,
            "count": len(articles)
        }
    except Exception as e:
        return {
            "articles": [],
            "count": 0,
            "error": str(e)
        }


def pubmed_fetch_article(pubmed_id: str) -> Dict:
    """
    Fetch article by PubMed ID.
    
    Args:
        pubmed_id: PubMed ID (with or without "PMID:" prefix)
    
    Returns:
        Dict with article details
    """
    try:
        article = fetch_pubmed_article(pubmed_id)
        return {
            "article": article,
            "success": True
        }
    except Exception as e:
        return {
            "article": None,
            "success": False,
            "error": str(e)
        }


pubmed_search_tool = FunctionTool(pubmed_search)
pubmed_fetch_tool = FunctionTool(pubmed_fetch_article)

