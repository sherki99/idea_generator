import os
from graph.workflow import create_business_idea_workflow
from graph.state import (
    BusinessIdeaGenerationState, 
    UserInput,
    TargetAudience,
    TargetMarket,
    Phase1ResearchOutput
)
from datetime import datetime
import traceback



def test_separated_workflow():
    """Test the separated workflow"""
    
    # Create test user input
    target_audience = TargetAudience(
        demographic="B2B travel and tour operators focusing on transportation services in Italy",
        tech_literacy="Intermediate – uses booking software and CRM tools",
        pain_points=["Managing online bookings", "Reaching B2B partners", "SEO content for visibility"],
        age_range="28-45",
        income_level="$50k-100k",
        buying_behavior="Researches SaaS platforms, compares features, and relies on reviews before purchase"
    )

    user_input = UserInput(
        country_region="Italia",
        industry_market="transportation",
        target_market_type=TargetMarket.B2B,
        target_audience=target_audience,
    )

    # Create initial state
    initial_state = BusinessIdeaGenerationState(
        user_input=user_input,
        current_step="initialization"
    )

    # Create and run workflow
    print("🚀 Starting Separated Workflow...")
    workflow = create_business_idea_workflow()

    try:
        final_state = workflow.invoke(initial_state)

        # Create combined research output for backward compatibility
        if (final_state.get('market_research') and 
            final_state.get('pain_point_discovery') and 
            final_state.get('user_persona_analysis')):
            
            research_output = Phase1ResearchOutput(
                market_research=final_state['market_research'],
                pain_point_discovery=final_state['pain_point_discovery'],
                user_persona_analysis=final_state['user_persona_analysis'],
                research_summary=f"""
                Complete Phase 1 research for {user_input.industry_market}:
                - Market Trends: {(final_state['market_research'].market_trends)}
                - Competitors: {(final_state['market_research'].competitors)}
                - Pain Points: {(final_state['pain_point_discovery'].pain_points)}
                - User Personas: {(final_state['user_persona_analysis'].primary_personas)}
                """,
                research_quality_score=max(
                    final_state['market_research'].confidence_score,
                    final_state['pain_point_discovery'].confidence_score,
                    final_state['user_persona_analysis'].confidence_score
                ),
                next_steps_recommendation="Phase 1 complete. Ready for business idea generation."
            )
            final_state['research_output'] = research_output

        # Generate simple report
        report_lines = []
        report_lines.append("# 📊 Separated Workflow Report\n")
        report_lines.append(f"**Run Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        report_lines.append("---\n")
        
        if 'market_research' in final_state:
            market = final_state['market_research']
            report_lines.append("## 📈 Market Research")
            report_lines.append(f"- Market Trends: **{(market.market_trends)}**")
            report_lines.append(f"- Competitors: **{(market.competitors)}**")
            report_lines.append(f"- Confidence: **{market.confidence_score}/10**\n")

        if 'pain_point_discovery' in final_state:
            pain = final_state['pain_point_discovery']
            report_lines.append("## 🎯 Pain Points")
            report_lines.append(f"- Pain Points: **{(pain.pain_points)}**")
            report_lines.append(f"- Categories: **{(pain.top_pain_categories)}**")
            report_lines.append(f"- Confidence: **{pain.confidence_score}/10**\n")

        if final_state.get('errors'):
            report_lines.append("## Errors")
            for error in final_state['errors']:
                report_lines.append(f"- {error}\n")


        with open("", "w", encoding="utf-8") as f:
            f.write("\n".join(report_lines))

        print("Separated Workflow completed successfully!")
        print("📄Report saved to: separated_workflow_report.md")
        return final_state

    except Exception as e:
        print(f"Workflow failed: {str(e)}")
        traceback.print_exc()
        return None

if __name__ == "__main__":
    result = test_separated_workflow()
    if result:
        print("\Test completed!")
    else:
        print("\nTest failed!")