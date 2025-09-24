"""
Niche Opportunity Scanner Agent - Enhanced version
Combines structured pain points, subdomains, and multi-source signals to identify validated micro-SaaS niches.
"""

import os
import json
from pathlib import Path
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
from tools.twitter_search_tool import search_tweets

load_dotenv(override=True)

llm = AzureChatOpenAI(
    azure_endpoint=os.getenv("AZURE_API_BASE"),
    api_key=os.getenv("AZURE_API_KEY"),
    api_version=os.getenv("AZURE_API_VERSION"),
    azure_deployment=os.getenv("LLM_DEPLOYMENT_NAME")
)

def niche_opportunity_scanner_agent(state: BusinessIdeaGenerationState) -> Dict[str, Any]:
    print("🔍 Starting Enhanced Niche Opportunity Scanning...")

    try:
        # --- Gather context ---
        industry = state.user_input.industry_market
        country = state.user_input.country_region
        language = state.user_input.language if hasattr(state.user_input, "language") else "en"

        # Use structured pain points
        pain_points = state.research_output.pain_point_discovery.pain_points if state.research_output.pain_point_discovery else []

        # Subdomains/workflows for targeted search
        subdomains = state.research_output.pain_point_discovery.top_pain_categories if state.research_output.pain_point_discovery else [industry]

        # Personas
        personas = state.research_output.user_persona_analysis.primary_personas if state.research_output.user_persona_analysis else []

        # --- Collect multi-source signals ---
        signals = []

        for sd in subdomains:
            query = f"{sd} problems OR inefficiencies OR pain points"
            try:
                reddit_results = search_only(query, limit=3, language=language)
                signals.append({"source": "reddit", "subdomain": sd, "results": reddit_results})
            except Exception as e:
                signals.append({"source": "reddit", "subdomain": sd, "error": str(e)})
            
            try:
                twitter_results = search_tweets(query, max_results=5, language=language)
                signals.append({"source": "twitter", "subdomain": sd, "results": twitter_results})
            except Exception as e:
                signals.append({"source": "twitter", "subdomain": sd, "error": str(e)})

        # Google Trends
        trend_data = []
        try:
            trend_data.append(rising_trends(industry))
            for p in pain_points[:5]:
                trend_data.append(get_trend(p.problem_description))
        except Exception as e:
            trend_data.append({"error": f"Trend fetch failed: {str(e)}"})

        # --- Prepare LLM prompt ---
        NICHE_SYSTEM_MSG = """
        You are a Niche Opportunity Scanner Agent. Identify emerging or underserved micro-SaaS niches.
        Focus on niches validated by pain points, personas, subdomains, and market signals.
        """

        NICHE_USER_PROMPT = f"""
        Task:
        - Identify niches for micro-SaaS in {industry} ({country}).
        - Input data:
          * Personas: {json.dumps([p.model_dump() for p in personas], indent=2) if personas else "None"}
          * Structured Pain Points: {json.dumps([p.model_dump() for p in pain_points], indent=2) if pain_points else "None"}
          * Subdomains: {json.dumps(subdomains, indent=2)}
          * Market signals: {json.dumps(signals, indent=2)}
          * Trends: {json.dumps(trend_data, indent=2)}
        Instructions:
        - Identify at least 3 underserved niches.
        - For each niche:
          - Name, description, target persona, pain points addressed
          - Why underserved
          - Potential SaaS solution
          - Demand, trend score, competition, confidence
          - Evidence sources
        - Prioritize niches by impact, automation potential, and trend.
        - Output in structured JSON.
        ⚠️ Only generate niches if supported by evidence. Otherwise respond:
        "⚠️ No sufficiently validated opportunities identified."
        """

        messages = [
            {"role": "system", "content": NICHE_SYSTEM_MSG},
            {"role": "user", "content": NICHE_USER_PROMPT}
        ]

        structured_output = llm.with_structured_output(
            NicheOpportunityScannerOutput,
            method="function_calling"
        ).invoke(messages)

        # --- Save JSON output per country/industry/subdomain ---
        save_path = Path(f"niche_opportunities/{country}/{industry}")
        save_path.mkdir(parents=True, exist_ok=True)
        output_file = save_path / "niche_opportunities.json"

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(structured_output.model_dump(), f, indent=2, ensure_ascii=False)

        print("✅ Niche opportunities scanning complete and saved.")

        return {
            "research_output": {
                **(state.research_output.model_dump() if state.research_output else {}),
                "niche_opportunity": structured_output,
            },
            "current_step": "niche_opportunity_scanner_complete",
            "tools_used": state.tools_used + ["reddit_search", "twitter_search", "google_trends", "azure_llm"],
        }

    except Exception as e:
        print(f"Niche Opportunity Scanner failed: {e}")
        return {
            "current_step": "niche_opportunity_scanner_failed",
            "errors": state.errors + [f"Niche opportunity scanner failed: {str(e)}"]
        }
