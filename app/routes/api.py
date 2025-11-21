import os
import json
from fastapi import APIRouter, File, UploadFile, FastAPI
from fastapi.responses import FileResponse, JSONResponse
from app.models import ResumeData
from app.utils import extract_text_from_pdf, extract_text_from_docx
from app.workflow import build_workflow
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles


router = FastAPI(title="AI Resume Builder", version="1.0")
router.mount("/static", StaticFiles(directory="static"), name="static")
router.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Build the workflow once
graph = build_workflow()


@router.get("/")
async def root():
    """Serve main HTML page"""
    return FileResponse("static/index.html")


@router.post("/api/upload")
async def upload_resume(file: UploadFile = File(...)):
    """Upload and process resume file"""
    try:
        # Create uploads folder
        os.makedirs("uploads", exist_ok=True)
        filepath = f"uploads/{file.filename}"
        
        # Save file
        with open(filepath, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Extract text based on file type
        if file.filename.endswith(".pdf"):
            raw_text = extract_text_from_pdf(filepath)
        elif file.filename.endswith(".docx"):
            raw_text = extract_text_from_docx(filepath)
        else:
            return JSONResponse({"error": "Unsupported file format"}, status_code=400)
        
        # Create initial state
        initial_state = {
            "raw_text": raw_text,
            "parsed_data": {},
            "ats_score": {},
            "enhanced_data": {},
            "template": "modern",
            "output_file": ""
        }
        
        # Run the workflow
        result = graph.invoke(initial_state)
        
        # Extract filename from full path
        output_filename = os.path.basename(result["output_file"])
        
        return JSONResponse({
            "status": "success",
            "parsed_data": result["parsed_data"],
            "ats_score": result["ats_score"],
            "output_file": output_filename
        })
    
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)


@router.post("/api/process-manual")
async def process_manual_resume(data: ResumeData):
    """Process manually entered resume data"""
    try:
        raw_text = f"""
        Name: {data.name}
        Email: {data.email}
        Phone: {data.phone}
        
        Summary: {data.summary}
        
        Experience: {json.dumps(data.experience)}
        Education: {json.dumps(data.education)}
        Skills: {', '.join(data.skills)}
        Projects: {json.dumps(data.projects)}
        """
        
        initial_state = {
            "raw_text": raw_text,
            "parsed_data": data.dict(),
            "ats_score": {},
            "enhanced_data": {},
            "template": "modern",
            "output_file": ""
        }
        
        result = graph.invoke(initial_state)
        
        output_filename = os.path.basename(result["output_file"])
        
        return JSONResponse({
            "status": "success",
            "parsed_data": result["parsed_data"],
            "ats_score": result["ats_score"],
            "output_file": output_filename
        })
    
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)


@router.post("/api/enhance")
async def enhance_resume(data: dict):
    """Enhance existing resume"""
    try:
        raw_text = json.dumps(data)
        
        initial_state = {
            "raw_text": raw_text,
            "parsed_data": data,
            "ats_score": {},
            "enhanced_data": {},
            "template": "modern",
            "output_file": ""
        }
        
        # Run workflow
        result = graph.invoke(initial_state)
        
        return JSONResponse({
            "status": "success",
            "enhanced_data": result["enhanced_data"],
            "ats_score": result["ats_score"]
        })
    
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)


@router.get("/api/download/{filename}")
async def download_resume(filename: str):
    """Download generated resume"""
    try:
        filepath = f"outputs/{filename}"
        if os.path.exists(filepath):
            return FileResponse(filepath, filename=filename)
        return JSONResponse({"error": "File not found"}, status_code=404)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)


@router.get("/api/health")
async def health():
    """Health check"""
    return {"status": "ok", "service": "AI Resume Builder"}
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(router, host="0.0.0.0", port=8000)