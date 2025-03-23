from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import json

from app.core.legal_reasoner import LegalReasoner, ReasoningMethod
from app.core.legal_authority import LegalAuthority
from app.core.document_processor import DocumentProcessor
from app.core.expert_consultation import ExpertConsultationSystem, LegalExpertise
from app.core.cognitive_system import CognitiveSystem, ThoughtProcess
from app.core.practice_integration import PracticeIntegration, PracticeManagementSystem

router = APIRouter()

class LegalReasoningRequest(BaseModel):
    legal_text: str
    question: str
    methods: Optional[List[str]] = None

class AuthoritySearchRequest(BaseModel):
    legal_question: str
    jurisdiction: Optional[str] = "US"

class AuthorityAnalysisRequest(BaseModel):
    legal_text: str
    authorities: List[Dict[str, Any]]

class ExpertConsultationRequest(BaseModel):
    question: str
    document: str
    experts: Optional[List[str]] = None

class SecondOpinionRequest(BaseModel):
    analysis: Dict[str, Any]
    document: str

class IssueIdentificationRequest(BaseModel):
    document: str

class ClientMemoRequest(BaseModel):
    analysis: Dict[str, Any]
    client_info: Dict[str, Any]

class TimeEntryRequest(BaseModel):
    activities: List[Dict[str, Any]]
    billing_info: Dict[str, Any]

class TaskListRequest(BaseModel):
    project: Dict[str, Any]
    deadline: str

class SystemFormatRequest(BaseModel):
    data: Dict[str, Any]
    system: str

@router.post("/reasoning", response_model=Dict[str, Any])
async def legal_reasoning(request: LegalReasoningRequest):
    """
    Analyze a legal question using multiple reasoning methodologies
    """
    try:
        result = await LegalReasoner.analyze(
            legal_text=request.legal_text,
            question=request.question,
            methods=request.methods
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Legal reasoning failed: {str(e)}")

@router.post("/authorities/search", response_model=Dict[str, Any])
async def find_authorities(request: AuthoritySearchRequest):
    """
    Find relevant legal authorities for a given legal question
    """
    try:
        result = await LegalAuthority.find_relevant_authorities(
            legal_question=request.legal_question,
            jurisdiction=request.jurisdiction
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Authority search failed: {str(e)}")

@router.post("/authorities/analyze", response_model=Dict[str, Any])
async def analyze_with_authorities(request: AuthorityAnalysisRequest):
    """
    Analyze legal text in light of specific legal authorities
    """
    try:
        result = await LegalAuthority.analyze_with_authorities(
            legal_text=request.legal_text,
            authorities=request.authorities
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Authority analysis failed: {str(e)}")

@router.post("/consult", response_model=Dict[str, Any])
async def consult_experts(request: ExpertConsultationRequest):
    """
    Consult multiple specialized experts on a legal question
    """
    try:
        result = await ExpertConsultationSystem.consult_experts(
            question=request.question,
            document=request.document,
            experts=request.experts
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Expert consultation failed: {str(e)}")

@router.post("/second-opinion", response_model=Dict[str, Any])
async def get_second_opinion(request: SecondOpinionRequest):
    """
    Get a second opinion to critique an existing legal analysis
    """
    try:
        result = await ExpertConsultationSystem.get_second_opinion(
            analysis=request.analysis,
            document=request.document
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Second opinion failed: {str(e)}")

@router.post("/identify-issues", response_model=Dict[str, Any])
async def identify_issues(request: IssueIdentificationRequest):
    """
    Identify key legal issues in a document
    """
    try:
        cognitive_system = CognitiveSystem()
        result = await cognitive_system.identify_issues(request.document)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Issue identification failed: {str(e)}")

@router.post("/client-memo", response_model=Dict[str, Any])
async def generate_client_memo(request: ClientMemoRequest):
    """
    Generate a client-ready memo based on a legal analysis
    """
    try:
        result = await PracticeIntegration.generate_client_memo(
            analysis=request.analysis,
            client_info=request.client_info
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Client memo generation failed: {str(e)}")

@router.post("/time-entries", response_model=Dict[str, Any])
async def generate_time_entries(request: TimeEntryRequest):
    """
    Generate formatted time entries for a practice management system
    """
    try:
        result = await PracticeIntegration.generate_time_entries(
            activities=request.activities,
            billing_info=request.billing_info
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Time entry generation failed: {str(e)}")

@router.post("/task-list", response_model=Dict[str, Any])
async def create_task_list(request: TaskListRequest):
    """
    Create a task list with deadlines and assignments for a legal project
    """
    try:
        result = await PracticeIntegration.create_task_list(
            project=request.project,
            deadline=request.deadline
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Task list creation failed: {str(e)}")

@router.post("/format-for-system", response_model=Dict[str, Any])
async def format_for_system(request: SystemFormatRequest):
    """
    Format data for a specific practice management system
    """
    try:
        result = await PracticeIntegration.format_for_system(
            data=request.data,
            system=request.system
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"System formatting failed: {str(e)}")
