import json
from typing import Dict, Any
import os 
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from graph.state import BusinessIdeaGenerationState, BusinessModelGeneratorOutput, BusinessIdea

load_dotenv(override=True)

llm = AzureChatOpenAI(
    azure_endpoint=os.getenv("AZURE_API_BASE"),
    api_key=os.getenv("AZURE_API_KEY"),
    api_version=os.getenv("AZURE_API_VERSION"),
    azure_deployment=os.getenv("LLM_DEPLOYMENT_NAME")     
)

def business_model_generator_agent(state: BusinessIdeaGenerationState) -> Dict[str, Any]:
    """
    Generate evidence-backed, workflow-driven business ideas using multi-agent LLM workflows.
    Integrates pain points and validated niche opportunities.
    """

    print("💡 Generating Business Ideas from validated niches and pain points...")

    try:
        # --- Gather research outputs ---
        industry = state.user_input.industry_market
        country = state.user_input.country_region
        personas = state.research_output.user_persona_analysis.primary_personas if state.research_output.user_persona_analysis else []
        pain_points = state.research_output.pain_point_discovery.pain_points if state.research_output.pain_point_discovery else []
        niches = state.research_output.niche_opportunity.niches if state.research_output.niche_opportunity else []
        market_trends = state.research_output.market_research.market_trends if state.research_output.market_research else []

        # --- LLM Prompt ---
        analysis_prompt = f"""
        You are a **Business Model Generation Agent** specialized in creating **micro-SaaS solutions**
        leveraging **multi-agent workflows** (LangChain + LangGraph).

        Context:
        - Validated niches: {json.dumps([n.model_dump() for n in niches], indent=2)}
        - Structured pain points: {json.dumps([p.model_dump() for p in pain_points], indent=2)}
        - Personas: {json.dumps([p.model_dump() for p in personas], indent=2)}
        - Market trends: {json.dumps([t.model_dump() for t in market_trends], indent=2)}

        ⚠️ IMPORTANT:
        - Only generate ideas if supported by research evidence (pain points, niches, personas, trends).
        - Each idea must explain:
            1. Problem Statement (pain point or niche)
            2. Evidence source(s)
            3. Why multi-agent workflows are required
            4. Workflow design (LangChain/LangGraph)
            5. Unique value proposition
            6. Target persona
            7. Monetization strategy
            8. Feasibility score (0-10)

        Recommend **5-10 top validated ideas** with priority ranking.
        Reject all generic, unsupported, or chatbot-only ideas.
        """

        structured_output = llm.with_structured_output(
            BusinessModelGeneratorOutput,
            method="function_calling"
        ).invoke(analysis_prompt)

        print("✅ Business ideas successfully generated")

        return {
            "research_output": {
                **(state.research_output.model_dump() if state.research_output else {}), 
                "business_model_generator": structured_output
            },
            "current_step": "business_model_generator_complete",
            "tools_used": state.tools_used + ["azure_llm"]
        }

    except Exception as e:
        print(f"❌ Business Model Generator failed: {e}")

        fallback_idea = BusinessIdea(
            idea_name="Agent-powered Compliance Monitor",
            niche="B2B Transportation SaaS",
            description="Multi-agent system monitors regulations and contracts automatically.",
            workflow_design="Agents: monitor feeds, parse contracts, alert operators with actionable summaries.",
            unique_value_prop="Automates compliance in highly regulated industries.",
            monetization_strategy="Enterprise SaaS subscriptions",
            target_persona="Operations managers in transportation",
            feasibility_score=7.5,
            supporting_evidence=["trend: compliance automation", "pain_point: regulatory overhead"]
        )

        structured_output = BusinessModelGeneratorOutput(
            ideas=[fallback_idea],
            recommended_idea=fallback_idea.idea_name,
            confidence_score=6.5
        )

        return {
            "business_model_generator": structured_output,
            "current_step": "business_model_generator_fallback",
            "errors": state.errors + [f"Business model generator failed: {str(e)}"]
        }
