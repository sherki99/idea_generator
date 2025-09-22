"""
Market Research Agent - Handles market trends, competitors, and product launches
"""
import os
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
import json
from typing import Dict, Any, List

from graph.state import BusinessIdeaGenerationState, MarketResearchOutput, MarketTrend, CompetitorInfo
from tools.google_search_trend_tool import get_trend
from tools.product_hunt_tool import fetch_producthunt_posts  


load_dotenv(override=True)

llm = AzureChatOpenAI(
    azure_endpoint=os.getenv("AZURE_API_BASE"),
    api_key=os.getenv("AZURE_API_KEY"),
    api_version=os.getenv("AZURE_API_VERSION"),
    azure_deployment=os.getenv("LLM_DEPLOYMENT_NAME")
)


def market_research_agent(state: BusinessIdeaGenerationState) -> Dict[str, Any]:
    """
    Market Research Agent - Focused on trends, competitors, and new launches
    """
    print("Starting Market Research...")
    
    try:
        user_input = state.user_input
        industry = user_input.industry_market

        # Google Trends
        print(f"--- Analyzing Google Trends for: {industry}")
        trend_queries = [
            f"{industry} automation AI",
            f"{industry} machine learning",
            f"{industry} software tools",
            f"{industry} productivity",
            f"{industry} workflow automation",
        ]
        trend_data = []
        for query in trend_queries:
            try:
                print(f"  Searching: {query}")
                data = get_trend(query)
                trend_data.append({"query": query, "results": data})
            except Exception as e:
                print(f" Google Trends search failed for '{query}': {e}")

        #  ProductHunt
        print(f"--- Fetching ProductHunt launches for: {industry}")
        try:
            producthunt_data = fetch_producthunt_posts(category=industry, limit=10)
        except Exception as e:
            producthunt_data = []
            print(f" ProductHunt fetch failed: {e}")

        #  Prepare market research prompt
        market_research_data = {
            "industry": industry,
            "google_trends": trend_data,
            "producthunt_launches": producthunt_data,
        }

        market_research_prompt = f"""
        Analyze the market data for {industry} and extract structured insights.
        Focus on automation opportunities, AI integration, productivity improvements, 
        and new product launches.

        Raw Data:
        {json.dumps(market_research_data, indent=2)}...

        Identify:
        - Market trends with growth potential
        - Key competitors in the space
        - Growth opportunities for AI/automation solutions
        - Market saturation level assessment
        - Insights from recent ProductHunt launches
        - Always base your analysis on the raw data; do not invent information.
        """

        # 4️⃣ LLM structured output
        print("Analyzing market data with LLM...")
        structured_market_research = llm.with_structured_output(
            MarketResearchOutput,
            method="function_calling"
        ).invoke(market_research_prompt)
        print("LLM market research analysis successful")

        print("Market Research Complete!")
        print(f"Found {len(structured_market_research.market_trends)} market trends")
        print(f"Found {len(structured_market_research.competitors)} competitors")
        print(f"Found {len(producthunt_data)} recent ProductHunt launches")

        return {
            "research_output": {
                **(state.research_output.model_dump() if state.research_output else {}),
                "market_research": structured_market_research,
            },
            "current_step": "market_research_complete",
            "tools_used": state.tools_used + ["google_trends", "producthunt", "azure_llm"],
        }

    except Exception as e:
        print(f"Market research agent failed: {e}")
        return {
            "current_step": "market_research_failed",
            "errors": state.errors + [f"Market research failed: {str(e)}"]
        }
