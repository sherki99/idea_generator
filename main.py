import os
from graph.workflow import create_business_idea_workflow
from graph.state import (
    BusinessIdeaGenerationState, 
    UserInput,
    TargetAudience,
    TargetMarket,
)
from datetime import datetime
import traceback
import json




def save_business_model_output(final_state, output_folder="output"):
    """
    Save only the business_model_generator part of the final_state.
    """
    os.makedirs(output_folder, exist_ok=True)

    try:
        bmg_output = final_state['research_output'].get('business_model_generator')

        if not bmg_output:
            print("❌ No business_model_generator output found in final_state")
            return

        # Convert Pydantic object to dict if needed
        if hasattr(bmg_output, "model_dump"):
            json_data = bmg_output.model_dump(mode="json")
        else:
            json_data = bmg_output

        # Find a new filename in order
        i = 1
        while True:
            file_path = os.path.join(output_folder, f"business_model_output_{i}.json")
            if not os.path.exists(file_path):
                break
            i += 1

        with open(file_path, "w") as f:
            json.dump(json_data, f, indent=2)

    
        print(f"✅ Saved business model output to {file_path}")

    except Exception as e:
        print(f"❌ Failed to save business model output: {str(e)}")
        traceback.print_exc()

def test_separated_workflow():
    """Test the separated workflow including Phase 2"""
    
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

        print(f"📊 Current Step: {final_state['current_step']}")
        print(f"📊 Phase 1 Complete: {final_state.get('phase1_complete', False)}")
        print(f"📊 Business Model Generator Output: {final_state['research_output'].get('business_model_generator')}")

        # Save only business model output
        save_business_model_output(final_state)

        return final_state

    except Exception as e:
        print(f"❌ Workflow failed: {str(e)}")
        traceback.print_exc()
        return None




if __name__ == "__main__":
    result = test_separated_workflow()
    if result:
        print("\n✅ Test completed!")
    else:
        print("\n❌ Test failed!")
