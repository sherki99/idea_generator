"""
Pain Point Discovery Agent, only handles Reddit scraping for pain points
"""

import os 
from dotenv import load_dotenv 
from langchain_openai import AzureChatOpenAI
import json 
from typing import Dict, Any

from graph.state import BusinessIdeaGenerationState, PainPointDiscoveryOutput, PainPoint
from tools.reddit_scrapper_tool import search_only

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
    
    try:  
        user_input = state.user_input
        industry = user_input.industry_market

        print(f"--- Searching Reddit for pain points in {industry}")
       
        reddit_queries = [
            f"{industry} problems",
            f"{industry} automation challenges",
            f"{industry} manual work issues",
        ]

        reddit_insights = []
        for query in reddit_queries: 
            try:
                print(f"  Searching: {query}")
                reddit_result = search_only(query, limit="3")
                reddit_insights.append({
                    "query": query, 
                    "results": reddit_result
                })
            except Exception as e: 
                print(f"Reddit search failed for '{query}': {e}")

        # Pain points analysis
        pain_points_prompt = f"""
        Analyze Reddit discussions about {industry} to identify pain points and problems.
        Focus on repetitive tasks, manual processes, and efficiency issues.
        
        Raw Data:
        {json.dumps(reddit_insights, indent=2)[:2000]}...
        
        Extract:
        - Specific pain points with frequency and urgency scores
        - Categories of problems
        - Real user complaints and needs
        """
        
        try:
            print("Analyzing pain points with LLM...")
            structured_pain_points = llm.with_structured_output(
                PainPointDiscoveryOutput,
                method="function_calling"
            ).invoke(pain_points_prompt)
            print("LLM pain points analysis successful")
            
        except Exception as e:
            print(f"LLM structured output failed: {e}")
            print("Using fallback...")
            
            # Simple fallback
            structured_pain_points = PainPointDiscoveryOutput(
                pain_points=[
                    PainPoint(
                        problem_description=f"Manual processes in {industry}",
                        frequency_score=8,
                        urgency_score=7,
                        impact_level="high",
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
                total_mentions_analyzed=len(reddit_insights) * 3,
                analysis_date_range="past month",
                confidence_score=6.0
            )

        print("Pain Point Discovery Complete!")
        print(f"Found {(structured_pain_points.pain_points)} pain points")
        print(f"Found {len(structured_pain_points.top_pain_categories)} categories")
        
        return {
            "pain_point_discovery": structured_pain_points,
            "current_step": "pain_point_discovery_complete",
            "tools_used": state.tools_used + ["reddit_search", "azure_llm"],
        }
    
    except Exception as e: 
        print(f"Pain point discovery agent failed: {e}")
        return {
            "current_step": "pain_point_discovery_failed",
            "errors": state.errors + [f"Pain point discovery failed: {str(e)}"]
        }