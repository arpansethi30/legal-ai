import asyncio
import json
import uuid
from typing import List, Dict, Any

from app.core.llm import get_llm_response

async def generate_contract(negotiation_id: str, parties: List[str], terms: List[dict], contract_type: str):
    """
    Generate a legal contract based on negotiation terms
    """
    # Convert terms to a formatted string for the prompt
    terms_text = "\n".join([f"- {term['type']}: {term['details']}" for term in terms])
    
    # Create prompt for contract generation
    prompt = f"""
    Create a formal legal {contract_type} contract with the following details:
    
    Parties involved: {', '.join(parties)}
    
    Terms and conditions:
    {terms_text}
    
    Include the following sections:
    1. Definitions
    2. Scope of Agreement
    3. Term and Termination
    4. Payment Terms
    5. Confidentiality
    6. Intellectual Property
    7. Liability and Indemnification
    8. General Provisions
    
    Format the contract in proper legal language and structure.
    """
    
    # Generate contract content using LLM
    contract_content = await get_llm_response(prompt)
    
    # Generate a unique contract ID
    contract_id = str(uuid.uuid4())
    
    # Return the contract data
    return {
        "contract_id": contract_id,
        "content": contract_content,
        "version": 1,
        "status": "draft"
    }

async def analyze_contract_risks(contract_text: str) -> List[Dict[str, str]]:
    """
    Analyze contract for potential legal risks
    """
    prompt = f"""
    Analyze the following contract for potential legal risks, ambiguities, or unfavorable terms.
    Identify specific clauses that could lead to disputes or legal issues.
    
    Contract:
    {contract_text}
    
    Provide your analysis as a JSON array of risks, where each risk has:
    1. "clause": The specific clause or section
    2. "risk": Description of the potential issue
    3. "recommendation": Suggested improvement
    
    Format as JSON.
    """
    
    result = await get_llm_response(prompt)
    
    try:
        # Try to parse as JSON
        risks = json.loads(result)
        return risks
    except:
        # Extract JSON from the response if it's not pure JSON
        try:
            start_idx = result.find('[')
            end_idx = result.rfind(']') + 1
            if start_idx >= 0 and end_idx > start_idx:
                json_str = result[start_idx:end_idx]
                return json.loads(json_str)
        except:
            # Fallback if parsing fails
            return [
                {
                    "clause": "General",
                    "risk": "Unable to analyze contract risks",
                    "recommendation": "Review contract manually with legal counsel"
                }
            ]