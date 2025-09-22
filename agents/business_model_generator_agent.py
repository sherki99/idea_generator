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
    Generate concrete business ideas that can only be solved effectively 
    using multi-agent LLM workflows (LangChain + LangGraph).
    """

    print("💡 Generating Business Ideas with LLM-specific workflows...")

    try:

        # questo ristrege tanto di gia la mia ricerca 
      
        industry = state.user_input.industry_market
        personas = state.research_output.user_persona_analysis.primary_personas if state.research_output.user_persona_analysis else []
        pain_points = state.research_output.pain_point_discovery.pain_points if state.research_output.pain_point_discovery else []
        market_trends = state.research_output.market_research.market_trends if state.research_output.market_research else []
        niches = state.research_output.niche_opportunity.niches if state.research_output.niche_opportunity else []


        analysis_prompt = f"""
        You are a **Business Model Generation Agent** specialized in creating **LLM-powered SaaS solutions** that leverage **multi-agent workflows** (LangChain + LangGraph).

        Context from research:
        - Niche opportunities: {json.dumps([n.model_dump() for n in niches], indent=2)}
        - Pain points: {json.dumps([p.model_dump() for p in pain_points], indent=2) if pain_points else "None"}
        - Personas: {json.dumps([p.model_dump() for p in personas], indent=2) if personas else "None"}
        - Market trends: {json.dumps([t.model_dump() for t in market_trends], indent=2) if 'market_trends' in locals() else "None"}

        ⚠️ IMPORTANT RULE:
        - Only generate business ideas if they are clearly supported by **evidence from the research above** (personas, pain points, or trends).
        - If no strong evidence exists, respond with: 
        "⚠️ No sufficiently validated opportunities identified from the current research. Recommend expanding research scope before generating ideas."

        For each validated idea, provide:
        1. **Problem Statement** – A specific, evidence-backed pain point in the niche.
        2. **Evidence** – Quote or summarize the supporting research (persona insight, trend, or pain point).
        3. **Why Agents/Workflows are Required** – Why this solution requires multi-agent systems (not just a chatbot).
        4. **Workflow Design** – Example of LangChain/LangGraph architecture (agents, tools, interactions).
        5. **Unique Value Proposition** – Why this solution is different and valuable.
        6. **Target Persona** – Who pays for this and why.
        7. **Monetization Strategy** – SaaS model, API, enterprise, etc.
        8. **Feasibility Score (0-10)** – Based on today’s LLM/agent ecosystem.

        Finally:
        - Recommend ONE idea as the **best validated opportunity**, with clear justification.
        - Reject all "generic" chatbot-style ideas.
        - Only output grounded, niche, high-value SaaS opportunities.
        """


        structured_output = llm.with_structured_output(
            BusinessModelGeneratorOutput,
            method="function_calling"
        ).invoke(analysis_prompt)

        print("✅ LLM successfully generated business ideas")

        return {

            "research_output" : {
                **(state.research_output.model_dump() if state.research_output else {}), 
               "business_model_generator" : structured_output 
                
            },
            "phase1_complete" : True,
            "current_step": "business_model_generator_complete",
            "tools_used": state.tools_used + ["azure_llm"]
        }

    except Exception as e:
        print(f"❌ Business Model Generator failed: {e}")
        fallback_idea = BusinessIdea(
            idea_name="Agent-powered Compliance Monitor",
            niche="B2B Transportation SaaS",
            description="A system that uses multiple LLM agents to monitor regulations, contracts, and compliance updates across regions.",
            workflow_design="One agent monitors government feeds, another parses contracts, and a third alerts operators with actionable summaries.",
            unique_value_prop="Automates compliance tracking in highly regulated industries where manual monitoring is costly.",
            monetization_strategy="Enterprise SaaS subscriptions.",
            target_persona="Operations managers in transportation companies.",
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
