from typing import List, Dict, Any

def parse_trend_data(trend_data: str, industry: str) -> List[Dict[str, Any]]:
    """Parse Google Trends data into structured format."""
    try:
        # Extract key information from trend data string
        lines = trend_data.split('\n')
        
        trend_info = {
            "industry": industry,
            "trend_direction": "growing" if "%" in trend_data and float(trend_data.split('%')[0].split()[-1]) > 0 else "declining",
            "related_queries": [],
            "average_interest": 0
        }
        
        for line in lines:
            if "Average Value:" in line:
                trend_info["average_interest"] = float(line.split(':')[1].strip())
            elif "Rising Related Queries:" in line:
                queries = line.split(':')[1].strip().split(', ')
                trend_info["related_queries"] = queries[:5]  # Top 5
        
        return [trend_info]
    except Exception as e:
        print(f"Error parsing trend data: {e}")
        return []

def extract_pain_points_from_reddit(reddit_insights: List[Dict], industry: str) -> List[Dict[str, Any]]:
    """Extract pain points from Reddit search results."""
    pain_points = []
    
    for insight in reddit_insights:
        query = insight["query"]
        results = insight["results"]
        
        # Simple pain point extraction (can be improved with NLP)
        if isinstance(results, str):
            pain_points.append({
                "source": "reddit",
                "query": query,
                "description": results[:200] + "..." if len(results) > 200 else results,
                "industry": industry,
                "urgency_score": 5  # Default score, can be improved with sentiment analysis
            })
    
    return pain_points

def calculate_research_quality(trend_data: str, reddit_insights: List[Dict]) -> float:
    """Calculate a quality score for the research data."""
    score = 5.0  # Base score
    
    # Add score based on trend data availability
    if trend_data and len(trend_data) > 100:
        score += 2.0
    
    # Add score based on Reddit insights
    if reddit_insights and len(reddit_insights) > 0:
        score += 2.0
    
    # Add score based on data richness
    if any("Rising Related Queries" in trend_data for _ in [1]):
        score += 1.0
    
    return min(score, 10.0)  # Cap at 10
