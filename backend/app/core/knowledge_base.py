from typing import Dict, List, Any, Optional
from app.core.llm import get_llm_response
import json

class LegalPrecedents:
    """
    Database of key legal precedents relevant to contract law
    """
    
    # Sample precedents database (would be more extensive in a real system)
    _precedents = {
        "four_corners": {
            "name": "Four Corners Doctrine",
            "principle": "Courts should look only within the four corners of a written contract to determine the parties' intent.",
            "key_cases": [
                "Greenfield v. Philles Records, Inc., 98 N.Y.2d 562 (2002)",
                "W.W.W. Associates, Inc. v. Giancontieri, 77 N.Y.2d 157 (1990)"
            ],
            "exceptions": [
                "Ambiguous terms",
                "Evidence of fraud, duress, or mutual mistake"
            ]
        },
        "contra_proferentem": {
            "name": "Contra Proferentem",
            "principle": "Ambiguous contract terms should be interpreted against the party that drafted the contract.",
            "key_cases": [
                "Mastrobuono v. Shearson Lehman Hutton, Inc., 514 U.S. 52 (1995)",
                "Klapp v. United Insurance Group Agency, Inc., 468 Mich. 459 (2003)"
            ],
            "exceptions": [
                "Equal bargaining power",
                "Sophisticated parties"
            ]
        },
        "unconscionability": {
            "name": "Unconscionability Doctrine",
            "principle": "Courts may refuse to enforce contracts that are excessively unfair or one-sided.",
            "key_cases": [
                "Williams v. Walker-Thomas Furniture Co., 350 F.2d 445 (D.C. Cir. 1965)",
                "AT&T Mobility LLC v. Concepcion, 563 U.S. 333 (2011)"
            ],
            "types": [
                "Procedural unconscionability (unfair surprise)",
                "Substantive unconscionability (overly harsh terms)"
            ]
        }
    }
    
    @classmethod
    def get_precedent(cls, precedent_key: str) -> Dict[str, Any]:
        """Get information about a specific legal precedent"""
        return cls._precedents.get(precedent_key, {"name": "Unknown precedent", "principle": "Not found"})
    
    @classmethod
    def list_precedents(cls) -> List[str]:
        """List all available precedents"""
        return list(cls._precedents.keys())
    
    @classmethod
    async def apply_precedent_to_case(cls, precedent_key: str, case_facts: str) -> Dict[str, Any]:
        """Apply a specific legal precedent to a case fact pattern"""
        if precedent_key not in cls._precedents:
            return {"error": f"Precedent '{precedent_key}' not found"}
            
        precedent = cls._precedents[precedent_key]
        
        prompt = f"""
        Apply the legal precedent of {precedent['name']} to these case facts:
        
        PRECEDENT PRINCIPLE: {precedent['principle']}
        
        KEY CASES: {', '.join(precedent.get('key_cases', []))}
        
        CASE FACTS: {case_facts}
        
        Analyze how this precedent applies to the facts, including:
        1. Whether the precedent is applicable
        2. How the facts align with or differ from the precedent
        3. The likely outcome based on the precedent
        
        Format as a JSON object with these three sections.
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
                
            # Fallback structure
            return {
                "applicability": "Could not determine",
                "analysis": "Error parsing analysis",
                "likely_outcome": "Unknown"
            }