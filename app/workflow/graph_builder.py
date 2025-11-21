from langgraph.graph import StateGraph
from app.models import ResumeState
from .nodes import (
    parse_resume_node,
    ats_score_node,
    enhance_resume_node,
    generate_resume_node
)


def build_workflow():
    """Build and compile the LangGraph workflow"""
    
    # Create StateGraph
    workflow = StateGraph(ResumeState)
    
    # Add nodes
    workflow.add_node("parse", parse_resume_node)
    workflow.add_node("ats_score_analysis", ats_score_node)
    workflow.add_node("enhance", enhance_resume_node)
    workflow.add_node("generate", generate_resume_node)
    
    # Add edges (workflow flow)
    workflow.add_edge("parse", "ats_score_analysis")
    workflow.add_edge("ats_score_analysis", "enhance")
    workflow.add_edge("enhance", "generate")
    
    # Set entry and finish points
    workflow.set_entry_point("parse")
    workflow.set_finish_point("generate")
    
    # Compile and return
    graph = workflow.compile()
    return graph
