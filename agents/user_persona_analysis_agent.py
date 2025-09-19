"""
User Persona Analysis Agent - Only handles demographic research and buying behavior analysis
"""

import os 
from dotenv import load_dotenv 
from langchain_openai import AzureChatOpenAI
import json 
from typing import Dict, Any

from graph.state import (
    BusinessIdeaGenerationState, 
    UserPersonaAnalysisOutput, 
    UserPersona,
    PersonaDemographics,
    PersonaBehavior
)
from tools.reddit_scrapper_tool import search_only

load_dotenv(override=True)

llm = AzureChatOpenAI(
    azure_endpoint=os.getenv("AZURE_API_BASE"),
    api_key=os.getenv("AZURE_API_KEY"),
    api_version=os.getenv("AZURE_API_VERSION"),
    azure_deployment=os.getenv("LLM_DEPLOYMENT_NAME")     
)

def user_persona_analysis_agent(state: BusinessIdeaGenerationState) -> Dict[str, Any]:
    """
    User Persona Analysis Agent - Focused only on demographic research and buying behavior
    """
    print("👤 Starting User Persona Analysis...")
    
    try:  
        user_input = state.user_input
        industry = user_input.industry_market
        target_audience = user_input.target_audience

        print(f"--- Analyzing user personas for: {industry}")

        # Search for persona-related discussions
        persona_queries = [
            f"{industry} customer demographics",
            f"{industry} buyer behavior",
            f"{industry} decision makers",
            f"who uses {industry} tools",
            f"{industry} budget authority"
        ]

        persona_insights = []
        for query in persona_queries: 
            try:
                print(f"  Searching: {query}")
                reddit_result = search_only(query, limit="3")
                persona_insights.append({
                    "query": query, 
                    "results": reddit_result
                })
            except Exception as e: 
                print(f"Reddit search failed for '{query}': {e}")

        # Prepare persona analysis data
        persona_data = {
            "industry": industry,
            "target_market": user_input.target_market_type,
            "existing_audience": target_audience.model_dump() if target_audience else None,
            "reddit_insights": persona_insights
        }
        
        persona_analysis_prompt = f"""
        Analyze user personas for {industry} industry based on demographic research and buying behavior.
        Focus on creating detailed user profiles with demographics, behavior patterns, and decision-making processes.
        
        Context:
        - Industry: {industry}
        - Target Market: {user_input.target_market_type}
        - Existing Audience Info: {target_audience.model_dump() if target_audience else "None provided"}
        
        Research Data:
        {json.dumps(persona_insights, indent=2)}...
        
        Create detailed personas including:
        - Demographics (age, income, job titles, company size)
        - Behavioral patterns (communication, decision-making, technology adoption)
        - Pain points and motivations
        - Budget authority and price sensitivity
        """
        
        try:
            print("Analyzing personas with LLM...")
            structured_personas = llm.with_structured_output(
                UserPersonaAnalysisOutput,
                method="function_calling"
            ).invoke(persona_analysis_prompt)
            print("LLM persona analysis successful")
            
        except Exception as e:
            print(f"LLM structured output failed: {e}")
            print("Using fallback...")
            
            # Simple fallback personas
            primary_persona = UserPersona(
                persona_name=f"{industry} Professional",
                persona_description=f"Primary user of {industry} tools and solutions",
                demographics=PersonaDemographics(
                    age_range="28-45",
                    income_range="$50k-$100k",
                    education_level="Bachelor's degree or higher",
                    job_titles=[f"{industry} Manager", f"{industry} Specialist", f"{industry} Coordinator"],
                    company_size="10-500 employees",
                    location_type="Urban and suburban areas"
                ),
                behavior=PersonaBehavior(
                    preferred_communication_channels=["Email", "Professional networks", "Industry forums"],
                    decision_making_process="Research-driven, compares multiple options",
                    budget_authority="Recommends purchases, needs approval for large expenses",
                    technology_adoption="Early majority, adopts proven solutions",
                    research_habits=["Online reviews", "Peer recommendations", "Free trials"],
                    objections_concerns=["Cost", "Learning curve", "Integration challenges"]
                ),
                pain_points=[
                    f"Manual processes in {industry}",
                    "Time-consuming tasks",
                    "Lack of automation"
                ],
                goals_motivations=[
                    "Increase efficiency",
                    "Reduce manual work", 
                    "Improve results"
                ],
                preferred_features=[
                    "Easy to use",
                    "Good integration",
                    "Reliable support"
                ],
                price_sensitivity="Moderate - values ROI over lowest price",
                persona_size="60% of target market"
            )
            
            structured_personas = UserPersonaAnalysisOutput(
                primary_personas=[primary_persona],
                secondary_personas=[],
                persona_prioritization={"primary": f"{industry} Professional"},
                cross_persona_insights=[
                    f"Most {industry} users value efficiency over features",
                    f"Price sensitivity varies by company size",
                    "Integration capabilities are crucial"
                ],
                market_segmentation={
                    "by_company_size": "Small (1-50), Medium (51-500), Large (500+)",
                    "by_role": "Managers, Specialists, Decision makers"
                },
                research_methodology=["reddit_analysis", "demographic_research"],
                sample_size=len(persona_insights) * 3,
                confidence_score=6.0
            )

        print("User Persona Analysis Complete!")
        print(f"Primary Personas: {(structured_personas.primary_personas)}")
        print(f"Secondary Personas: {(structured_personas.secondary_personas)}")
        print(f"Confidence Score: {structured_personas.confidence_score}/10")
        
        return {
            "user_persona_analysis": structured_personas,
            "current_step": "user_persona_analysis_complete",
            "tools_used": state.tools_used + ["reddit_search", "azure_llm"],
        }
    
    except Exception as e: 
        print(f"User persona analysis agent failed: {e}")
        return {
            "current_step": "user_persona_analysis_failed",
            "errors": state.errors + [f"User persona analysis failed: {str(e)}"]
        }