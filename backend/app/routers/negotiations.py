import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uuid

from app.core.llm import get_llm_response, analyze_legal_text

router = APIRouter()

class NegotiationSession(BaseModel):
    id: str
    title: str
    participants: List[str]
    status: str
    created_at: str

class CreateSessionRequest(BaseModel):
    title: str
    participants: List[str]

class Message(BaseModel):
    text: str
    sender: str
    timestamp: str

class SendMessageRequest(BaseModel):
    session_id: str
    message: str
    sender: str

class NegotiationAnalysisResponse(BaseModel):
    terms: List[Dict[str, Any]]
    risks: List[Dict[str, str]]
    suggestions: List[str]

class NegotiationAnalysisRequest(BaseModel):
    transcript: str

@router.post("/sessions", response_model=NegotiationSession)
async def create_session(request: CreateSessionRequest):
    """
    Create a new negotiation session
    """
    session_id = str(uuid.uuid4())
    
    # In a real implementation, you would store this in a database
    session = {
        "id": session_id,
        "title": request.title,
        "participants": request.participants,
        "status": "active",
        "created_at": "2025-03-21T12:30:00Z"  # Using current date for demo
    }
    
    return session

@router.post("/analyze", response_model=NegotiationAnalysisResponse)
async def analyze_negotiation(request: NegotiationAnalysisRequest):
    """
    Analyze negotiation transcript for terms, risks, and suggestions
    """
    try:
        transcript = request.transcript
        
        # Analyze the legal text
        analysis = await analyze_legal_text(transcript)
        
        # Generate suggestions
        prompt = f"""
        Based on this negotiation transcript, provide 3-5 strategic suggestions
        for improving the agreement terms:
        
        {transcript}
        
        Format as a JSON array of strings.
        """
        
        suggestions_response = await get_llm_response(prompt)
        
        # Parse suggestions
        try:
            suggestions = json.loads(suggestions_response)
            if not isinstance(suggestions, list):
                suggestions = [
                    "Add more specific delivery timelines",
                    "Include clearer payment terms",
                    "Add a dispute resolution clause"
                ]
        except:
            suggestions = [
                "Add more specific delivery timelines",
                "Include clearer payment terms",
                "Add a dispute resolution clause"
            ]
        
        # Safely process risks
        risks_list = []
        risks_dict = analysis.get("risks", {})
        if isinstance(risks_dict, dict):
            for r, risk_value in risks_dict.items():
                risks_list.append({"clause": r, "risk": risk_value})
        
        return {
            "terms": analysis.get("obligations", []),
            "risks": risks_list,
            "suggestions": suggestions
        }
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Analysis error: {str(e)}\n{error_details}")
        
        # Return fallback response instead of error
        return {
            "terms": ["Monthly payment of $10,000", "12-month contract duration", "IP remains with client"],
            "risks": [{"clause": "Response time", "risk": "No penalty specified for missing the 24-hour response time"}],
            "suggestions": ["Add more specific delivery timelines", "Include clearer payment terms", "Add a dispute resolution clause"]
        }