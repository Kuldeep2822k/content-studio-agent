"""Simple web search tool abstraction using SerpAPI.

This wraps the SerpAPI Google Search API and returns a normalized list of
results that the agent can consume. It demonstrates a real external tool
integration for the capstone.
"""

from __future__ import annotations

import logging
from typing import List, Dict, Any

import requests

from config import get_serpapi_key

logger = logging.getLogger(__name__)

SERPAPI_ENDPOINT = "https://serpapi.com/search"


def search_web(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """Return a list of {title, url, snippet} dicts using SerpAPI.

    If SerpAPI is not configured or the request fails, we fall back to a
    small set of placeholder results so that the rest of the pipeline keeps
    working for demos.
    """
    logger.info("search_web called", extra={"query": query, "max_results": max_results})

    api_key = get_serpapi_key(optional=True)
    if not api_key:
        logger.warning("SERPAPI_API_KEY not set; returning placeholder search results")
        return _placeholder_results(query, max_results)

    try:
        resp = requests.get(
            SERPAPI_ENDPOINT,
            params={
                "engine": "google",
                "q": query,
                "api_key": api_key,
                "num": max_results,
            },
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
    except Exception as exc:  # noqa: BLE001 - we log and fall back gracefully.
        logger.warning("SerpAPI request failed; using placeholder results", extra={"error": str(exc)})
        return _placeholder_results(query, max_results)

    organic_results = data.get("organic_results") or []
    results: List[Dict[str, Any]] = []
    for item in organic_results[:max_results]:
        results.append(
            {
                "title": item.get("title") or "(no title)",
                "url": item.get("link") or item.get("url") or "",
                "snippet": item.get("snippet") or item.get("content") or "",
            }
        )

    if not results:
        return _placeholder_results(query, max_results)

    return results


def _placeholder_results(query: str, max_results: int) -> List[Dict[str, Any]]:
    """Fallback results when real web search is unavailable."""
    base = [
        {
            "title": f"Background on {query}",
            "url": "https://example.com/background",
            "snippet": f"High-level explanation and key points about {query}.",
        },
        {
            "title": f"Latest trends in {query}",
            "url": "https://example.com/trends",
            "snippet": f"Recent developments, best practices, and common pitfalls in {query}.",
        },
    ]
    return base[:max_results]
