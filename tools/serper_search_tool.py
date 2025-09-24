import os
from dotenv import load_dotenv
import json
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from langchain.tools import StructuredTool
import requests

load_dotenv(override=True)


def web_search_function(
    query: str,
    search_type: str = "search",
    num_results: int = 10,
    location: Optional[str] = None,
    country: Optional[str] = None,
    language: Optional[str] = None,
    time_range: Optional[str] = None,
    safe_search: bool = False,
) -> str:
    """
    Perform a customizable web search using the Serper API.

    Parameters:
        query (str): The main query/topic to search for.
        search_type (str, optional): Type of search: "search", "news", or "scholar". Defaults to "search".
        num_results (int, optional): Maximum number of search results to return. Defaults to 10.
        location (str, optional): Specific location for geotargeted search (e.g., "Milan, Italy").
        country (str, optional): Country code for search localization (e.g., "IT").
        language (str, optional): Preferred language of results (e.g., "it" for Italian).
        time_range (str, optional): Time range for results (e.g., "d"=day, "w"=week, "m"=month, "y"=year).
        safe_search (bool, optional): Enable safe search filtering. Defaults to False.

    Returns:
        str: JSON string containing search results or error information.
             Each result includes: title, snippet, URL, date, and source
    """
    api_key = os.getenv("SERPER_API_KEY")
    if not api_key:
        return json.dumps({"error": "SERPER_API_KEY not set", "results": []})

    url = f"https://google.serper.dev/{search_type}"
    headers = {"X-API-KEY": api_key, "Content-Type": "application/json"}

    payload = {"q": query, "num": num_results}
    if location: payload["location"] = location
    if country: payload["gl"] = country
    if language: payload["hl"] = language
    if time_range: payload["tbs"] = f"qdr:{time_range}"
    if safe_search: payload["safe"] = "active"

    try:
        resp = requests.post(url, headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()


        results = []
        for item in data.get("organic", [])[:num_results]:
           # print(item)
            results.append({
                "title": item.get("title"),
                "snippet": item.get("snippet"),
                "url": item.get("link"),
                "date": item.get("date"),
                "source": item.get("source") or item.get("domain") or "UnKnow",
            })

        return json.dumps({
            "query": query,
            "search_type": search_type,
            "total_results": len(results),
            "results": results,
        }, indent=2)

    except Exception as e:
        return json.dumps({"error": str(e), "results": []})


def create_websearch_tool():
    """Create LangChain StructuredTool for Serper web search"""
    return StructuredTool.from_function(
        name="web_search",
        description="Search the web/news/scholar using the Serper API",
        func=web_search_function,
      # args_schema=WebSearchInput,
        coroutine=None  # Not async anymore
    )

