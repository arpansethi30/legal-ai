from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
import uuid

from app.services.contract_gen import generate_contract, analyze_contract_risks
from app.services.langtrace import trace_function

router = APIRouter()

class ContractRequest(BaseModel):
    negotiation_id: str
    parties: List[str]
    terms: List[Dict[str, str]]
    contract_type: str

class ContractResponse(BaseModel):
    contract_id: str
    content: str
    version: int
    status: str

class RiskAnalysisRequest(BaseModel):
    contract_text: str

class RiskAnalysisResponse(BaseModel):
    risks: List[Dict[str, str]]

@router.post("/generate", response_model=ContractResponse)
@trace_function(tags=["contract", "generation"])
async def create_contract(request: ContractRequest):
    """
    Generate a contract based on negotiation terms
    """
    try:
        contract = await generate_contract(
            negotiation_id=request.negotiation_id,
            parties=request.parties,
            terms=request.terms,
            contract_type=request.contract_type
        )
        return contract
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Contract generation failed: {str(e)}")

@router.post("/analyze", response_model=RiskAnalysisResponse)
async def analyze_risks(request: RiskAnalysisRequest):
    """
    Analyze contract for potential legal risks
    """
    try:
        risks = await analyze_contract_risks(request.contract_text)
        return {"risks": risks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Risk analysis failed: {str(e)}")

@router.get("/templates", response_model=List[str])
async def get_contract_templates():
    """
    Get available contract templates
    """
    templates = ["service_agreement", "nda", "employment", "licensing", "partnership"]
    return templates

@router.post("/analyze-risks", response_model=RiskAnalysisResponse)
async def analyze_contract_risks(request: RiskAnalysisRequest):
    """
    Analyze contract for potential legal risks
    """
    try:
        risks = await analyze_contract_risks(request.contract_text)
        return {"risks": risks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Risk analysis failed: {str(e)}")
