import json
from typing import Dict, List, Any, Optional
from enum import Enum
from app.core.llm import get_llm_response

class RegulatoryDomain(Enum):
    """Major regulatory domains for compliance checking"""
    DATA_PRIVACY = "Data Privacy and Protection"
    EMPLOYMENT = "Employment and Labor Law"
    INTELLECTUAL_PROPERTY = "Intellectual Property"
    CONSUMER_PROTECTION = "Consumer Protection"
    FINANCIAL = "Financial Regulations"
    HEALTHCARE = "Healthcare Regulations"
    ENVIRONMENTAL = "Environmental Regulations"

class JurisdictionLevel(Enum):
    """Levels of jurisdictional authority"""
    INTERNATIONAL = "International"
    FEDERAL = "Federal/National"
    STATE = "State/Provincial"
    LOCAL = "Local/Municipal"

class ComplianceEngine:
    """
    Advanced system for checking contract compliance with regulations
    """
    
    @staticmethod
    async def check_compliance(contract_text: str, domains: List[str] = None, jurisdiction: str = "US") -> Dict[str, Any]:
        """
        Check contract compliance with specified regulatory domains
        """
        # Default to data privacy and employment if no domains specified
        if not domains:
            domains = [RegulatoryDomain.DATA_PRIVACY.value, RegulatoryDomain.EMPLOYMENT.value]
        
        prompt = f"""
            Check this contract for compliance with regulations in these domains:
            {', '.join(domains)}
            
            Jurisdiction: {jurisdiction}
            
            CONTRACT:
            {contract_text}
            
            For each regulatory domain:
            1. Identify the key regulations or laws that apply
            2. Assess whether the contract complies with each regulation
            3. Flag any potential compliance issues or gaps
            4. Provide specific recommendations to address compliance issues
            
            Format as a JSON object with each domain as a key, containing an object with
            "applicable_regulations", "compliance_status", "issues", and "recommendations" properties.
        """
        
        response = await get_llm_response(prompt)
        
        try:
            compliance = json.loads(response)
            return {
                "jurisdiction": jurisdiction,
                "domains": domains,
                "compliance_results": compliance
            }
        except json.JSONDecodeError:
            # Try to extract JSON
            try:
                start = response.find('{')
                end = response.rfind('}') + 1
                if start >= 0 and end > 0:
                    json_str = response[start:end]
                    compliance = json.loads(json_str)
                    return {
                        "jurisdiction": jurisdiction,
                        "domains": domains,
                        "compliance_results": compliance
                    }
            except:
                pass
            
            # Return basic structure if parsing fails
            return {
                "jurisdiction": jurisdiction,
                "domains": domains,
                "compliance_results": {domain: {
                    "applicable_regulations": [],
                    "compliance_status": "Could not determine",
                    "issues": ["Analysis failed"],
                    "recommendations": ["Consult with regulatory counsel"]
                } for domain in domains},
                "error": "Compliance check failed"
            }
    
    @staticmethod
    async def generate_compliance_clauses(requirements: str, jurisdiction: str = "US") -> Dict[str, Any]:
        """
        Generate contract clauses to ensure compliance with specific regulatory requirements
        """
        prompt = f"""
            Generate contract clauses that ensure compliance with these regulatory requirements:
            
            REQUIREMENTS:
            {requirements}
            
            JURISDICTION:
            {jurisdiction}
            
            For each major requirement:
            1. Draft a legally compliant clause
            2. Explain how the clause addresses the requirement
            3. Note any jurisdictional variations that might be needed
            
            Format as a JSON array of clause objects, each with "clause_text", "explanation", 
            and "jurisdictional_notes" properties.
        """
        
        response = await get_llm_response(prompt)
        
        try:
            clauses = json.loads(response)
            return {
                "requirements": requirements,
                "jurisdiction": jurisdiction,
                "compliance_clauses": clauses
            }
        except json.JSONDecodeError:
            # Try to extract a JSON array
            try:
                start = response.find('[')
                end = response.rfind(']') + 1
                if start >= 0 and end > 0:
                    json_str = response[start:end]
                    clauses = json.loads(json_str)
                    return {
                        "requirements": requirements,
                        "jurisdiction": jurisdiction,
                        "compliance_clauses": clauses
                    }
            except:
                pass
            
            # Return basic structure if parsing fails
            return {
                "requirements": requirements,
                "jurisdiction": jurisdiction,
                "compliance_clauses": [],
                "error": "Could not generate compliance clauses"
            }
