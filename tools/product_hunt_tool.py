# producthunt_tool.py

import os
import requests
from dotenv import load_dotenv
from typing import List, Dict, Any

load_dotenv(override=True)

PRODUCTHUNT_TOKEN = os.getenv("PRODUCTHUNT_DEVELOPER_TOKEN")
BASE_URL = "https://api.producthunt.com/v2/api/graphql"

VALID_CATEGORIES = ["tech", "games", "books", "productivity", "design"]

def fetch_producthunt_posts(category: str = "tech", limit: int = 10) -> List[Dict[str, Any]]:
    """
    Fetch trending ProductHunt posts for a specific category.

    Args:
        category (str): Product category (default: "tech").
        limit (int): Number of posts to fetch (default: 10).

    Returns:
        List[Dict[str, Any]]: List of post information.
    """


    if category not in VALID_CATEGORIES:
        print(f"Category '{category}' is not valid. Using 'tech' instead.")
        category = "tech"

    headers = {
        "Authorization": f"Bearer {PRODUCTHUNT_TOKEN}",
        "Content-Type": "application/json",
    }

    

    query = """
    {
      posts(first: %d, order: VOTES, topic: "%s") {
        edges {
          node {
            name
            tagline
            votesCount
            createdAt
            url
          }
        }
      }
    }
    """ % (limit, category)

    try:
        response = requests.post(BASE_URL, json={"query": query}, headers=headers)
        response.raise_for_status()
        data = response.json()

        print("Top-level keys:", data)

    

        # Safely check if data exists
        posts_edges = data.get("data", {}).get("posts", {}).get("edges", [])
        return [edge["node"] for edge in posts_edges]

    except Exception as e:
        print(f"ProductHunt fetch error: {e}")
        return []
    

