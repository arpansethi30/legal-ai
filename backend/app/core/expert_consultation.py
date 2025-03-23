import asyncio
import json
from typing import Dict, List, Any, Optional
from enum import Enum
from app.core.llm import get_llm_response
from app.services.langtrace import trace_function

class LegalExpertise(Enum):
    """Areas of legal specialization"""
    CONTRACT_LAW = "Contract Law Expert"
    INTELLECTUAL_PROPERTY = "Intellectual Property Expert"
    EMPLOYMENT_LAW = "Employment Law Expert"
    CORPORATE_LAW = "Corporate Law Expert"
    REGULATORY_COMPLIANCE = "Regulatory Compliance Expert"
    LITIGATION = "Litigation Expert"
    TRANSACTION = "Transactional Expert"
    TAX_LAW = "Tax Law Expert"
    INTERNATIONAL_LAW = "International Law Expert"

class ExpertConsultationSystem:
    """
    System for simulating expert consultation on complex legal matters
    """
    
    @staticmethod
    @trace_function(tags=["expert_consultation"])
    async def consult_experts(question: str, document: str, experts: List[str] = None) -> Dict[str, Any]:
        """
        Consult multiple specialized experts on a legal question
        """
        # Default to a standard set of experts if none specified
        if not experts:
            experts = [
                LegalExpertise.CONTRACT_LAW.value,
                LegalExpertise.LITIGATION.value,
                LegalExpertise.REGULATORY_COMPLIANCE.value
            ]
        
        # Get consultation from each expert
        consultations = {}
        
        for expert in experts:
            consultation = await ExpertConsultationSystem._get_expert_opinion(
                expert=expert,
                question=question,
                document=document
            )
            consultations[expert] = consultation
        
        # Synthesize expert opinions
        synthesis = await ExpertConsultationSystem._synthesize_opinions(
            question=question,
            consultations=consultations
        )
        
        return {
            "question": question,
            "document_preview": document[:100] + "...",
            "expert_consultations": consultations,
            "synthesis": synthesis,
            "experts_consulted": experts
        }
    
    @staticmethod
    async def _get_expert_opinion(expert: str, question: str, document: str) -> Dict[str, Any]:
        """Get opinion from a specific type of legal expert"""
        
        # Expert-specific prompts
        prompts = {
            LegalExpertise.CONTRACT_LAW.value: f"""
                As a contract law expert with 20+ years of experience, analyze this legal question:
                
                QUESTION: {question}
                
                DOCUMENT: {document[:2000]}...
                
                Provide your expert analysis focusing on:
                - Contract formation issues
                - Interpretation principles
                - Enforceability concerns
                - Risk allocation analysis
                - Standard industry practices
                
                Format your response as a formal expert consultation with:
                1. Initial assessment
                2. Detailed analysis with specific contract law principles
                3. Practical recommendations
                4. Areas requiring further investigation
                
                Structure as a JSON object with these four properties.
            """,
            
            LegalExpertise.INTELLECTUAL_PROPERTY.value: f"""
                As an intellectual property expert with 20+ years of experience, analyze this legal question:
                
                QUESTION: {question}
                
                DOCUMENT: {document[:2000]}...
                
                Provide your expert analysis focusing on:
                - IP ownership and assignment issues
                - Licensing considerations
                - Infringement risks
                - IP protection strategies
                - Industry-standard IP clauses
                
                Format your response as a formal expert consultation with:
                1. Initial assessment
                2. Detailed analysis with specific IP law principles
                3. Practical recommendations
                4. Areas requiring further investigation
                
                Structure as a JSON object with these four properties.
            """,
            
            LegalExpertise.EMPLOYMENT_LAW.value: f"""
                As an employment law expert with 20+ years of experience, analyze this legal question:
                
                QUESTION: {question}
                
                DOCUMENT: {document[:2000]}...
                
                Provide your expert analysis focusing on:
                - Employment classification issues
                - Compliance with labor laws
                - Discrimination/harassment concerns
                - Employee rights and protections
                - Standard employment practices
                
                Format your response as a formal expert consultation with:
                1. Initial assessment
                2. Detailed analysis with specific employment law principles
                3. Practical recommendations
                4. Areas requiring further investigation
                
                Structure as a JSON object with these four properties.
            """,
            
            LegalExpertise.LITIGATION.value: f"""
                As a litigation expert with 20+ years of trial experience, analyze this legal question:
                
                QUESTION: {question}
                
                DOCUMENT: {document[:2000]}...
                
                Provide your expert analysis focusing on:
                - Litigation risk assessment
                - Potential causes of action
                - Evidentiary considerations
                - Procedural strategies
                - Settlement possibilities
                
                Format your response as a formal expert consultation with:
                1. Initial assessment
                2. Detailed analysis with specific litigation principles
                3. Practical recommendations
                4. Areas requiring further investigation
                
                Structure as a JSON object with these four properties.
            """,
            
            LegalExpertise.REGULATORY_COMPLIANCE.value: f"""
                As a regulatory compliance expert with 20+ years of experience, analyze this legal question:
                
                QUESTION: {question}
                
                DOCUMENT: {document[:2000]}...
                
                Provide your expert analysis focusing on:
                - Applicable regulatory frameworks
                - Compliance requirements
                - Regulatory risk areas
                - Reporting obligations
                - Industry-standard compliance practices
                
                Format your response as a formal expert consultation with:
                1. Initial assessment
                2. Detailed analysis with specific regulatory principles
                3. Practical recommendations
                4. Areas requiring further investigation
                
                Structure as a JSON object with these four properties.
            """
        }
        
        # Use the appropriate prompt or a default one
        prompt = prompts.get(expert, f"""
            As a legal expert specializing in {expert}, analyze this legal question:
            
            QUESTION: {question}
            
            DOCUMENT: {document[:2000]}...
            
            Provide your expert opinion in a formal consultation format.
            Structure as a JSON object with "initial_assessment", "detailed_analysis", 
            "recommendations", and "further_investigation" properties.
        """)
        
        response = await get_llm_response(prompt)
        
        try:
            opinion = json.loads(response)
            return opinion
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
            
            # Return basic structure if parsing fails
            return {
                "initial_assessment": f"Error processing {expert} consultation",
                "detailed_analysis": ["Analysis failed"],
                "recommendations": ["Consult with a live expert"],
                "further_investigation": ["All aspects require investigation"]
            }
    
    @staticmethod
    async def _synthesize_opinions(question: str, consultations: Dict[str, Any]) -> Dict[str, Any]:
        """
        Synthesize opinions from multiple experts into a unified response
        """
        prompt = f"""
            You are a senior partner at a prestigious law firm. Synthesize these expert consultations into a 
            comprehensive response to the client's question:
            
            QUESTION: {question}
            
            EXPERT CONSULTATIONS:
            {json.dumps(consultations, indent=2)}
            
            Provide:
            1. An executive summary that highlights key points from all experts
            2. Areas of consensus among the experts
            3. Any significant disagreements or different perspectives
            4. Integrated recommendations that balance different considerations
            5. A practical action plan for the client
            
            Format as a JSON object with these five properties.
        """
        
        response = await get_llm_response(prompt)
        
        try:
            synthesis = json.loads(response)
            return synthesis
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
            
            # Return basic structure if parsing fails
            return {
                "executive_summary": "Error synthesizing expert opinions",
                "areas_of_consensus": [],
                "significant_disagreements": [],
                "integrated_recommendations": [],
                "action_plan": ["Consult with legal counsel"]
            }
    
    @staticmethod
    @trace_function(tags=["expert_consultation", "second_opinion"])
    async def get_second_opinion(analysis: Dict[str, Any], document: str) -> Dict[str, Any]:
        """
        Get a second opinion to critique an existing legal analysis
        """
        prompt = f"""
            You are a senior legal expert asked to provide a second opinion on this legal analysis:
            
            ORIGINAL ANALYSIS:
            {json.dumps(analysis, indent=2)}
            
            DOCUMENT: {document[:2000]}...
            
            Provide your second opinion addressing:
            1. Strengths of the original analysis
            2. Weaknesses or oversights in the analysis
            3. Additional considerations or perspectives
            4. Alternative interpretations or approaches
            5. Revised or additional recommendations
            
            Format as a JSON object with these five properties.
        """
        
        response = await get_llm_response(prompt)
        
        try:
            second_opinion = json.loads(response)
            return {
                "original_analysis_preview": str(analysis)[:100] + "...",
                "second_opinion": second_opinion
            }
        except json.JSONDecodeError:
            # Try to extract JSON
            try:
                start = response.find('{')
                end = response.rfind('}') + 1
                if start >= 0 and end > 0:
                    json_str = response[start:end]
                    second_opinion = json.loads(json_str)
                    return {
                        "original_analysis_preview": str(analysis)[:100] + "...",
                        "second_opinion": second_opinion
                    }
            except:
                pass
            
            # Return basic structure if parsing fails
            return {
                "original_analysis_preview": str(analysis)[:100] + "...",
                "second_opinion": {
                    "strengths": ["Unable to assess strengths"],
                    "weaknesses": ["Unable to assess weaknesses"],
                    "additional_considerations": ["Second opinion generation failed"],
                    "alternative_approaches": [],
                    "revised_recommendations": ["Consult with legal counsel"]
                }
            }