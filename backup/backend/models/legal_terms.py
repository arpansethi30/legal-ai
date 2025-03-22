# backend/models/legal_terms.py
import re
import json
import os
from typing import List, Dict, Any
import google.generativeai as genai

class LegalTermsExtractor:
    """Extract and define legal terms from documents"""
    
    def __init__(self, gemini_model):
        self.gemini_model = gemini_model
        self.terms_cache_file = "terms_cache.json"
        self.terms_cache = self._load_terms_cache()
        
        # Common legal terms to identify
        self.common_legal_terms = [
            "force majeure", "indemnification", "jurisdiction", "liability", "negligence",
            "tort", "enjoin", "damages", "specific performance", "venue", "arbitration",
            "mediation", "liquidated damages", "warranty", "covenant", "estoppel",
            "fiduciary", "lien", "encumbrance", "easement", "injunction", "materiality",
            "severability", "termination", "assignment", "confidentiality", "waiver"
        ]
        
    def _load_terms_cache(self) -> Dict[str, str]:
        """Load cached legal term definitions from file"""
        if os.path.exists(self.terms_cache_file):
            try:
                with open(self.terms_cache_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
        
    def _save_terms_cache(self) -> None:
        """Save legal term definitions to cache file"""
        try:
            with open(self.terms_cache_file, 'w') as f:
                json.dump(self.terms_cache, f)
        except Exception as e:
            print(f"Error saving terms cache: {e}")
            
    def extract_terms(self, text: str) -> List[str]:
        """Extract legal terms from document text"""
        found_terms = []
        
        # Look for common legal terms
        for term in self.common_legal_terms:
            if re.search(r'\b' + re.escape(term) + r'\b', text.lower()):
                found_terms.append(term)
                
        # Look for defined terms (often in quotes or ALL CAPS)
        defined_terms = re.findall(r'"([^"]+)"|\b([A-Z]{2,}[A-Z\s]+)\b', text)
        for match in defined_terms:
            term = match[0] if match[0] else match[1]
            if len(term) > 3 and term.lower() not in [t.lower() for t in found_terms]:
                found_terms.append(term)
                
        return found_terms
        
    async def get_term_definition(self, term: str) -> str:
        """Get definition of a legal term using Gemini"""
        # Check cache first
        if term.lower() in self.terms_cache:
            return self.terms_cache[term.lower()]
            
        # Otherwise ask Gemini
        try:
            prompt = f"""
            Provide a clear, concise definition of the legal term "{term}". 
            Include the following:
            1. A brief explanation in plain language
            2. The legal context where this term is commonly used
            3. Any important implications
            
            Keep your response under 200 words and focus on accuracy and clarity.
            """
            
            response = self.gemini_model.generate_content(prompt)
            definition = response.text.strip()
            
            # Cache the result
            self.terms_cache[term.lower()] = definition
            self._save_terms_cache()
            
            return definition
            
        except Exception as e:
            return f"Error retrieving definition: {str(e)}"
            
    async def process_document_terms(self, text: str) -> Dict[str, Any]:
        """
        Process a document to extract legal terms and provide definitions
        Returns a dictionary with terms and definitions
        """
        # Extract terms
        terms = self.extract_terms(text)
        
        # Get definitions for each term
        term_definitions = {}
        for term in terms:
            definition = await self.get_term_definition(term)
            term_definitions[term] = definition
            
        return {
            "success": True,
            "terms_count": len(terms),
            "terms": term_definitions
        }


class LegalRiskAssessor:
    """Assess legal risks in documents"""
    
    def __init__(self, gemini_model):
        self.gemini_model = gemini_model
        
        # Common risk categories in legal documents
        self.risk_categories = {
            "liability": ["unlimited liability", "damages", "indemnification"],
            "compliance": ["regulatory", "statute", "compliance", "governed by"],
            "termination": ["termination", "cancel", "rescind", "revoke"],
            "confidentiality": ["confidential", "non-disclosure", "trade secret"],
            "payment": ["payment", "fee", "compensation", "expense", "late payment"],
            "intellectual_property": ["intellectual property", "copyright", "patent", "trademark"]
        }
        
    def identify_risk_factors(self, text: str) -> Dict[str, List[str]]:
        """
        Identify potential risk factors in document text based on keywords
        Returns a dictionary with risk categories and related text snippets
        """
        risks = {}
        text_lower = text.lower()
        
        # Check for each risk category
        for category, keywords in self.risk_categories.items():
            matches = []
            
            for keyword in keywords:
                # Find surrounding context for keyword matches
                for match in re.finditer(r'\b' + re.escape(keyword.lower()) + r'\b', text_lower):
                    start = max(0, match.start() - 100)
                    end = min(len(text), match.end() + 100)
                    context = text[start:end].strip()
                    matches.append(context)
                    
            if matches:
                risks[category] = matches
                
        return risks
        
    async def analyze_risks(self, document_text: str, document_type: str = "contract") -> Dict[str, Any]:
        """
        Analyze legal risks in a document
        Returns analysis of risk factors with AI-generated insights
        """
        # First identify risk factors based on keywords
        risk_factors = self.identify_risk_factors(document_text)
        
        # Use Gemini to analyze the risks
        prompt = f"""
        Analyze the following legal document of type {document_type} for potential legal risks.
        
        Document excerpts by risk category:
        {json.dumps(risk_factors, indent=2)}
        
        Please provide:
        1. An assessment of the overall risk level (Low, Medium, High)
        2. Specific risk concerns for each category identified
        3. Recommendations to mitigate these risks
        
        Format your response as JSON with keys: 'overall_risk', 'risk_analysis', and 'recommendations'.
        """
        
        try:
            response = self.gemini_model.generate_content(prompt)
            analysis = response.text
            
            try:
                # Try to parse as JSON, but handle case where model doesn't return proper JSON
                analysis_json = json.loads(analysis)
            except:
                # If not valid JSON, create structured response manually
                analysis_json = {
                    "overall_risk": "Unable to determine",
                    "risk_analysis": "Unable to parse model output as JSON. See raw analysis.",
                    "recommendations": "",
                    "raw_analysis": analysis
                }
                
            return {
                "success": True,
                "risk_factors": risk_factors,
                "analysis": analysis_json,
                "model": "gemini-1.5-pro"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "risk_factors": risk_factors,
            } 