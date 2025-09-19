
# Market Research Node → Web scraping, trend analysis, competitor research
# Pain Point Discovery Node → Reddit/forum scraping, customer complaint analysis
# User Persona Analysis Node → Demographic research, buying behavior analysis


# Reddit/Forum Scraper → Find real user complaints and needs
# Google Trends API → Identify rising search patterns
# ProductHunt API → Analyze successful launches and gaps
# LinkedIn Sales Navigator API → B2B market research
# Twitter/X API → Social listening for pain points

import os 
from dotenv import load_dotenv 
from pydantic import BaseModel
from langchain_openai import AzureChatOpenAI
import json 
from typing import Dict, Any

from graph.state import (
    BusinessIdeaGenerationState, PainPointDiscoveryOutput, Phase1ResearchOutput, 
    MarketResearchOutput, MarketTrend, CompetitorInfo, PainPoint
)
from tools.google_search_trend_tool import get_trend 
from tools.reddit_scrapper_tool import search_only

load_dotenv(override=True)

llm = AzureChatOpenAI(
    azure_endpoint=os.getenv("AZURE_API_BASE"),
    api_key=os.getenv("AZURE_API_KEY"),
    api_version=os.getenv("AZURE_API_VERSION"),
    azure_deployment=os.getenv("LLM_DEPLOYMENT_NAME")     
)

def parse_api_data(trend_data, reddit_insights, industry):
    """
    Parse API data and create structured fallback data if LLM fails
    """
    # Create basic market trends from trend data
    market_trends = []
    if trend_data:
        for i, trend_item in enumerate(trend_data[:3]):  # Limit to top 3
            market_trends.append(MarketTrend(
                trend_name=f"{industry} Trend {i+1}",
                description=f"Rising interest in {trend_item.get('query', 'automation')} based on search data",
                relevance_score=8.0 - i,  # Decreasing relevance
                time_horizon="medium-term",
                key_drivers=["Digital transformation", "Efficiency needs", "Cost reduction"]
            ))
    
    # Create basic pain points from reddit data  
    pain_points = []
    if reddit_insights:
        for i, reddit_item in enumerate(reddit_insights[:5]):  # Limit to top 5
            query = reddit_item.get('query', f'{industry} problems')
            results = str(reddit_item.get('results', ''))
            
            pain_points.append(PainPoint(
                problem_description=f"Common issue found: {query}",
                frequency_score=7 - i,  # Decreasing frequency
                urgency_score=6,
                impact_level="medium" if i < 2 else "low",
                affected_audience=f"{industry} professionals",
                source_mentions=10 - i * 2,
                source_platforms=["reddit"],
                automation_potential=8.0 - i,
                current_solutions=["Manual processes", "Basic tools"]
            ))
    
    return market_trends, pain_points

def market_research_agent(state: BusinessIdeaGenerationState) -> Dict[str, Any]:
    """
    Enhanced market research agent with better fallback handling
    """
    print("🔍 Starting enhanced market research...")
    
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
                print(f"  ⚠️ Google Trends search failed for '{query}': {e}")

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
                print(f"  ⚠️ Reddit search failed for '{query}': {e}")
        
        print(f"📊 Data collection complete:")
        print(f"  - Google Trends queries: {len(trend_data)}")
        print(f"  - Reddit searches: {len(reddit_insights)}")

        # Parse API data for fallback
        fallback_trends, fallback_pain_points = parse_api_data(trend_data, reddit_insights, industry)

        # Try LLM structured analysis first
        raw_research = {
            "industry": industry,
            "google_trends": trend_data,
            "reddit_insights": reddit_insights
        }
        
        market_research_prompt = f"""
        Analyze the market data for {industry} and extract structured insights.
        Focus on automation opportunities, AI integration, and productivity improvements.
        
        Raw Data:
        {json.dumps(raw_research, indent=2)[:2000]}...  # Truncate to avoid token limits
        
        Identify:
        - Market trends with growth potential
        - Key competitors in the space
        - Growth opportunities for AI/automation solutions
        - Market saturation level assessment
        """
        
        try:
            print("🤖 Analyzing data with LLM...")
            structured_market_research = llm.with_structured_output(
                MarketResearchOutput, 
                method="function_calling"
            ).invoke(market_research_prompt)
            print("✅ LLM market research analysis successful")
            
        except Exception as e:
            print(f"⚠️ LLM structured output failed for market research: {e}")
            print("🔄 Using parsed data fallback...")
            
            # Enhanced fallback with parsed data
            structured_market_research = MarketResearchOutput(
                market_trends=fallback_trends,
                competitors=[
                    CompetitorInfo(
                        name=f"{industry} Leader",
                        description=f"Major player in {industry} automation",
                        market_position="leader",
                        strengths=["Established user base", "Feature rich"],
                        weaknesses=["High cost", "Complex setup"]
                    )
                ],
                market_saturation_level="medium",
                growth_opportunities=[
                    f"AI-powered automation in {industry}",
                    f"SMB-focused {industry} tools",
                    f"Integration solutions for {industry}"
                ],
                research_sources=["google_trends", "reddit"],
                confidence_score=6.0  # Lower confidence for fallback
            )

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
            print("🎯 Analyzing pain points with LLM...")
            structured_pain_points = llm.with_structured_output(
                PainPointDiscoveryOutput,
                method="function_calling"
            ).invoke(pain_points_prompt)
            print("✅ LLM pain points analysis successful")
            
        except Exception as e:
            print(f"⚠️ LLM structured output failed for pain points: {e}")
            print("🔄 Using parsed data fallback...")
            
            # Enhanced fallback with parsed data
            structured_pain_points = PainPointDiscoveryOutput(
                pain_points=fallback_pain_points,
                top_pain_categories=[
                    f"{industry} manual processes",
                    f"{industry} data entry",
                    f"{industry} reporting tasks"
                ],
                data_sources=["reddit"],
                total_mentions_analyzed=len(reddit_insights) * 3,  # Estimate
                analysis_date_range="past month",
                confidence_score=6.0  # Lower confidence for fallback
            )

        # Create comprehensive research output
        research_output = Phase1ResearchOutput(
            market_research=structured_market_research,
            pain_point_discovery=structured_pain_points,
            research_summary=f"""
            Market research completed for {industry} industry:
            - Found {len(structured_market_research.market_trends)} market trends
            - Identified {len(structured_pain_points.pain_points)} pain points
            - Market saturation: {structured_market_research.market_saturation_level}
            - Key opportunities in automation and AI integration
            """,
            research_quality_score=max(
                structured_market_research.confidence_score, 
                structured_pain_points.confidence_score
            ),
            next_steps_recommendation="Proceed to user persona analysis and business idea generation."
        )

        print("✅ Market Research Complete!")
        print(f"📈 Found {len(structured_market_research.market_trends)} market trends")
        print(f"🏢 Found {len(structured_market_research.competitors)} competitors")
        print(f"🎯 Found {len(structured_pain_points.pain_points)} pain points")
        print(f"📊 Overall quality score: {research_output.research_quality_score}/10")
        
        # Return updated state as dict (LangGraph requirement)
        return {
            "research_output": research_output,
            "current_step": "market_research_complete",
            "tools_used": state.tools_used + ["google_trends", "reddit_search", "azure_llm"],
            "phase1_complete": True
        }
    
    except Exception as e: 
        print(f"❌ Market research agent failed: {e}")
        import traceback
        traceback.print_exc()
        
        return {
            "current_step": "market_research_failed",
            "errors": state.errors + [f"Market research failed: {str(e)}"]
        }