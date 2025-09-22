# tools/openalex_tool.py

import requests
from typing import List, Dict, Any

BASE_URL = "https://api.openalex.org"


def search_organizations(query: str, per_page: int = 5) -> List[Dict[str, Any]]:
    """
    Search organizations (universities, companies, labs) on OpenAlex.

    Args:
        query (str): Keyword to search (e.g., "AI startup", "Tesla").
        per_page (int): Number of results to fetch (default 5).

    Returns:
        List[Dict]: List of organizations with key details.
    """
    url = f"{BASE_URL}/institutions"
    params = {
        "search": query,
        "per-page": per_page
    }
    response = requests.get(url, params=params)
    data = response.json()

    results = []
    for org in data.get("results", []):
        results.append({
            "id": org.get("id"),
            "name": org.get("display_name"),
            "country": org.get("country_code"),
            "type": org.get("type"),
            "works_count": org.get("works_count"),
            "homepage": org.get("homepage_url")
        })
    return results


def search_works(query: str, per_page: int = 5) -> List[Dict[str, Any]]:
    """
    Search research works (papers, patents) related to a query.

    Args:
        query (str): Topic or keyword (e.g., "Generative AI", "blockchain").
        per_page (int): Number of results to fetch (default 5).

    Returns:
        List[Dict]: List of research works.
    """
    url = f"{BASE_URL}/works"
    params = {
        "search": query,
        "per-page": per_page,
        "sort": "cited_by_count:desc"  # show most cited first
    }
    response = requests.get(url, params=params)
    data = response.json()

    results = []
    for work in data.get("results", []):
        results.append({
            "id": work.get("id"),
            "title": work.get("title"),
            "publication_date": work.get("publication_date"),
            "cited_by_count": work.get("cited_by_count"),
            "authorships": [a.get("author", {}).get("display_name") for a in work.get("authorships", [])],
            "doi": work.get("doi"),
            "url": work.get("primary_location", {}).get("landing_page_url"),
        })
    return results


def search_authors(query: str, per_page: int = 5) -> List[Dict[str, Any]]:
    """
    Search for authors/researchers related to a topic.

    Args:
        query (str): Keyword or author name.
        per_page (int): Number of results to fetch (default 5).

    Returns:
        List[Dict]: Author details.
    """
    url = f"{BASE_URL}/authors"
    params = {
        "search": query,
        "per-page": per_page
    }
    response = requests.get(url, params=params)
    data = response.json()

    results = []
    for author in data.get("results", []):
        results.append({
            "id": author.get("id"),
            "name": author.get("display_name"),
            "works_count": author.get("works_count"),
            "cited_by_count": author.get("cited_by_count"),
            "last_known_institution": author.get("last_known_institution", {}).get("display_name"),
        })
    return results


# Quick test
if __name__ == "__main__":
    print("🔍 Testing OpenAlex Organization Search")
    orgs = search_organizations("AI startup")
    for o in orgs:
        print(o)

    print("\n📚 Testing OpenAlex Works Search")
    works = search_works("Generative AI")
    for w in works:
        print(w)

    print("\n👩‍🔬 Testing OpenAlex Authors Search")
    authors = search_authors("Elon Musk")
    for a in authors:
        print(a)
