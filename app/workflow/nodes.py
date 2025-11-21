import json
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException
from app.models import ResumeState
from app.utils import save_resume_docx
from .llm_config import llm


# -------- Node: Parse Resume --------
def parse_resume_node(state: ResumeState) -> ResumeState:
    """Parse raw resume text into structured data"""
    
    # Validation
    if not state["raw_text"] or len(state["raw_text"].strip()) < 20:
        raise Exception("Resume text is too short or empty to process")
    
    prompt = PromptTemplate(
        input_variables=["resume_text"],
        template="""
        Parse this resume and extract structured data. Return ONLY valid JSON.
        {resume_text}
        
        Return JSON with this structure:
        {{
            "name": "string",
            "email": "string",
            "phone": "string",
            "linkedin": "string",
            "summary": "string",
            "experience": [
                {{"title": "string", "company": "string", "duration": "string", "description": "string"}}
            ],
            "education": [
                {{"degree": "string", "field": "string", "institution": "string", "year": "string"}}
            ],
            "skills": ["string"],
            "projects": [
                {{"title": "string", "description": "string"}}
            ]
        }}
        """
    )
    
    parser = JsonOutputParser()
    chain = prompt | llm | parser
    
    try:
        parsed_data = chain.invoke({"resume_text": state["raw_text"]})
    except OutputParserException as e:
        raise Exception(f"Failed to parse resume as JSON: {str(e)}")
    
    state["parsed_data"] = parsed_data
    return state


# -------- Node: Calculate ATS Score --------
def ats_score_node(state: ResumeState) -> ResumeState:
    """Calculate ATS score for resume"""
    prompt = PromptTemplate(
        input_variables=["resume_data"],
        template="""
        Analyze this resume data for ATS (Applicant Tracking System) compatibility.
        {resume_data}
        
        Return ONLY valid JSON with:
        {{
            "score": <0-100>,
            "feedback": "string",
            "improvements": ["string list of improvements"],
            "missing_keywords": ["string list of keywords to add"]
        }}
        """
    )
    
    parser = JsonOutputParser()
    chain = prompt | llm | parser
    
    try:
        ats_data = chain.invoke({"resume_data": json.dumps(state["parsed_data"])})
    except OutputParserException as e:
        ats_data = {
            "score": 0,
            "feedback": "Could not calculate ATS score",
            "improvements": [],
            "missing_keywords": []
        }
    
    state["ats_score"] = ats_data
    return state


# -------- Node: Enhance Resume --------
def enhance_resume_node(state: ResumeState) -> ResumeState:
    """Enhance resume with AI improvements"""
    prompt = PromptTemplate(
        input_variables=["resume_data", "ats_feedback"],
        template="""
        Improve this resume to increase ATS score and professional impact.
        Resume: {resume_data}
        ATS Feedback: {ats_feedback}
        
        Return ONLY valid JSON with enhanced resume structure:
        {{
            "name": "string",
            "email": "string",
            "phone": "string",
            "linkedin": "string",
            "summary": "improved professional summary",
            "experience": [
                {{"title": "string", "company": "string", "duration": "string", "description": "enhanced description with action verbs"}}
            ],
            "education": [
                {{"degree": "string", "field": "string", "institution": "string", "year": "string"}}
            ],
            "skills": ["enhanced skill list"],
            "projects": [
                {{"title": "string", "description": "enhanced description"}}
            ]
        }}
        """
    )
    
    parser = JsonOutputParser()
    chain = prompt | llm | parser
    
    try:
        enhanced_data = chain.invoke({
            "resume_data": json.dumps(state["parsed_data"]),
            "ats_feedback": json.dumps(state["ats_score"])
        })
    except OutputParserException as e:
        enhanced_data = state["parsed_data"]
    
    state["enhanced_data"] = enhanced_data
    return state


# -------- Node: Generate Resume --------
def generate_resume_node(state: ResumeState) -> ResumeState:
    """Generate final resume file"""
    
    resume_data = state.get("enhanced_data") or state.get("parsed_data")
    template = state.get("template", "modern")
    
    filepath = save_resume_docx(resume_data, template)
    state["output_file"] = filepath
    return state
