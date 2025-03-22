# backend/models/document_comparison.py
import difflib
import re
from typing import Dict, List, Any, Tuple
import google.generativeai as genai
import json


class DocumentComparator:
    """Compare two legal documents and identify key differences"""

    def __init__(self, gemini_model):
        self.gemini_model = gemini_model

    def extract_sections(self, text: str) -> Dict[str, str]:
        """Extract sections from a legal document based on headings"""
        sections = {}
        # Simple regex to identify common section patterns in legal docs
        section_pattern = re.compile(
            r"(?:^|\n)(?:[IVX]+\.|[0-9]+\.|[A-Z][A-Za-z\s]+:|\([a-z]\))"
        )
        
        # Find all potential section starts
        matches = list(section_pattern.finditer(text))
        
        # Process each section
        for i in range(len(matches)):
            # Get section name
            start = matches[i].start()
            end = matches[i].end()
            section_name = text[start:end].strip()
            
            # Get section content (up to next section or end)
            content_start = end
            content_end = matches[i + 1].start() if i < len(matches) - 1 else len(text)
            section_content = text[content_start:content_end].strip()
            
            sections[section_name] = section_content
            
        return sections

    def compare_text_sections(
        self, doc1_sections: Dict[str, str], doc2_sections: Dict[str, str]
    ) -> List[Dict[str, Any]]:
        """
        Compare sections between two documents
        Return a list of differences with section name and change type
        """
        differences = []
        
        # Find sections that exist in both documents
        common_sections = set(doc1_sections.keys()) & set(doc2_sections.keys())
        only_in_doc1 = set(doc1_sections.keys()) - set(doc2_sections.keys())
        only_in_doc2 = set(doc2_sections.keys()) - set(doc1_sections.keys())
        
        # Add sections that only exist in doc1
        for section in only_in_doc1:
            differences.append({
                "section": section,
                "change_type": "removed",
                "text": doc1_sections[section]
            })
            
        # Add sections that only exist in doc2
        for section in only_in_doc2:
            differences.append({
                "section": section,
                "change_type": "added",
                "text": doc2_sections[section]
            })
            
        # Compare text in common sections
        for section in common_sections:
            text1 = doc1_sections[section]
            text2 = doc2_sections[section]
            
            if text1 != text2:
                # Use difflib to identify specific changes
                diff = list(difflib.ndiff(text1.splitlines(), text2.splitlines()))
                
                differences.append({
                    "section": section,
                    "change_type": "modified",
                    "from_text": text1,
                    "to_text": text2,
                    "diff": diff
                })
                
        return differences

    async def analyze_differences(
        self, doc1_text: str, doc2_text: str
    ) -> Dict[str, Any]:
        """
        Analyze differences between two legal documents
        Returns the analysis including significant changes and implications
        """
        # Extract sections
        doc1_sections = self.extract_sections(doc1_text)
        doc2_sections = self.extract_sections(doc2_text)
        
        # Get technical differences 
        diff_details = self.compare_text_sections(doc1_sections, doc2_sections)
        
        # Use Gemini to analyze the implications of the changes
        if diff_details:
            # Prepare prompt for the model
            prompt = f"""
            Analyze the following differences between two legal documents:
            
            {json.dumps(diff_details, indent=2)}
            
            Please provide:
            1. A summary of the most significant changes
            2. The legal implications of these changes
            3. Any recommendations to consider
            
            Format your response as JSON with keys: 'significant_changes', 'legal_implications', and 'recommendations'.
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
                        "significant_changes": "Unable to parse model output as JSON. See raw analysis.",
                        "legal_implications": "",
                        "recommendations": "",
                        "raw_analysis": analysis
                    }
                    
                return {
                    "success": True,
                    "diff_details": diff_details,
                    "analysis": analysis_json,
                    "model": "gemini-1.5-pro"
                }
                
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "diff_details": diff_details,
                }
        
        return {
            "success": True,
            "message": "No significant differences found between documents.",
            "diff_details": [],
        } 