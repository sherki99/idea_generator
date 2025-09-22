# twitter_tool.py

import os
import requests
from dotenv import load_dotenv
from typing import List, Dict, Any

load_dotenv(override=True)

# Twitter credentials
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")

BASE_URL = "https://api.twitter.com/2/tweets/search/recent"

def search_tweets(query: str, max_results: int = 20, lang: str = "en") -> List[Dict[str, Any]]:
    """
    Search recent tweets for a given query.

    Args:
        query (str): Search keyword or hashtag.
        max_results (int): Maximum number of tweets to fetch (default 20, max 100 per request).
        lang (str): Language filter (default 'en').

    Returns:
        List[Dict[str, Any]]: List of tweets with text and metadata.
    """
    headers = {
        "Authorization": f"Bearer {TWITTER_BEARER_TOKEN}"
    }

    params = {
        "query": query,
        "max_results": max_results,
        "tweet.fields": "created_at,author_id,public_metrics,lang",
        "expansions": "author_id"
    }

    response = requests.get(BASE_URL, headers=headers, params=params)
    
    try:
        data = response.json()
        tweets = data.get("data", [])
        return tweets
    except Exception as e:
        print(f"❌ Twitter fetch error: {e}")
        return []
