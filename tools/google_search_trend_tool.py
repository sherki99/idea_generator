import os
from typing import List, Dict, Any
from dotenv import load_dotenv
from langchain_community.tools.google_trends import GoogleTrendsQueryRun
from langchain_community.utilities.google_trends import GoogleTrendsAPIWrapper

load_dotenv(override=True)

os.environ["SERPAPI_API_KEY"] = os.getenv("SERPAPI_API_KEY")

google_trend_tool = GoogleTrendsQueryRun(
    api_wrapper=GoogleTrendsAPIWrapper()
)

def get_trend(query: str, geo: str = "US", timeframe: str = "now 7-d") -> Dict[str, Any]:
    """
    Fetch Google Trends data for a single query.

    Args:
        query (str): The search term to check.
        geo (str): Geographic region (default: "US").
        timeframe (str): Time range, e.g., "now 7-d", "today 12-m", "all".

    Returns:
        dict: Google Trends data response.
    """
    return google_trend_tool.run({
        "query": query,
      # I need to look hwo can be more specific 
      #  "geo": geo,
      #  "timeframe": timeframe
    })

def compare_trends(queries: List[str], geo: str = "US", timeframe: str = "today 12-m") -> Dict[str, Any]:
    """
    Compare multiple queries on Google Trends.

    Args:
        queries (List[str]): Search terms to compare.
        geo (str): Geographic region.
        timeframe (str): Time range.

    Returns:
        dict: Comparison result from Google Trends.
    """
    return google_trend_tool.run({
        "keyword": queries,
        "geo": geo,
        "timeframe": timeframe
    })

def rising_trends(query: str, geo: str = "US") -> Dict[str, Any]:
    """
    Fetch related rising queries for a given search term.

    Args:
        query (str): Base search term.
        geo (str): Geographic region.

    Returns:
        dict: Related rising queries.
    """
    return google_trend_tool.run({
        "keyword": query,
        "geo": geo,
        "related": "rising"
    })
