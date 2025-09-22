"""
Niche Opportunity Scanner Agent
Identifies emerging / underserved niches by combining persona insights, pain points, and market trends.
"""

import os
import json
from dotenv import load_dotenv
from typing import Dict, Any, List

from langchain_openai import AzureChatOpenAI

from graph.state import (
    BusinessIdeaGenerationState,
    NicheOpportunityScannerOutput,
    NicheOpportunity
)
from tools.reddit_scrapper_tool import search_only
from tools.google_search_trend_tool import get_trend, rising_trends
from tools.openalex_market_signals import get_openalex_market_signals

load_dotenv(override=True)

llm = AzureChatOpenAI(
    azure_endpoint=os.getenv("AZURE_API_BASE"),
    api_key=os.getenv("AZURE_API_KEY"),
    api_version=os.getenv("AZURE_API_VERSION"),
    azure_deployment=os.getenv("LLM_DEPLOYMENT_NAME")     
)


def niche_opportunity_scanner_agent(state: BusinessIdeaGenerationState) -> Dict[str, Any]:
    """
    Scan for niche opportunities within the target industry.
    Combines Reddit discussions + Google Trends + persona insights.
    """

    print("🔍 Starting Niche Opportunity Scanning...")

    try:
        industry = state.user_input.industry_market
        personas = state.research_output.user_persona_analysis.primary_personas if state.research_output.user_persona_analysis else []
        pain_points = state.research_output.pain_point_discovery.pain_points if state.research_output.pain_point_discovery else []

        # Step 1: Collect Reddit signals
        reddit_queries = [
            f"{industry} unmet needs",
            f"{industry} alternatives",
            f"{industry} competitors",
            f"best tools for {industry}",
            f"{industry} gaps in market"
        ]
        reddit_results = []
        for q in reddit_queries:
            try:
                result = search_only(q, limit="3")
                reddit_results.append({"query": q, "results": result})
            except Exception as e:
                reddit_results.append({"query": q, "error": str(e)})

        # Step 2: Collect Google Trends signals
        trend_data = []
        try:
            trend_data.append(rising_trends(industry))
            for p in pain_points[:4]:  # limit to top pain points
                trend_data.append(get_trend(p.problem_description))
        except Exception as e:
            trend_data.append({"error": f"Trend fetch failed: {str(e)}"})


        # openalex_data = []
        # try:
            
        #     openalex_data = get_openalex_market_signals(industry, top_n=5)
        # except Exception as e:
        #     openalex_data = {"error": str(e)}



        # Step 3: Analyze with LLM
        analysis_prompt = f"""
        You are a niche opportunity analysis agent.
        Analyze the {industry} market and identify emerging or underserved niches.
        
        Inputs:
        - Personas: {json.dumps([p.model_dump() for p in personas], indent=2) if personas else "None"}
        - Pain Points: {json.dumps([p.model_dump() for p in pain_points], indent=2) if pain_points else "None"}
        - Reddit signals: {json.dumps(reddit_results, indent=2)}
        - Google Trends data: {json.dumps(trend_data, indent=2)}
        - OpenAlex innovation signals: {json.dumps(openalex_data, indent=2)}
        
        Task:
        - Identify at least 3 niche opportunities.
        - For each: describe the opportunity, target persona, why demand exists, and why it’s underserved.
        - Rate demand level (Low/Medium/High), trend score (1-10), competition level (Low/Medium/High).
        - Recommend which niches should be prioritized.
        """

        try:
            structured_output = llm.with_structured_output(
                NicheOpportunityScannerOutput,
                method="function_calling"
            ).invoke(analysis_prompt)

            print("✅ LLM successfully generated niche opportunities")
        except Exception as e:
            print(f"LLM structured output failed: {e}")
            # fallback
            fallback_niche = NicheOpportunity(
                niche_name=f"{industry} Automation Tools",
                description=f"Tools to automate repetitive tasks in {industry}.",
                target_persona="Mid-level professionals",
                demand_level="High",
                trend_score=7.5,
                competition_level="Medium",
                pain_points_addressed=["Efficiency", "Time management"],
            )
            structured_output = NicheOpportunityScannerOutput(
                niches=[fallback_niche],
                prioritization={"top_opportunity": fallback_niche.niche_name},
                confidence_score=6.5,
                research_sources=["reddit_search", "google_trends"]
            )

        return {

            "research_output": {
                **(state.research_output.model_dump() if state.research_output else {}),
                 "niche_opportunity": structured_output,
            },
      
            "current_step": "niche_opportunity_scanner_complete",
            "tools_used": state.tools_used + ["reddit_search", "google_trends", "azure_llm"],
        }

    except Exception as e:
        print(f"❌ Niche Opportunity Scanner failed: {e}")
        return {
            "current_step": "niche_opportunity_scanner_failed",
            "errors": state.errors + [f"Niche opportunity scanner failed: {str(e)}"]
        }
