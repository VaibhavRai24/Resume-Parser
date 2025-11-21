from pydantic import BaseModel
from typing import Optional, List
from typing_extensions import TypedDict

class ResumeData(BaseModel):
    """Model for manually entered resume data"""
    name: str
    email: str
    phone: str
    summary: str
    experience: List[dict]
    education: List[dict]
    skills: List[str]
    projects: Optional[List[dict]] = []


class ResumeState(TypedDict):
    """State for LangGraph workflow"""
    raw_text: str
    parsed_data: dict
    ats_score: dict
    enhanced_data: dict
    template: str
    output_file: str
