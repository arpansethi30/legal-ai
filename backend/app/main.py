from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv

from app.routers import auth, contracts, negotiations, voice, agent  # Add agent here
from app.services.langtrace import setup_langtrace

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="Legal Negotiation AI",
    description="AI-powered legal negotiation and contract drafting assistant",
    version="0.1.0"
)

# Setup CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Langtrace monitoring
setup_langtrace()

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(contracts.router, prefix="/contracts", tags=["Contracts"])
app.include_router(negotiations.router, prefix="/negotiations", tags=["Negotiations"])
app.include_router(voice.router, prefix="/voice", tags=["Voice"])
app.include_router(agent.router, prefix="/agent", tags=["AI Agent"])  # Add this line

@app.get("/")
async def root():
    return {
        "status": "online",
        "message": "Legal Negotiation AI API is running",
        "documentation": "/docs"
    }

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
