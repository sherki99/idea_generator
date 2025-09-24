# reddit_search_and_load.py

from langchain_community.document_loaders import RedditPostsLoader
from langchain_community.tools.reddit_search.tool import (
    RedditSearchRun,
    RedditSearchAPIWrapper,
    RedditSearchSchema,
)
from dotenv import load_dotenv
import os
from typing import List

load_dotenv(override=True)

client_id = os.getenv("REDDIT_CLIENT_ID")
client_secret = os.getenv("REDDIT_CLIENT_SECRET")
user_agent = "agent_problem_hunter/0.1 by Consistent-Paint-650"

# Initialize Reddit search tool
reddit_search_tool = RedditSearchRun(
    api_wrapper=RedditSearchAPIWrapper(
        reddit_client_id=client_id,
        reddit_client_secret=client_secret,
        reddit_user_agent=user_agent,
    )
)


def search_only(
    query: str,
    subreddit: str = "all",
    time_filter: str = "month",
    sort: str = "new",
    limit: str = "5",
    language:  str = "en",
) -> List[str]:
    """
    Use RedditSearchRun to search posts by query.
    Returns raw search results.
    """
    search_params = RedditSearchSchema(
        query=query,
        time_filter=time_filter,
        subreddit=subreddit,
        limit=limit,
        sort=sort,
        language=language
    )

    result = reddit_search_tool.run(tool_input=search_params.dict())

    if isinstance(result, str):
        return result
    elif isinstance(result, dict):
        return str(result)
    else:
        return f"Reddit search results for: {query}"

def search_and_load_reddit_posts(
    query: str,
    subreddits: List[str] = None,
    categories: List[str] = None,
    max_posts: int = 50,
) -> List[str]:
    """
    Search Reddit for a query, then load the full posts as documents.
    """
    if subreddits is None:
        subreddits = ["all"]
    if categories is None:
        categories = ["new", "hot"]

    # Step 1: Search Reddit for post URLs or IDs
    search_results = reddit_search_tool.invoke({
        "query": query,
        "sort": "top",
        "time_filter": "week",
        "limit": max_posts,
    })

    # Step 2: Load full post content as documents
    loader = RedditPostsLoader(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=user_agent,
        categories=categories,
        mode="url_list",               # load specific posts by URL or ID
        search_queries=search_results, # pass search results
        number_posts=max_posts,
    )
    
    docs = loader.load()

    # Return only the textual content
    return [doc.page_content for doc in docs]

def load_post_only(
    query: str,
    subreddits: List[str] = None,
    categories: List[str] = None,
) -> List[str]:
    """
    Load posts from specified subreddits and filter by query keyword.
    """
    if subreddits is None:
        subreddits = ["all"]
    if categories is None:
        categories = ["new", "hot"]

    loader = RedditPostsLoader(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=user_agent,
        categories=categories,
        mode="subreddit",   # load directly from subreddits
        search_queries=subreddits,
        number_posts=50,
    )

    docs = loader.load()

    # Filter posts by query string (case-insensitive)
    return [doc.page_content for doc in docs if query.lower() in doc.page_content.lower()]
        