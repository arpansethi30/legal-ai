from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Any, Optional

from app.core.agent import LegalAgent

router = APIRouter()

class AgentTaskRequest(BaseModel):
    task: str
    context: Optional[Dict[str, Any]] = None

class AgentTaskResponse(BaseModel):
    task_id: str
    result: Dict[str, Any]

@router.post("/execute", response_model=AgentTaskResponse)
async def execute_agent_task(request: AgentTaskRequest):
    """
    Execute a complex legal task using the AI agent
    """
    try:
        # Create agent instance
        agent = LegalAgent()
        
        # Execute task
        result = await agent.execute_task(request.task)
        
        # Return with a task ID (in a real app, this would be stored in a database)
        import uuid
        task_id = str(uuid.uuid4())
        
        return {
            "task_id": task_id,
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent execution failed: {str(e)}")

class DisputeMediationRequest(BaseModel):
    party_a_position: str
    party_b_position: str
    disputed_terms: List[str]
    context: Optional[str] = None

@router.post("/mediate", response_model=Dict[str, Any])
async def mediate_dispute(request: DisputeMediationRequest):
    """
    Mediate a contract dispute between two parties
    """
    try:
        # Format the dispute context
        dispute_context = f"""
        Party A Position:
        {request.party_a_position}
        
        Party B Position:
        {request.party_b_position}
        
        Disputed Terms:
        {', '.join(request.disputed_terms)}
        
        Additional Context:
        {request.context or 'None provided'}
        """
        
        # Create agent and use its mediation capability
        agent = LegalAgent()
        result = await agent._mediate_dispute(dispute_context)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Mediation failed: {str(e)}")

class ContractComparisonRequest(BaseModel):
    contract_a: str
    contract_b: str
    focus_areas: Optional[List[str]] = None

@router.post("/compare-contracts", response_model=Dict[str, Any])
async def compare_contracts(request: ContractComparisonRequest):
    """
    Compare two contracts and identify key differences
    """
    try:
        # Create context for comparison
        focus_areas_text = ', '.join(request.focus_areas) if request.focus_areas else "all sections"
        
        comparison_context = f"""
        Task: Compare the following two contracts and identify key differences, especially in {focus_areas_text}.
        
        Contract A:
        {request.contract_a}
        
        Contract B:
        {request.contract_b}
        """
        
        # Create agent and execute the task
        agent = LegalAgent()
        plan = [
            {
                "action": "analyze_text",
                "input": comparison_context,
                "expected_output": "Comparison analysis"
            }
        ]
        
        # Store plan in working memory
        agent.working_memory["plan"] = plan
        agent.working_memory["task"] = "Compare contracts"
        agent.working_memory["results"] = []
        
        # Execute the step
        result = await agent.execute_step(plan[0])
        
        return {
            "comparison": result,
            "summary": {
                "key_differences": result.get("key_differences", ["Analysis failed"]),
                "recommendations": result.get("recommendations", ["Analysis failed"])
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Contract comparison failed: {str(e)}")
@router.post("/deliberate", response_model=Dict[str, Any])
async def legal_deliberation(request: Dict[str, str]):
    """
    Perform structured legal reasoning on a specific question
    """
    try:
        # Extract the question and optional context
        question = request.get("question", "")
        context = request.get("context", "")
        
        if not question:
            raise HTTPException(status_code=400, detail="Question is required")
        
        # Create agent instance
        agent = LegalAgent()
        
        # Perform deliberation
        result = await agent._deliberate(question, context)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Deliberation failed: {str(e)}")