from graph.state import BusinessIdeaGenerationState
from langgraph.graph  import StateGraph, END
from typing import Dict 

from agents.market_research_agent import market_research_agent
from agents.pain_point_discovery_agent import pain_point_discovery_agent
from agents.user_persona_analysis_agent import user_persona_analysis_agent


# # Phase 2 Agents
from agents.niche_opportunity_scanner_agent import niche_opportunity_scanner_agent
from agents.business_model_generator_agent import business_model_generator_agent
from agents.validate_ideas_agent import business_model_validation_agent


#from agents.business_model_generator_agent import business_model_generator_node
# from agents.problem_solution_matcher_agent import problem_solution_matcher_node

def create_business_idea_workflow():
    """Create the workflow for Business Idea Generation multi-agent system - Phase 1 & 2."""
    
    workflow = StateGraph(BusinessIdeaGenerationState)
    
    # Phase 1: Research & Analysis Nodes
    workflow.add_node("market_research", market_research_agent)
    workflow.add_node("pain_point_discovery", pain_point_discovery_agent)
    workflow.add_node("user_persona_analysis", user_persona_analysis_agent)
    workflow.add_node("business_model_generator_agent", business_model_generator_agent)
    
    # # Phase 2: Idea Generation Nodes
    workflow.add_node("niche_opportunity_scanner", niche_opportunity_scanner_agent)
    workflow.add_node("business_model_generator", business_model_generator_agent)
    # workflow.add_node("problem_solution_matcher", problem_solution_matcher_node)

       
    # Phase 3: Validation Node
    workflow.add_node("business_model_validation", business_model_validation_agent)
    
    # Set entry point
    workflow.set_entry_point("market_research")
    
    # Phase 1 workflow edges
    workflow.add_edge("market_research", "pain_point_discovery" )  # "pain_point_discovery"
    workflow.add_edge("pain_point_discovery", "user_persona_analysis")
   
    
    # # Transition from Phase 1 to Phase 2
    workflow.add_edge("user_persona_analysis", "niche_opportunity_scanner")
    workflow.add_edge("niche_opportunity_scanner", "business_model_generator")
    
    # Phase 3: Validation edges
    workflow.add_edge("business_model_generator", "business_model_validation")
    workflow.add_edge("business_model_validation", END)
    
    return workflow.compile()
