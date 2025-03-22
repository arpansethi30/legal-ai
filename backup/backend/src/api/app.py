# backend/src/api/app.py
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from src.config.settings import get_settings
from src.api.routers import document, query, advanced_legal, research

def create_app() -> FastAPI:
    """
    Application factory pattern for creating the FastAPI app
    """
    # Load environment variables
    load_dotenv()
    
    settings = get_settings()
    
    # Create FastAPI app
    app = FastAPI(
        title="Legal AI API",
        description="Advanced Legal AI API with specialized capabilities",
        version=settings.APP_VERSION
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Update for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(
        document.router,
        prefix=settings.API_PREFIX
    )
    app.include_router(
        query.router,
        prefix=settings.API_PREFIX
    )
    app.include_router(
        advanced_legal.router, 
        prefix=settings.API_PREFIX
    )
    app.include_router(
        research.router, 
        prefix=settings.API_PREFIX
    )

    @app.get("/")
    async def root():
        """Root endpoint with API information"""
        return {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "description": "A multimodal AI agent for legal document analysis and queries"
        }

    @app.get("/healthcheck")
    async def healthcheck():
        """Health check endpoint"""
        return {
            "status": "healthy",
            "api_version": settings.APP_VERSION
        }
        
    return app 