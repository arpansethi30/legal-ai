import re
import json
from typing import Dict, List, Any, Optional
from enum import Enum
from app.core.llm import get_llm_response

class DocumentType(Enum):
    """Common legal document types"""
    CONTRACT = "Contract"
    PLEADING = "Pleading"
    MOTION = "Motion"
    BRIEF = "Brief"
    OPINION = "Judicial Opinion"
    STATUTE = "Statute or Code"
    REGULATION = "Regulation"
    POLICY = "Policy Document"

class DocumentProcessor:
    """
    Advanced system for processing legal documents
    """
    
    @staticmethod
    async def identify_document_type(text: str) -> Dict[str, Any]:
        """
        Identify the type of legal document based on content and structure
        """
        prompt = f"""
            Analyze this text and identify what type of legal document it is:
            
            {text[:2000]}...  # Using first 2000 chars for efficiency
            
            Consider:
            1. Document structure and formatting
            2. Language patterns and terminology
            3. Presence of specific legal components
            4. Purpose and function of the document
            
            Identify the document type (e.g., contract, pleading, motion, brief, etc.)
            and provide confidence level and specific markers that support your classification.
            
            Format as a JSON object with "document_type", "confidence", and "markers" properties.
        """
        
        response = await get_llm_response(prompt)
        
        try:
            result = json.loads(response)
            return result
        except json.JSONDecodeError:
            # Try to extract JSON
            try:
                start = response.find('{')
                end = response.rfind('}') + 1
                if start >= 0 and end > 0:
                    json_str = response[start:end]
                    return json.loads(json_str)
            except:
                pass
            
            # Return fallback if parsing fails
            return {
                "document_type": "Unknown",
                "confidence": 0,
                "markers": ["Could not identify document type"]
            }
    
    @staticmethod
    async def extract_document_structure(text: str) -> Dict[str, Any]:
        """
        Extract the structure and key components of a legal document
        """
        prompt = f"""
            Extract the structure and key components of this legal document:
            
            {text[:3000]}...  # Using first 3000 chars, would use full in production
            
            Identify:
            1. Major sections and headings
            2. Key provisions or clauses
            3. Defined terms
            4. Parties involved
            5. Dates and deadlines
            6. Signature blocks
            7. Exhibits or attachments
            8. Any other structural elements
            
            Format as a JSON object with these categories as properties.
        """
        
        response = await get_llm_response(prompt)
        
        try:
            structure = json.loads(response)
            return structure
        except json.JSONDecodeError:
            # Try to extract JSON
            try:
                start = response.find('{')
                end = response.rfind('}') + 1
                if start >= 0 and end > 0:
                    json_str = response[start:end]
                    return json.loads(json_str)
            except:
                pass
            
            # Return fallback if parsing fails
            return {
                "major_sections": [],
                "key_provisions": [],
                "defined_terms": [],
                "parties": [],
                "dates_deadlines": [],
                "signature_blocks": [],
                "exhibits_attachments": [],
                "other_elements": [],
                "error": "Could not extract document structure"
            }
    
    @staticmethod
    async def compare_documents(doc1: str, doc2: str) -> Dict[str, Any]:
        """
        Compare two legal documents and identify differences
        """
        # First extract structure of both documents
        structure1 = await DocumentProcessor.extract_document_structure(doc1)
        structure2 = await DocumentProcessor.extract_document_structure(doc2)
        
        prompt = f"""
            Compare these two legal documents based on their extracted structures:
            
            DOCUMENT 1 STRUCTURE:
            {json.dumps(structure1, indent=2)}
            
            DOCUMENT 2 STRUCTURE:
            {json.dumps(structure2, indent=2)}
            
            Identify:
            1. Structural differences (sections present in one but not the other)
            2. Content differences in similar sections
            3. Changes in defined terms
            4. Changes to parties, dates, or key provisions
            5. Substantive changes that affect legal meaning
            6. Stylistic or non-substantive changes
            
            Format as a JSON object with these categories as properties.
        """
        
        response = await get_llm_response(prompt)
        
        try:
            comparison = json.loads(response)
            return comparison
        except json.JSONDecodeError:
            # Try to extract JSON
            try:
                start = response.find('{')
                end = response.rfind('}') + 1
                if start >= 0 and end > 0:
                    json_str = response[start:end]
                    return json.loads(json_str)
            except:
                pass
            
            # Return fallback if parsing fails
            return {
                "structural_differences": [],
                "content_differences": [],
                "defined_term_changes": [],
                "party_date_provision_changes": [],
                "substantive_changes": [],
                "stylistic_changes": [],
                "error": "Could not complete document comparison"
            }
    
    @staticmethod
    async def generate_redline(doc1: str, doc2: str) -> Dict[str, Any]:
        """
        Generate a redline comparison between two documents
        
        Note: In a real system, this would use a diff algorithm or legal comparison software.
        For the hackathon, we'll simulate key aspects of this functionality.
        """
        prompt = f"""
            Generate a redline comparison between these document excerpts.
            
            ORIGINAL DOCUMENT:
            {doc1[:1500]}...
            
            REVISED DOCUMENT:
            {doc2[:1500]}...
            
            For each significant change:
            1. Identify the text that was removed (with context)
            2. Identify the text that was added (with context)
            3. Classify the change (substantive, clarification, stylistic, etc.)
            4. Note the potential legal impact of the change
            
            Format as a JSON array of change objects with these four properties.
        """
        
        response = await get_llm_response(prompt)
        
        try:
            changes = json.loads(response)
            return {
                "changes": changes,
                "total_changes": len(changes)
            }
        except json.JSONDecodeError:
            # Try to extract a JSON array
            try:
                start = response.find('[')
                end = response.rfind(']') + 1
                if start >= 0 and end > 0:
                    json_str = response[start:end]
                    changes = json.loads(json_str)
                    return {
                        "changes": changes,
                        "total_changes": len(changes)
                    }
            except:
                pass
            
            # Return fallback if parsing fails
            return {
                "changes": [],
                "total_changes": 0,
                "error": "Could not generate redline comparison"
            }
    
    @staticmethod
    async def extract_key_information(text: str, information_types: List[str] = None) -> Dict[str, Any]:
        """
        Extract specific types of information from a legal document
        """
        # Default information types if none provided
        if not information_types:
            information_types = [
                "parties", "dates", "amounts", "obligations", "conditions",
                "representations", "warranties", "termination_rights", "governing_law"
            ]
        
        prompt = f"""
            Extract the following types of information from this legal document:
            {', '.join(information_types)}
            
            DOCUMENT:
            {text[:3000]}...
            
            For each type of information:
            1. Extract all relevant instances
            2. Include the context in which they appear
            3. Note any qualifications or conditions
            
            Format as a JSON object with each information type as a key,
            containing an array of extracted items with context.
        """
        
        response = await get_llm_response(prompt)
        
        try:
            extracted = json.loads(response)
            return extracted
        except json.JSONDecodeError:
            # Try to extract JSON
            try:
                start = response.find('{')
                end = response.rfind('}') + 1
                if start >= 0 and end > 0:
                    json_str = response[start:end]
                    return json.loads(json_str)
            except:
                pass
            
            # Return fallback if parsing fails
            return {information_type: [] for information_type in information_types}
