# so the main idea is to be bale ot crete an multi agenti sysem with stight worklfow thta is abel rally to coem with with busisees idea saas b22 that has iffen rpaeme such take an input  detiel pae as input and come cup with b2b busisse idea or b2c also that powetr the multu agentstsem you ar ebale to su custoom tool and api wher ellm lack and hsi weakness and cna do wbe sreasrh or what evr can do, to come with clear and vlaidtae idea htta can need ot be jsu twrite nee dot be speicf agent, to come busosnes ide athat can have an mvp  in tow weeks, isnest fo beign gnerel m no to fund reall ysepcifi niche under nche where user nbeedto saas bmean wher etheuse rby paiyjgn a sublsito cito can sue yoru serive motnth subsiton, thsi ide nee dot really brinc value


I odo not wan tot genere any toehr is ok for nwo the ony cod eI iwna ot to help budl is bertte state the state I woile liek riht is ot have better stae what mena isbet og nere user inpi mpre specif and laso th ebdge randg is nto need becsie si lowo byge any way what I mena that need ot come with ide a where of multi agenti thta that ai agent or ai in genrte wher eit can ad dvaleu fo reperitve task urktu agent sye mI will focus ona l the part an dbuidl th reapiu of the an dforn etst adn if it work th e frone nd is do by freelance thes eis the main ida mreo cofuc so ngente look fo ai idea spo mayeb th emakre trned canb do genreal anbd the wul be filter by othe rnode in hte sbet by suer inotu ened ot be specif
I want to help now jsut t o giv eide of worklfo with node and custom tools ex: an exmaple og wihci tway I owielleikt ot byudil the project usint htsi as frmawornas th emain of cisur jsu tidffienr exanoe to give ide ahwo sturte my workflow righ tI wan ot to give an ide of proetint workflto to do base o th idescir above 

"""# Updated graph/workflow.py
from langgraph.graph import StateGraph, END
from typing import Dict, Any
from graph.state import YouTubeResearchState
from agents.search_agent import search_video_node
from agents.extract_transcript_agent import extract_transcripts_node
from agents.summary_agent import create_summary_node
from agents.store_agents import storage_node
from agents.final_report_agent import final_report_node

def create_workflow():
    """Create the workflow for YouTube multi-agent system."""
    
    workflow = StateGraph(YouTubeResearchState)
    
    # Add nodes/agents
    workflow.add_node("search", search_video_node)
    workflow.add_node("extract_transcript", extract_transcripts_node)
    workflow.add_node("summarize", create_summary_node)
    workflow.add_node("store", storage_node)
    workflow.add_node("final_report", final_report_node)
    
    # Set entry point
    workflow.set_entry_point("search")
    
    # Add workflow edges
    workflow.add_edge("search", "extract_transcript")
    workflow.add_edge("extract_transcript", "summarize")
    workflow.add_edge("summarize", "store")
    workflow.add_edge("store", "final_report")
    workflow.add_edge("final_report", END)
    
    return workflow.compile()""""from graph.workflow import create_workflow
from graph.state import YouTubeResearchState

def run_youtube_research():
    """
    Main function to run the YouTube research workflow.
    """
    app = create_workflow()
    
    
    initial_state = {
        "query": "the original growth hacker",
        "channels": ["Lenny Podcast"],
        "max_results_per_query": 10,
        "language": "en",
        "topic_focus": "",
        "video_urls": [],
        "video_metadata": [],
        "transcripts": {},
        "summaries": {},
        "storage_results": {},
        "final_report": "",
        "current_step": "starting",
        "errors": []
    }
    
    print("Starting YouTube Research Workflow...")
    
    try:
        final_state = app.invoke(initial_state)
        print("Workflow completed!")
        print(f"Video URLs found: {final_state.get('video_urls', [])}")
        print(f"Current step: {final_state.get('current_step', 'unknown')}")
        return final_state
    except Exception as e:
        print(f"Workflow failed: {str(e)}")
        return None

if __name__ == "__main__":
    result = run_youtube_research()


    ""2
"""
Async YouTube Search Tool - Clean version
Search videos by topics, channels, or topics within channels using YouTube Data API.
"""

import os
import json
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from langchain.tools import StructuredTool
import aiohttp
import asyncio
from dotenv import load_dotenv

load_dotenv(override=True)

class YouTubeSearchInput(BaseModel):
    query: str = Field(description="Main search query/topic")
    topics: Optional[List[str]] = Field(None, description="Additional specific topics")
    channels: Optional[List[str]] = Field(None, description="Channel names to search in")
    max_results_per_query: int = Field(default=5, description="Max videos per query")


async def youtube_search_function_async(
    query: str,
    topics: Optional[List[str]] = None,
    channels: Optional[List[str]] = None,
    max_results_per_query: int = 2,
) -> str:
    """
    Search YouTube for videos by topics, channels, or topics within channels.

    Parameters:
        query (str): Main search query/topic.
        topics (list[str], optional): Additional topics to search for.
        channels (list[str], optional): Channels to search in.
        max_results_per_query (int): Maximum videos to retrieve per query (default 2).

    Returns:
        str: JSON string containing video metadata, URLs, and search summary.
    """
    try:
        api_key = os.getenv("YOUTUBE_API_KEY")
        if not api_key:
            return json.dumps({"error": "YOUTUBE_API_KEY not set", "videos": []})

        all_videos = []
        base_url = "https://www.googleapis.com/youtube/v3"

        async def fetch_json(session, url, params):
            async with session.get(url, ...