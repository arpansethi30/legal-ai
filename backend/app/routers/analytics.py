from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import json

from app.core.legal_reasoning import IRAC, LegalDoctrines
from app.core.knowledge_base import LegalPrecedents
from app.core.llm import get_llm_response

router = APIRouter()

class LegalAnalysisRequest(BaseModel):
    contract_text: str
    question: Optional[str] = None
    doctrines: Optional[List[str]] = None

class PrecedentAnalysisRequest(BaseModel):
    case_facts: str
    precedent_key: str

@router.post("/irac", response_model=Dict[str, Any])
async def analyze_with_irac(request: LegalAnalysisRequest):
    """
    Analyze a legal issue using the formal IRAC method
    """
    question = request.question or "What are the main legal obligations in this contract?"
    
    try:
        result = await IRAC.apply(request.contract_text, question)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"IRAC analysis failed: {str(e)}")

@router.post("/doctrines", response_model=Dict[str, Any])
async def analyze_with_doctrines(request: LegalAnalysisRequest):
    """
    Analyze a contract through the lens of specified legal doctrines
    """
    # Use provided doctrines or default to a few common ones
    doctrines = request.doctrines or [
        LegalDoctrines.FOUR_CORNERS.value,
        LegalDoctrines.CONTRA_PROFERENTEM.value
    ]
    
    try:
        prompt = f"""
        Analyze this contract through the lens of these legal doctrines:
        {', '.join(doctrines)}
        
        CONTRACT TEXT:
        {request.contract_text}
        
        For each doctrine, provide:
        1. How the doctrine applies to this contract
        2. Potential issues or considerations
        3. Recommendations based on the doctrine
        
        Format as a JSON object with each doctrine as a key.
        """
        
        response = await get_llm_response(prompt)
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # Try to extract JSON
            try:
                start = response.find('{')
                end = response.rfind('}') + 1
                if start >= 0 and end > 0:
                    return json.loads(response[start:end])
            except:
                pass
                
            # Return error information
            raise HTTPException(status_code=422, detail="Could not parse analysis result")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Doctrine analysis failed: {str(e)}")

@router.post("/precedents", response_model=Dict[str, Any])
async def analyze_with_precedent(request: PrecedentAnalysisRequest):
    """
    Apply a legal precedent to a case fact pattern
    """
    try:
        result = await LegalPrecedents.apply_precedent_to_case(
            request.precedent_key, 
            request.case_facts
        )
        
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
            
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Precedent analysis failed: {str(e)}")

@router.get("/precedents", response_model=List[str])
async def list_precedents():
    """
    List available legal precedents
    """
    return LegalPrecedents.list_precedents()