# backend/app/main.py
import os
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from .config import settings
from .routers import document, query, advanced_legal, research

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="Legal AI API",
    description="Advanced Legal AI API with specialized capabilities",
    version="2.0.0"
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
app.include_router(advanced_legal.router, prefix=settings.API_PREFIX)
app.include_router(research.router, prefix=settings.API_PREFIX)

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

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)