from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import json

from app.core.multi_agent import LegalMultiAgentSystem
from app.core.legal_graph import LegalKnowledgeGraph
from app.core.adversarial import AdversarialTester
from app.core.document_embeddings import LegalDocumentEmbeddings
from app.core.temporal_reasoning import TemporalReasoning
from app.core.contract_simulation import ContractSimulation
from app.core.regulatory_compliance import ComplianceEngine

router = APIRouter()

class MultiAgentRequest(BaseModel):
    legal_question: str
    context: str
    rounds: Optional[int] = 3

class GraphExtractionRequest(BaseModel):
    legal_text: str

class GraphQueryRequest(BaseModel):
    query: str
    graph_data: Dict[str, Any]

class AdversarialTestRequest(BaseModel):
    contract_text: str
    perspective: Optional[str] = "neutral"

class ScenarioSimulationRequest(BaseModel):
    contract_text: str
    num_scenarios: Optional[int] = 3

class SemanticSearchRequest(BaseModel):
    contract_text: str
    query: str

class TimelineRequest(BaseModel):
    contract_text: str
    start_date: str

class ComplianceCheckRequest(BaseModel):
    contract_text: str
    domains: Optional[List[str]] = None
    jurisdiction: Optional[str] = "US"

@router.post("/multi-agent/deliberate", response_model=Dict[str, Any])
async def multi_agent_deliberation(request: MultiAgentRequest):
    """
    Conduct a multi-agent legal deliberation with specialized legal experts
    """
    try:
        system = LegalMultiAgentSystem()
        result = await system.deliberate(
            request.legal_question,
            request.context,
            request.rounds
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Multi-agent deliberation failed: {str(e)}")

@router.post("/knowledge-graph/extract", response_model=Dict[str, Any])
async def extract_legal_knowledge_graph(request: GraphExtractionRequest):
    """
    Extract a knowledge graph from legal text
    """
    try:
        graph = LegalKnowledgeGraph()
        result = await graph.extract_graph_from_text(request.legal_text)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Knowledge graph extraction failed: {str(e)}")

@router.post("/knowledge-graph/query", response_model=Dict[str, Any])
async def query_legal_knowledge_graph(request: GraphQueryRequest):
    """
    Query a legal knowledge graph using natural language
    """
    try:
        graph = LegalKnowledgeGraph()
        result = await graph.query_graph(request.query, request.graph_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Knowledge graph query failed: {str(e)}")

@router.post("/adversarial/test", response_model=Dict[str, Any])
async def test_contract_adversarially(request: AdversarialTestRequest):
    """
    Find weaknesses, loopholes, and exploitable ambiguities in a contract
    """
    try:
        tester = AdversarialTester()
        result = await tester.find_weaknesses(
            request.contract_text,
            request.perspective
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Adversarial testing failed: {str(e)}")

@router.post("/adversarial/simulate", response_model=Dict[str, Any])
async def simulate_contract_scenarios(request: ScenarioSimulationRequest):
    """
    Generate and simulate hypothetical scenarios to test contract robustness
    """
    try:
        tester = AdversarialTester()
        result = await tester.simulate_scenarios(
            request.contract_text,
            request.num_scenarios
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scenario simulation failed: {str(e)}")

@router.post("/semantic/search", response_model=Dict[str, Any])
async def semantic_clause_search(request: SemanticSearchRequest):
    """
    Semantically search for relevant clauses in a contract
    """
    try:
        embeddings = LegalDocumentEmbeddings()
        result = await embeddings.semantic_clause_search(
            request.contract_text,
            request.query
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Semantic search failed: {str(e)}")

@router.post("/temporal/timeline", response_model=Dict[str, Any])
async def create_contract_timeline(request: TimelineRequest):
    """
    Create a timeline of all obligations and events from a contract
    """
    try:
        result = await TemporalReasoning.create_timeline(
            request.contract_text,
            request.start_date
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Timeline creation failed: {str(e)}")

@router.post("/temporal/deadlines", response_model=Dict[str, Any])
async def identify_critical_deadlines(request: GraphExtractionRequest):
    """
    Identify critical deadlines in a contract with risk assessment
    """
    try:
        result = await TemporalReasoning.identify_critical_deadlines(
            request.legal_text
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Critical deadline identification failed: {str(e)}")

@router.post("/simulation/monte-carlo", response_model=Dict[str, Any])
async def monte_carlo_contract_simulation(request: ScenarioSimulationRequest):
    """
    Run multiple simulations with different scenarios to assess contract robustness
    """
    try:
        result = await ContractSimulation.monte_carlo_simulation(
            request.contract_text,
            request.num_scenarios
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Monte Carlo simulation failed: {str(e)}")

@router.post("/compliance/check", response_model=Dict[str, Any])
async def check_regulatory_compliance(request: ComplianceCheckRequest):
    """
    Check contract compliance with specified regulatory domains
    """
    try:
        result = await ComplianceEngine.check_compliance(
            request.contract_text,
            request.domains,
            request.jurisdiction
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Compliance check failed: {str(e)}")
