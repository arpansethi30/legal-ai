import json
from typing import Dict, List, Any
from app.core.llm import get_llm_response
from app.core.legal_reasoning import ClauseLibrary

# Contract type definitions with required sections
CONTRACT_TYPES = {
    "service_agreement": {
        "required_sections": [
            "parties", "services", "term", "payment", "confidentiality", 
            "intellectual_property", "warranties", "limitation_of_liability", 
            "termination", "governing_law"
        ],
        "description": "Agreement for professional services provision"
    },
    "nda": {
        "required_sections": [
            "parties", "confidential_information", "obligations", "exclusions", 
            "term", "return_of_information", "remedies", "governing_law"
        ],
        "description": "Agreement to protect confidential information"
    },
    "employment": {
        "required_sections": [
            "parties", "position", "duties", "compensation", "benefits", 
            "term", "termination", "confidentiality", "non_compete", 
            "intellectual_property", "governing_law"
        ],
        "description": "Agreement between employer and employee"
    },
    "licensing": {
        "required_sections": [
            "parties", "license_grant", "restrictions", "fees", "term", 
            "termination", "warranties", "indemnification", "limitation_of_liability", 
            "governing_law"
        ],
        "description": "Agreement to license intellectual property"
    },
    "partnership": {
        "required_sections": [
            "parties", "purpose", "contributions", "profit_sharing", "management", 
            "term", "withdrawal", "dissolution", "confidentiality", "governing_law"
        ],
        "description": "Agreement to form a business partnership"
    }
}

class RiskAssessment:
    """Risk assessment for contract clauses"""
    
    @staticmethod
    async def assess_clause(clause_text: str, context: str = "") -> Dict[str, Any]:
        """
        Analyze a contract clause for legal risks
        """
        prompt = f"""
        Analyze this contract clause for legal risks:
        
        CLAUSE: {clause_text}
        
        {f"CONTEXT: {context}" if context else ""}
        
        Provide a detailed risk assessment including:
        1. Risk Level (Low, Medium, High)
        2. Identified Ambiguities
        3. Potential Enforcement Issues
        4. Suggested Improvements
        
        Format as a JSON object with these four sections.
        """
        
        response = await get_llm_response(prompt)
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # Extract JSON if possible
            try:
                start = response.find('{')
                end = response.rfind('}') + 1
                if start >= 0 and end > 0:
                    return json.loads(response[start:end])
            except:
                pass
                
            # Fallback structure
            return {
                "Risk_Level": "Medium",
                "Identified_Ambiguities": ["Could not parse ambiguities"],
                "Potential_Enforcement_Issues": ["Could not identify enforcement issues"],
                "Suggested_Improvements": ["Have this clause reviewed by legal counsel"]
            }
    
    @staticmethod
    async def identify_missing_sections(contract_text: str, contract_type: str) -> List[str]:
        """
        Identify standard sections missing from a contract
        """
        if contract_type not in CONTRACT_TYPES:
            return ["Unknown contract type"]
            
        required_sections = CONTRACT_TYPES[contract_type]["required_sections"]
        
        prompt = f"""
        Analyze this {contract_type} and identify which of these standard sections are missing:
        {', '.join(required_sections)}
        
        CONTRACT TEXT:
        {contract_text}
        
        Return a JSON array of missing sections.
        """
        
        response = await get_llm_response(prompt)
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # Try to extract a JSON array
            try:
                start = response.find('[')
                end = response.rfind(']') + 1
                if start >= 0 and end > 0:
                    return json.loads(response[start:end])
            except:
                pass
                
            # Fallback response
            return ["Could not analyze missing sections"]