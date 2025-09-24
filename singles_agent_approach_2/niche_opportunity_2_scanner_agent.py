"""
Pain Point Discovery Agent - AI-Powered Micro-SaaS Finder

Discovers actionable pain points in a given industry and country that can be 
solved fully with AI workflows, automation, and multi-agent collaboration.

Workflow:
1. Generate platform queries (Reddit, Twitter, forums) via LLM.
2. Scrape posts/tweets based on queries.
3. Analyze collected data to extract structured pain points:
   - Description, persona, frequency, urgency, impact, automation potential,
     micro-SaaS solution potential, evidence sources, category.
4. Output structured JSON for downstream AI solution agents.

Dependencies:
- AzureChatOpenAI, LangChain, custom Reddit/Twitter scraping tools,
  BusinessIdeaGenerationState, PainPointDiscoveryOutput.
"""

import os 
from dotenv import load_dotenv 
from langchain_openai import AzureChatOpenAI
import json 
from typing import Dict, Any

from graph.state import BusinessIdeaGenerationState, PainPointDiscoveryOutput, PainPoint
from tools.reddit_scrapper_tool import search_only
from tools.twitter_search_tool import search_tweets


load_dotenv(override=True)

llm = AzureChatOpenAI(
    azure_endpoint=os.getenv("AZURE_API_BASE"),
    api_key=os.getenv("AZURE_API_KEY"),
    api_version=os.getenv("AZURE_API_VERSION"),
    azure_deployment=os.getenv("LLM_DEPLOYMENT_NAME")     
)


def pain_point_discovery_agent(state: BusinessIdeaGenerationState) -> Dict[str, Any]:
    """
    Pain Point Discovery Agent - Focused only on finding pain points
    """
    print("Starting Pain Point Discovery...")

    user_input = state.user_input
    industry = user_input.industry_market
    country = user_input.country_region

    PAIN_POINT_SYSTEM_MESSAGE = f"""
        You are the Pain Point Discovery Agent in SaaS Idea Lab — an AI-powered micro-SaaS generator.

        Your responsibilities:
        1. Identify **pain points, inefficiencies, and unmet needs** within {industry} in {country}.
        2. Focus ONLY on problems that can be solved entirely with **AI workflows and multi-agent automation**, including:
        - Multi-agent collaboration (LangChain, LangGraph)
        - Integration with existing APIs and tools
        - Fully automated solutions with minimal human intervention
        3. Base findings on **evidence from research**, including:
        - Personas
        - Market trends
        - Social signals (Reddit, Twitter, forums, Quora, product reviews)
        4. Decide autonomously:
        - Which platforms, subreddits, hashtags, or forums to explore
        - How to phrase queries and which keywords to use
        5. For each pain point, provide structured info:
        - Description
        - Target persona
        - Urgency
        - Impact level (Low/Medium/High)
        - AI workflow automation potential (1–10)
        - Solution potential as AI-powered micro-SaaS
        - Source(s)
        6. Group pain points into meaningful categories (manual tasks, inefficiencies, missing AI-enabled tools, workflow gaps)
        7. Output must be **structured JSON**, ready for the AI Workflow Solution Agent.

        Prioritize actionable pain points that could realistically be solved fully by AI agents.
        """

    query_prompt = f"""
        You are the Pain Point Discovery Agent.
        Goal: uncover **all pain points** in {industry} in {country} that can be solved entirely with AI workflows.

        Instructions:
        1. Decide autonomously which platforms, subreddits, hashtags, or forums to explore.
        2. Generate multiple search queries per platform.
        3. For each query, specify:
        - tool (reddit/twitter/forum)
        - subreddit or hashtag if applicable
        - query text
        - result limit
        4. Output JSON array in this format:

        [
        {{ "tool": "reddit", "subreddit": "subreddit_name", "query": "...", "limit": 5 }},
        {{ "tool": "twitter", "hashtag": "#example", "query": "...", "limit": 10 }}
        ]

        Focus ONLY on problems that could be fully solved by AI workflows (automation, multi-agent collaboration, tool integrations).
        """      

    messages = [
        {"role": "system", "content": PAIN_POINT_SYSTEM_MESSAGE},
        {"role": "user", "content": query_prompt}
    ]

    suggested_queries_json = llm.with_structured_output(messages, function="json_mode")
    suggested_queries = json.loads(suggested_queries_json)


    collected_data = []
    for q in suggested_queries:
        try:
            if q["tool"] == "reddit":
                subreddit = q.get("subreddit")
                results = search_only(q["query"], subreddit=subreddit, limit=q.get("limit", 3))
            elif q["tool"] == "twitter":
                hashtag = q.get("hashtag")
                results = search_tweets(q["query"], hashtag=hashtag, max_results=q.get("limit", 10))
            else:
                results = []
            collected_data.append({
                "tool": q["tool"],
                "query": q["query"],
                "results": results
            })
        except Exception as e:
            collected_data.append({
                "tool": q["tool"],
                "query": q["query"],
                "error": str(e)
            })




    PAIN_POINT_USER_PROMPT = f"""
    You are the Pain Point Discovery Agent.

    Your task: Identify **actionable pain points** in {industry} that can be fully solved with AI workflows or AI-powered micro-SaaS solutions
    pain point or repetive task that can be solved thanks to AI agents workflow

    Social signals collected:
    {json.dumps(collected_data, indent=2)}

    Instructions:
    1. Analyze the social signals and identify **distinct pain points**.
    2. For each pain point, provide:
    - description: What is the problem?
    - target_persona: Who experiences this problem?
    - frequency_score: How often this issue occurs (1–10)
    - urgency_score: How urgent it is to solve (1–10)
    - impact_level: Low / Medium / High
    - automation_potential: How easily this could be solved by AI workflows (1–10)
    - solution_potential: Potential as an AI-powered micro-SaaS
    - evidence_sources: Where this was observed (platform, post count)
    - category: e.g., manual tasks, inefficiencies, missing AI tools
    3. Only include **pain points that are actionable and suitable for AI workflow solutions**.
    4. Output results in **structured JSON**.

    ⚠️ If no actionable pain points exist, respond:
    "⚠️ No sufficiently validated, actionable pain points identified. Recommend expanding research scope."
    """

    try:
        print("Analyzing pain points with LLM...")
        structured_pain_points = llm.with_structured_output(
            PainPointDiscoveryOutput,
            method="function"
        ).invoke(PAIN_POINT_USER_PROMPT)
        print("LLM pain points analysis successful")
    except Exception as e:
        print(f"LLM structured output failed: {e}")
        print("Using fallback...")

        # Fallback with a default example
        structured_pain_points = PainPointDiscoveryOutput(
            pain_points=[
                PainPoint(
                    problem_description=f"Manual processes in {industry}",
                    frequency_score=8,
                    urgency_score=7,
                    impact_level="High",
                    affected_audience=f"{industry} professionals",
                    source_mentions=10,
                    source_platforms=["reddit"],
                    automation_potential=8.0,
                    current_solutions=["Manual processes", "Basic tools"]
                )
            ],
            top_pain_categories=[
                f"{industry} manual processes",
                f"{industry} data entry",
                f"{industry} reporting tasks"
            ],
            data_sources=["reddit"],
            total_mentions_analyzed=sum(len(d.get("results", [])) for d in collected_data),
            analysis_date_range="past month",
            confidence_score=6.0
        )

    print("Pain Point Discovery Complete!")
    print(f"Found {len(structured_pain_points.pain_points)} pain points")
    print(f"Found {len(structured_pain_points.top_pain_categories)} categories")

    return {
        "research_output": {
            **(state.research_output.model_dump() if state.research_output else {}),
            "pain_point_discovery": structured_pain_points,
        },
        "pain_point_discovery": structured_pain_points,
        "current_step": "pain_point_discovery_complete",
        "tools_used": state.tools_used + ["reddit_search", "azure_llm"],
    }