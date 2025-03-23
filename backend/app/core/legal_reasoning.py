import asyncio
import json
from enum import Enum
from typing import Dict, List, Any, Optional
from app.core.llm import get_llm_response
from app.services.langtrace import trace_function

class LegalDoctrines(Enum):
    """Core legal doctrines relevant to contract analysis"""
    FOUR_CORNERS = "Four Corners Doctrine"
    CONTRA_PROFERENTEM = "Contra Proferentem"
    UNCONSCIONABILITY = "Unconscionability"
    CONSIDERATION = "Consideration"
    GOOD_FAITH = "Good Faith and Fair Dealing"
    FORCE_MAJEURE = "Force Majeure"
    INDEMNIFICATION = "Indemnification"
    SEVERABILITY = "Severability"

class IRAC:
    """Issue, Rule, Analysis, Conclusion legal reasoning framework"""
    
    @staticmethod
    @trace_function(tags=["legal", "irac"])
    async def apply(legal_text: str, question: str) -> Dict[str, Any]:
        """
        Apply the IRAC legal reasoning framework to a legal question
        """
        prompt = f"""
        Legal Text: {legal_text}
        
        Legal Question: {question}
        
        Apply the formal IRAC (Issue, Rule, Analysis, Conclusion) legal reasoning framework:
        
        1. ISSUE: Identify the precise legal issue or question presented
        2. RULE: Identify the relevant legal rules, principles, or standards that apply
        3. ANALYSIS: Apply the rules to the specific facts in the legal text
        4. CONCLUSION: State the conclusion that follows from the analysis
        
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
                "ISSUE": "Could not parse issue",
                "RULE": "Could not parse applicable rules",
                "ANALYSIS": "Could not generate analysis",
                "CONCLUSION": "Could not determine conclusion"
            }

class ClauseLibrary:
    """Standard contract clause library"""
    
    _clauses = {
        "confidentiality": {
            "standard": "Each party shall protect the other's confidential information with the same degree of care as it uses for its own confidential information of like nature, but no less than reasonable care.",
            "strict": "Recipient shall not disclose Confidential Information to any third party and shall limit access to such information to its employees strictly on a need-to-know basis.",
            "moderate": "Recipient may disclose Confidential Information to its employees, agents, and contractors who have a need to know, provided they are bound by similar confidentiality obligations."
        },
        "force_majeure": {
            "standard": "Neither party shall be liable for any failure or delay in performance due to circumstances beyond its reasonable control.",
            "detailed": "Neither party shall be liable for any failure or delay in performance due to acts of God, war, terrorism, civil unrest, fire, explosion, accident, flood, sabotage, governmental action, or other events beyond its reasonable control."
        },
        "indemnification": {
            "standard": "Each party shall indemnify and hold harmless the other from any claims arising from its breach of this Agreement.",
            "supplier": "Supplier shall defend, indemnify, and hold harmless Client from any third-party claims arising from the Services provided under this Agreement.",
            "mutual": "Each party shall defend, indemnify, and hold harmless the other party from any third-party claims arising from the indemnifying party's breach of this Agreement or negligence."
        },
        "termination": {
            "standard": "Either party may terminate this Agreement upon 30 days' written notice.",
            "for_cause": "Either party may terminate this Agreement immediately upon written notice if the other party materially breaches this Agreement.",
            "mutual": "This Agreement may be terminated: (a) by mutual written agreement; (b) by either party upon 30 days' written notice; or (c) immediately by either party if the other party breaches this Agreement."
        },
        "governing_law": {
            "standard": "This Agreement shall be governed by the laws of [STATE/COUNTRY], without regard to its conflict of laws principles.",
            "arbitration": "This Agreement shall be governed by the laws of [STATE/COUNTRY]. Any disputes shall be resolved through binding arbitration conducted in [LOCATION] in accordance with the rules of [ARBITRATION BODY]."
        }
    }
    
    @classmethod
    async def get_clause(cls, clause_type: str, variant: str = "standard", context: str = "") -> str:
        """Get a standard clause with optional customization based on context"""
        if clause_type not in cls._clauses:
            return f"Clause type '{clause_type}' not found in library."
            
        if variant not in cls._clauses[clause_type]:
            variant = "standard"  # Default to standard if variant not found
            
        clause = cls._clauses[clause_type][variant]
        
        # If context provided, customize the clause
        if context:
            prompt = f"""
            Standard legal clause: "{clause}"
            
            Context for customization: {context}
            
            Please customize this standard clause to fit the given context while 
            maintaining its legal meaning and enforceability.
            
            Return only the customized clause text.
            """
            
            customized = await get_llm_response(prompt)
            return customized
            
        return clause