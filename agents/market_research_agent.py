"""
Market Research Agent - Only handles market trends and competitors
"""

import os 
from dotenv import load_dotenv 
from langchain_openai import AzureChatOpenAI
import json 
from typing import Dict, Any

from graph.state import BusinessIdeaGenerationState, MarketResearchOutput, MarketTrend, CompetitorInfo
from tools.google_search_trend_tool import get_trend 

load_dotenv(override=True)

llm = AzureChatOpenAI(
    azure_endpoint=os.getenv("AZURE_API_BASE"),
    api_key=os.getenv("AZURE_API_KEY"),
    api_version=os.getenv("AZURE_API_VERSION"),
    azure_deployment=os.getenv("LLM_DEPLOYMENT_NAME")     
)

def market_research_agent(state: BusinessIdeaGenerationState) -> Dict[str, Any]:
    """
    Market Research Agent - Focused only on trends and competitors
    """
    print("Starting Market Research...")
    
    try:  
        user_input = state.user_input
        industry = user_input.industry_market

        print(f"--- Analyzing Google trends for: {industry}")

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
                trend_data.append({
                    "query": query,
                    "results": data
                })
            except Exception as e:
                print(f" Google Trends search failed for '{query}': {e}")

        # Prepare market research data
        market_research_data = {
            "industry": industry,
            "google_trends": trend_data
        }
        
        market_research_prompt = f"""
        Analyze the market data for {industry} and extract structured insights.
        Focus on automation opportunities, AI integration, and productivity improvements.
        
        Raw Data:
        {json.dumps(market_research_data, indent=2)[:2000]}...
        
        Identify:
        - Market trends with growth potential
        - Key competitors in the space
        - Growth opportunities for AI/automation solutions
        - Market saturation level assessment
        - I want yuo always use the data the get from the raw data and get most of it, do not never invent or add somethign that is not true not from the raw data.
        """
        
        try:
            print("Analyzing market data with LLM...")
            structured_market_research = llm.with_structured_output(
                MarketResearchOutput, 
                method="function_calling"
            ).invoke(market_research_prompt)
            print("LLM market research analysis successful")
            
        except Exception as e:
            print(f"LLM structured output failed: {e}")
            print("Using fallback...")
            
            # # Simple fallback
            # structured_market_research = MarketResearchOutput(
            #     market_trends=[
            #         MarketTrend(
            #             trend_name=f"{industry} Automation",
            #             description=f"Growing automation needs in {industry}",
            #             relevance_score=8.0,
            #             time_horizon="medium-term",
            #             key_drivers=["Digital transformation", "Efficiency needs"]
            #         )
            #     ],
            #     competitors=[
            #         CompetitorInfo(
            #             name=f"{industry} Leader",
            #             description=f"Major player in {industry} automation",
            #             market_position="leader",
            #             strengths=["Established user base", "Feature rich"],
            #             weaknesses=["High cost", "Complex setup"]
            #         )
            #     ],
            #     market_saturation_level="medium",
            #     growth_opportunities=[
            #         f"AI-powered automation in {industry}",
            #         f"SMB-focused {industry} tools"
            #     ],
            #     research_sources=["google_trends"],
            #     confidence_score=6.0
            # )

        print("Market Research Complete!")
        print(f"Found {(structured_market_research.market_trends)} market trends")
        print(f"Found {(structured_market_research.competitors)} competitors")
        
        return {
            "market_research": structured_market_research,
            "current_step": "market_research_complete",
            "tools_used": state.tools_used + ["google_trends", "azure_llm"],
        }
    
    except Exception as e: 
        print(f"Market research agent failed: {e}")
        return {
            "current_step": "market_research_failed",
            "errors": state.errors + [f"Market research failed: {str(e)}"]
        }