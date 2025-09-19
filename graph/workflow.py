from graph.state import BusinessIdeaGenerationState
from langgraph.graph  import StateGraph, END
from typing import Dict 

from agents.market_research_agent import market_research_agent
from agents.pain_point_discovery_agent import pain_point_discovery_agent
from agents.user_persona_analysis_agent import user_persona_analysis_agent

# # Phase 2 Agents
# from agents.niche_opportunity_scanner_agent import niche_opportunity_scanner_node
# from agents.business_model_generator_agent import business_model_generator_node
# from agents.problem_solution_matcher_agent import problem_solution_matcher_node

def create_business_idea_workflow():
    """Create the workflow for Business Idea Generation multi-agent system - Phase 1 & 2."""
    
    workflow = StateGraph(BusinessIdeaGenerationState)
    
    # Phase 1: Research & Analysis Nodes
    workflow.add_node("market_research", market_research_agent)
    workflow.add_node("pain_point_discovery", pain_point_discovery_agent)
    workflow.add_node("user_persona_analysis", user_persona_analysis_agent)
    
    # # Phase 2: Idea Generation Nodes
    # workflow.add_node("niche_opportunity_scanner", niche_opportunity_scanner_node)
    # workflow.add_node("business_model_generator", business_model_generator_node)
    # workflow.add_node("problem_solution_matcher", problem_solution_matcher_node)
    
    # Set entry point
    workflow.set_entry_point("market_research")
    
    # Phase 1 workflow edges
    workflow.add_edge("market_research", "pain_point_discovery" )  # "pain_point_discovery"
    workflow.add_edge("pain_point_discovery", "user_persona_analysis")
    workflow.add_edge("pain_point_discovery", END)
    
    # # Transition from Phase 1 to Phase 2
    #workflow.add_edge("user_persona_analysis", "niche_opportunity_scanner")
    
    # # Phase 2 workflow edges
    # workflow.add_edge("niche_opportunity_scanner", "business_model_generator")
    # workflow.add_edge("business_model_generator", "problem_solution_matcher")
    # workflow.add_edge("problem_solution_matcher", END)
    
    return workflow.compile()
