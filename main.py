#from graph.workflow import create_business_idea_workflow
from graph.state import (
    BusinessIdeaGenerationState, 
    UserInput,
    TargetAudience,
    TargetMarket,
)
from datetime import datetime
import traceback

def test_market_research():
    """Test the market research workflow - Fixed version with report saved to Markdown."""
    
    # Create test user input
    target_audience = TargetAudience(
        demographic="Online store owners",
        tech_literacy="intermediate",
        pain_points=["Writing product descriptions", "SEO content"],
        age_range="25-45",
        income_level="$50k-100k",
        buying_behavior="Researches multiple SaaS platforms before buying"
    )
    
    user_input = UserInput(
        country_region="United States",
        industry_market="E-commerce",
        target_market_type=TargetMarket.B2B,
        target_audience=target_audience,
    )
    
    # Create initial state
    initial_state = BusinessIdeaGenerationState(
        user_input=user_input,
        current_step="initialization"
    )
    
    # Create and run workflow
    print("🚀 Starting Business Idea Generation Workflow...")
    from graph.workflow import create_business_idea_workflow
    workflow = create_business_idea_workflow()
    
    try:
        final_state = workflow.invoke(initial_state)

        # Build report content as Markdown
        report_lines = []
        report_lines.append("# 📊 Business Idea Generation Workflow Report\n")
        report_lines.append(f"**Run Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        report_lines.append("---\n")
        report_lines.append(f"### Final Step: `{final_state.get('current_step', 'unknown')}`\n")

        if 'research_output' in final_state:
            research = final_state['research_output']
            report_lines.append("## 📈 Market Research")
            report_lines.append(f"- Market Trends: **{(research.market_research.market_trends)}**")
            report_lines.append(f"- Competitors: **{(research.market_research.competitors)}**")
            report_lines.append(f"- Growth Opportunities: **{(research.market_research.growth_opportunities)}**\n")

            report_lines.append("## 🎯 Pain Points")
            report_lines.append(f"- Pain Points Discovered: **{(research.pain_point_discovery.pain_points)}**")
            report_lines.append(f"- Pain Categories: **{(research.pain_point_discovery.top_pain_categories)}**\n")

            report_lines.append("## 📊 Quality Scores")
            report_lines.append(f"- Overall Research Quality: **{research.research_quality_score}/10**")
            report_lines.append(f"- Market Research Confidence: **{research.market_research.confidence_score}/10**")
            report_lines.append(f"- Pain Point Confidence: **{research.pain_point_discovery.confidence_score}/10**\n")

        if final_state.get('errors'):
            report_lines.append("## ❌ Errors")
            report_lines.append(f"- {final_state['errors']}\n")

        if final_state.get('tools_used'):
            report_lines.append("## 🔧 Tools Used")
            report_lines.append(f"- {final_state['tools_used']}\n")

        # Save report to Markdown file
        report_path = "workflow_report.md"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("\n".join(report_lines))

        print(f"\n✅ Report saved to: {report_path}")

        return final_state
        
    except Exception as e:
        print(f"❌ Workflow failed: {str(e)}")
        traceback.print_exc()
        return None

    

if __name__ == "__main__":
    result = test_market_research()
    
    if result:
        print("saving as md for test")
        print("\n✅ Test completed successfully!")
    else:
        print("\n❌ Test failed!")


