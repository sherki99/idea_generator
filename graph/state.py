# models/base_models.py - Fixed Pydantic Base Models
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union
from enum import Enum
from datetime import datetime

# Enums for structured choices
class TargetMarket(str, Enum):
    B2B = "B2B"
    B2C = "B2C"
    B2B2C = "B2B2C"

class Industry(str, Enum):
    HEALTHCARE = "healthcare"
    TECHNOLOGY = "technology"
    FINANCE = "finance"
    EDUCATION = "education"
    RETAIL = "retail"
    REAL_ESTATE = "real_estate"
    HOSPITALITY = "hospitality"
    TRANSPORTATION = "transportation"
    MANUFACTURING = "manufacturing"
    AGRICULTURE = "agriculture"
    ENERGY = "energy"
    ENTERTAINMENT = "entertainment"
    MARKETING = "marketing"
    LEGAL = "legal"
    HUMAN_RESOURCES = "human_resources"  

# Phase 0: User Input Models
class TargetAudience(BaseModel):
    """Target audience specification."""
    demographic: str = Field(description="Primary demographic")
    age_range: Optional[str] = Field(None, description="Age range if relevant")
    income_level: Optional[str] = Field(None, description="Income level")
    tech_literacy: str = Field(description="Technology comfort level")
    pain_points: List[str] = Field(default_factory=list, description="Known pain points")
    buying_behavior: Optional[str] = Field(None, description="Purchasing decisions")

class UserInput(BaseModel):
    """Complete user input specification."""
    country_region: str = Field(description="Target country/region")
    industry_market: str = Field(description="Industry focus")
    target_market_type: TargetMarket = Field(description="Business model type")
    target_audience: Optional[TargetAudience] = Field(None, description="Target audience details")
    created_at: datetime = Field(default_factory=datetime.now)

# Market Research Models 
class CompetitorInfo(BaseModel):
    """Individual competitor information."""
    name: str = Field(description="Competitor name")
    description: str = Field(description="What they do")
    pricing: Optional[str] = Field(None, description="Pricing model")
    market_position: str = Field(description="Market position")
    strengths: List[str] = Field(default_factory=list, description="Key strengths")
    weaknesses: List[str] = Field(default_factory=list, description="Weaknesses/gaps")
    funding_stage: Optional[str] = Field(None, description="Funding stage")
    url: Optional[str] = Field(None, description="Website URL")

class MarketTrend(BaseModel):
    """Individual market trend information."""
    trend_name: str = Field(description="Name of the trend")
    description: str = Field(description="Detailed description")
    growth_rate: Optional[float] = Field(None, description="Growth rate if available")
    market_size: Optional[str] = Field(None, description="Current market size")
    projected_size: Optional[str] = Field(None, description="Projected market size")
    key_drivers: List[str] = Field(default_factory=list, description="Trend drivers")
    time_horizon: str = Field(description="Expected duration")
    relevance_score: float = Field(ge=0, le=10, description="Relevance score (0-10)")

class MarketResearchOutput(BaseModel):
    """Output from Market Research Node."""
    market_trends: List[MarketTrend] = Field(default_factory=list, description="Market trends")
    competitors: List[CompetitorInfo] = Field(default_factory=list, description="Competitors")
    market_saturation_level: str = Field(description="Market saturation level")
    growth_opportunities: List[str] = Field(default_factory=list, description="Growth opportunities")
    market_size_estimate: Optional[str] = Field(None, description="Market size estimate")
    seasonal_patterns: Optional[str] = Field(None, description="Seasonal patterns description")
    geographic_insights: Optional[str] = Field(None, description="Geographic insights description")
    research_sources: List[str] = Field(default_factory=list, description="Data sources")
    confidence_score: float = Field(ge=0, le=10, description="Research quality confidence")

# Pain Point Discovery Models
class PainPoint(BaseModel):
    """Individual pain point discovered."""
    problem_description: str = Field(description="Problem description")
    frequency_score: int = Field(ge=1, le=10, description="Problem frequency (1-10)")
    urgency_score: int = Field(ge=1, le=10, description="Problem urgency (1-10)")
    impact_level: str = Field(description="Impact level")
    affected_audience: str = Field(description="Who faces this problem")
    current_solutions: List[str] = Field(default_factory=list, description="Existing solutions")
    source_mentions: int = Field(description="Number of mentions found")
    source_platforms: List[str] = Field(default_factory=list, description="Discovery platforms")
    example_quotes: List[str] = Field(default_factory=list, description="User quotes")
    automation_potential: float = Field(ge=0, le=10, description="Automation potential")

class PainPointDiscoveryOutput(BaseModel):
    """Output from Pain Point Discovery Node."""
    pain_points: List[PainPoint] = Field(default_factory=list, description="Discovered pain points")
    top_pain_categories: List[str] = Field(default_factory=list, description="Problem categories")
    sentiment_analysis: Optional[str] = Field(None, description="Sentiment analysis summary")
    data_sources: List[str] = Field(default_factory=list, description="Analyzed platforms")
    total_mentions_analyzed: int = Field(description="Total mentions processed")
    analysis_date_range: str = Field(description="Data date range")
    confidence_score: float = Field(ge=0, le=10, description="Analysis confidence")

# User Persona Models 
class PersonaDemographics(BaseModel):
    """Demographic information for a persona."""
    age_range: str = Field(description="Age range")
    gender_distribution: Optional[str] = Field(None, description="Gender distribution")
    income_range: str = Field(description="Income range")
    education_level: str = Field(description="Education level")
    job_titles: List[str] = Field(default_factory=list, description="Job titles")
    company_size: Optional[str] = Field(None, description="Company size")
    location_type: str = Field(description="Geographic distribution")

class PersonaBehavior(BaseModel):
    """Behavioral patterns of a persona."""
    preferred_communication_channels: List[str] = Field(default_factory=list, description="Communication channels")
    decision_making_process: str = Field(description="Decision making process")
    budget_authority: str = Field(description="Budget authority")
    technology_adoption: str = Field(description="Technology adoption pattern")
    research_habits: List[str] = Field(default_factory=list, description="Research habits")
    objections_concerns: List[str] = Field(default_factory=list, description="Common objections")

class UserPersona(BaseModel):
    """Complete user persona profile."""
    persona_name: str = Field(description="Persona name")
    persona_description: str = Field(description="Persona summary")
    demographics: PersonaDemographics = Field(description="Demographics")
    behavior: PersonaBehavior = Field(description="Behavioral patterns")
    pain_points: List[str] = Field(default_factory=list, description="Pain points")
    goals_motivations: List[str] = Field(default_factory=list, description="Goals and motivations")
    preferred_features: List[str] = Field(default_factory=list, description="Valued features")
    accessibility_needs: Optional[List[str]] = Field(default_factory=list, description="Accessibility needs")

class UserPersonaAnalysisOutput(BaseModel):
    """Output from User Persona Analysis Node."""
    primary_personas: List[UserPersona] = Field(default_factory=list, description="Main personas")
    secondary_personas: List[UserPersona] = Field(default_factory=list, description="Secondary personas")
    persona_prioritization: Dict[str, str] = Field(default_factory=dict, description="Persona prioritization")
    cross_persona_insights: List[str] = Field(default_factory=list, description="Cross-persona insights")
    market_segmentation: Union[Dict[str, Any], List[Dict[str, Any]]] = Field(
        default_factory=dict, description="Market segmentation"
    )
    research_methodology: List[str] = Field(default_factory=list, description="Research methods")
    sample_size: Optional[int] = Field(None, description="Total sample size")
    confidence_score: float = Field(ge=0, le=10, description="Persona accuracy confidence")



# Phase 2: Niche Opportunity Scanner Models
class NicheOpportunity(BaseModel):
    """Individual niche opportunity identified."""
    niche_name: str = Field(description="Name of the niche opportunity")
    description: str = Field(description="Why this niche exists and what makes it unique")
    target_persona: str = Field(description="Persona most aligned with this niche")
    demand_level: str = Field(description="Demand level: Low, Medium, High")
    trend_score: float = Field(ge=0, le=10, description="Trend score (0-10)")
    competition_level: str = Field(description="Competition intensity: Low, Medium, High")
    pain_points_addressed: List[str] = Field(default_factory=list, description="Pain points this niche addresses")
    supporting_evidence: Optional[List[str]] = Field(default_factory=list, description="Evidence from research data")
    estimated_market_size: Optional[str] = Field(None, description="Estimated market size if available")

class NicheOpportunityScannerOutput(BaseModel):
    """Output from Niche Opportunity Scanner Node."""
    niches: List[NicheOpportunity]= Field(default_factory=list, description="List of niche opportunities") # this any should not be optional
    prioritization: Dict[str, str] = Field(default_factory=dict, description="Recommended prioritization")
    cross_niche_insights: Optional[List[str]] = Field(default_factory=list, description="Insights across niches")
    confidence_score: float = Field(ge=0, le=10, description="Confidence in opportunity assessment")
    research_sources: List[str] = Field(default_factory=list, description="Sources used in discovery")

class BusinessIdea(BaseModel):
    """Detailed business idea scoped to LLM-powered workflows."""
    idea_name: str = Field(description="Name of the business idea")
    niche: str = Field(description="Niche this idea addresses")
    description: str = Field(description="Description of the SaaS idea and what it solves")
    workflow_design: str = Field(description="How LangChain + LangGraph agents can solve this problem")
    unique_value_prop: str = Field(description="Why this is uniquely valuable compared to alternatives")
    monetization_strategy: str = Field(description="How the product can be monetized")
    target_persona: str = Field(description="Primary user or customer persona")
    feasibility_score: float = Field(ge=0, le=10, description="How feasible this is with LLMs + agents")
    supporting_evidence: List[str] = Field(default_factory=list, description="Supporting signals from niche research")

class BusinessModelGeneratorOutput(BaseModel):
    """Output of business model generator agent."""
    ideas: List[BusinessIdea] = Field(default_factory=list, description="Generated business ideas")
    recommended_idea: Optional[str] = Field(None, description="The single best idea to pursue")
    confidence_score: float = Field(ge=0, le=10, description="Confidence in these recommendations")


class Phase1ResearchOutput(BaseModel):
    """Complete output from Phase 1: Research & Analysis."""
    
    market_research: Optional[MarketResearchOutput] = Field(None, description="Market research results")
    pain_point_discovery: Optional[PainPointDiscoveryOutput] = Field(None, description="Pain point analysis")
    user_persona_analysis: Optional[UserPersonaAnalysisOutput] = Field(None, description="Persona research")
    niche_opportunity: Optional[NicheOpportunityScannerOutput] = Field(None, description="Niche opportunities discovered")
    business_model_generator: Optional[BusinessModelGeneratorOutput] = Field(None, description="SaaS ideas with AI multi-agent workflows")
    
    research_summary: Optional[str] = Field(None, description="Research summary")
    key_opportunities: Optional[List[str]] = Field(None, description="Key opportunities")
    research_quality_score: Optional[float] = Field(None, ge=0, le=10, description="Research quality score")
    next_steps_recommendation: Optional[str] = Field(None, description="Next steps")



# State Model for LangGraph
class BusinessIdeaGenerationState(BaseModel):
    """Complete state model for business idea generation workflow."""
    # Phase 0: Input
    user_input: UserInput = Field(description="User specifications")
    
    # Phase 1: Research outputs
    phase1_complete: bool = Field(default=False, description="completion status")
    research_output: Phase1ResearchOutput = Field(None, description="Phase results")
    

    # Workflow management
    current_step: str = Field(default="initialization", description="Current step")
    errors: List[str] = Field(default_factory=list, description="Errors encountered")
    tools_used: List[str] = Field(default_factory=list, description="Tools used")
    processing_start_time: datetime = Field(default_factory=datetime.now)
    step_timestamps: Optional[str] = Field(None, description="Step completion timestamps")
    
    # Configuration
    debug_mode: bool = Field(default=False, description="Debug mode")
    save_intermediate_results: bool = Field(default=True, description="Save intermediate results")
    
    class Config:
        arbitrary_types_allowed = True

