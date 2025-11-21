from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.routes import router


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    
    app = FastAPI(title="AI Resume Builder", version="1.0")
    
    # Add CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Mount static files
    app.mount("/static", StaticFiles(directory="static"), name="static")
    
    # Include router
    app.include_router(router)
    
    return app
