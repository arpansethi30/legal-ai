from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv

from app.routers import auth, contracts, negotiations, voice, agent, analytics, workflow
from app.services.langtrace import setup_langtrace
from app.middleware import LegalAuditMiddleware, PrivilegeProtectionMiddleware

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="LexCounsel AI",
    description="State-of-the-art legal AI system for contract analysis, negotiation, and risk assessment",
    version="3.0.0"
)

# Setup CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add legal-specific middleware
app.add_middleware(LegalAuditMiddleware)
app.add_middleware(PrivilegeProtectionMiddleware)

# Initialize Langtrace monitoring
setup_langtrace()

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(contracts.router, prefix="/contracts", tags=["Contracts"])
app.include_router(negotiations.router, prefix="/negotiations", tags=["Negotiations"])
app.include_router(voice.router, prefix="/voice", tags=["Voice"])
app.include_router(agent.router, prefix="/agent", tags=["AI Agent"])
app.include_router(analytics.router, prefix="/analytics", tags=["Legal Analytics"])
app.include_router(workflow.router, prefix="/workflow", tags=["Legal Workflow"])

@app.get("/")
async def root():
    return {
        "system": "LexCounsel AI",
        "status": "operational",
        "version": "3.0.0",
        "core_capabilities": [
            "Multi-methodology legal reasoning",
            "Authority-based legal analysis",
            "Expert consultation simulation",
            "Interactive legal issue identification",
            "Cognitive exploration of legal problems",
            "Practice management integration",
            "Legal document processing and analysis"
        ]
    }

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)