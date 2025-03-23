import asyncio
import json
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from app.core.llm import get_llm_response
from app.services.langtrace import trace_function

class ReasoningMethod(Enum):
    """Legal reasoning methodologies"""
    CASE_BASED = "Case-Based Reasoning"
    STATUTORY = "Statutory Interpretation"
    PRINCIPLES = "Legal Principles Analysis"
    ANALOGICAL = "Analogical Reasoning"
    CONSEQUENTIALIST = "Consequentialist Analysis"
    TEXTUAL = "Textual Analysis"
    INTENTIONALIST = "Intentionalist Analysis"

class LegalReasoner:
    """
    Sophisticated legal reasoning system using multiple legal reasoning methodologies
    with step-by-step thought processes and conclusion confidence
    """
    
    @staticmethod
    @trace_function(tags=["legal_reasoning", "multi_method"])
    async def analyze(legal_text: str, question: str, methods: List[str] = None) -> Dict[str, Any]:
        """
        Analyze a legal question using multiple reasoning methodologies
        """
        # Default to all methods if none specified
        if not methods:
            methods = [method.value for method in ReasoningMethod]
        
        # Perform reasoning using each methodology
        analyses = {}
        confidence_scores = {}
        
        for method in methods:
            analysis, confidence = await LegalReasoner._apply_method(
                method=method,
                legal_text=legal_text,
                question=question
            )
            analyses[method] = analysis
            confidence_scores[method] = confidence
        
        # Synthesize a final answer with meta-reasoning
        synthesis = await LegalReasoner._synthesize_analyses(
            question=question,
            analyses=analyses,
            confidence_scores=confidence_scores
        )
        
        return {
            "question": question,
            "method_analyses": analyses,
            "confidence_scores": confidence_scores,
            "synthesis": synthesis,
            "methodologies_used": methods
        }
    
    @staticmethod
    async def _apply_method(method: str, legal_text: str, question: str) -> Tuple[Dict[str, Any], float]:
        """Apply a specific legal reasoning methodology"""
        
        # Method-specific prompts
        prompts = {
            ReasoningMethod.CASE_BASED.value: f"""
                Apply case-based legal reasoning to answer this question:
                
                QUESTION: {question}
                
                LEGAL TEXT: {legal_text}
                
                Follow these steps:
                1. Identify relevant precedents or similar cases
                2. Extract key principles from those cases
                3. Compare the current facts to precedent cases
                4. Determine how the precedents apply to this situation
                5. Reach a conclusion based on the precedential analysis
                
                For each step, show your reasoning in detail. Then provide:
                - Your final conclusion
                - A confidence score (0-100) with explanation
                
                Format as a JSON object with "reasoning_steps", "conclusion", and "confidence" properties.
            """,
            
            ReasoningMethod.STATUTORY.value: f"""
                Apply statutory interpretation to answer this question:
                
                QUESTION: {question}
                
                LEGAL TEXT: {legal_text}
                
                Follow these steps:
                1. Identify the relevant statutory provisions
                2. Analyze the plain meaning of the text
                3. Consider the legislative intent if ambiguous
                4. Apply any relevant canons of construction
                5. Interpret the statute in light of the specific facts
                
                For each step, show your reasoning in detail. Then provide:
                - Your final conclusion
                - A confidence score (0-100) with explanation
                
                Format as a JSON object with "reasoning_steps", "conclusion", and "confidence" properties.
            """,
            
            ReasoningMethod.PRINCIPLES.value: f"""
                Apply legal principles analysis to answer this question:
                
                QUESTION: {question}
                
                LEGAL TEXT: {legal_text}
                
                Follow these steps:
                1. Identify fundamental legal principles at play
                2. Determine how these principles apply
                3. Balance competing principles if necessary
                4. Evaluate how principles align with justice and fairness
                5. Apply principles to reach a conclusion
                
                For each step, show your reasoning in detail. Then provide:
                - Your final conclusion
                - A confidence score (0-100) with explanation
                
                Format as a JSON object with "reasoning_steps", "conclusion", and "confidence" properties.
            """,
            
            ReasoningMethod.ANALOGICAL.value: f"""
                Apply analogical reasoning to answer this question:
                
                QUESTION: {question}
                
                LEGAL TEXT: {legal_text}
                
                Follow these steps:
                1. Identify relevant analogies to this situation
                2. Evaluate similarities and differences
                3. Determine if similarities warrant the same treatment
                4. Consider counteranalogies
                5. Draw a conclusion from the analogical analysis
                
                For each step, show your reasoning in detail. Then provide:
                - Your final conclusion
                - A confidence score (0-100) with explanation
                
                Format as a JSON object with "reasoning_steps", "conclusion", and "confidence" properties.
            """,
            
            ReasoningMethod.CONSEQUENTIALIST.value: f"""
                Apply consequentialist legal analysis to answer this question:
                
                QUESTION: {question}
                
                LEGAL TEXT: {legal_text}
                
                Follow these steps:
                1. Identify possible interpretations or outcomes
                2. Evaluate consequences of each interpretation
                3. Consider impacts on stakeholders and society
                4. Assess alignment with legal system goals
                5. Choose interpretation with best consequences
                
                For each step, show your reasoning in detail. Then provide:
                - Your final conclusion
                - A confidence score (0-100) with explanation
                
                Format as a JSON object with "reasoning_steps", "conclusion", and "confidence" properties.
            """,
            
            ReasoningMethod.TEXTUAL.value: f"""
                Apply textual analysis to answer this question:
                
                QUESTION: {question}
                
                LEGAL TEXT: {legal_text}
                
                Follow these steps:
                1. Parse the specific language used
                2. Analyze syntax, grammar, and word choice
                3. Identify any ambiguities or inconsistencies
                4. Determine the most natural reading
                5. Draw conclusions from the textual analysis
                
                For each step, show your reasoning in detail. Then provide:
                - Your final conclusion
                - A confidence score (0-100) with explanation
                
                Format as a JSON object with "reasoning_steps", "conclusion", and "confidence" properties.
            """,
            
            ReasoningMethod.INTENTIONALIST.value: f"""
                Apply intentionalist analysis to answer this question:
                
                QUESTION: {question}
                
                LEGAL TEXT: {legal_text}
                
                Follow these steps:
                1. Identify the likely intention behind the text
                2. Consider context and purpose
                3. Evaluate which interpretation best fulfills the intent
                4. Address any conflicts between text and intent
                5. Reach a conclusion based on the intended meaning
                
                For each step, show your reasoning in detail. Then provide:
                - Your final conclusion
                - A confidence score (0-100) with explanation
                
                Format as a JSON object with "reasoning_steps", "conclusion", and "confidence" properties.
            """
        }
        
        # Use the appropriate prompt or a default one
        prompt = prompts.get(method, f"""
            Apply legal reasoning to answer this question:
            
            QUESTION: {question}
            
            LEGAL TEXT: {legal_text}
            
            Provide detailed step-by-step reasoning, a conclusion, and a confidence score (0-100).
            Format as a JSON object with "reasoning_steps", "conclusion", and "confidence" properties.
        """)
        
        response = await get_llm_response(prompt)
        
        try:
            result = json.loads(response)
            confidence = float(result.get("confidence", 50)) / 100.0  # Normalize to 0-1
            return result, confidence
        except json.JSONDecodeError:
            # Try to extract JSON
            try:
                start = response.find('{')
                end = response.rfind('}') + 1
                if start >= 0 and end > 0:
                    json_str = response[start:end]
                    result = json.loads(json_str)
                    confidence = float(result.get("confidence", 50)) / 100.0
                    return result, confidence
            except:
                pass
            
            # Return fallback if parsing fails
            return {
                "reasoning_steps": ["Could not parse reasoning steps"],
                "conclusion": "Analysis failed for this method",
                "confidence": 0
            }, 0.0
    
    @staticmethod
    async def _synthesize_analyses(question: str, analyses: Dict[str, Any], confidence_scores: Dict[str, float]) -> Dict[str, Any]:
        """
        Synthesize insights from multiple reasoning methods into a final answer
        """
        prompt = f"""
            You are a meta-legal reasoner tasked with synthesizing analyses from multiple legal reasoning methodologies.
            
            QUESTION: {question}
            
            ANALYSES FROM DIFFERENT METHODS:
            {json.dumps(analyses, indent=2)}
            
            CONFIDENCE SCORES:
            {json.dumps(confidence_scores, indent=2)}
            
            Synthesize these analyses into a comprehensive answer. Consider:
            1. Where different methods agree and disagree
            2. The confidence level and reasoning strength of each method
            3. Which methods are most appropriate for this particular question
            4. How to resolve any conflicts between different approaches
            
            Provide:
            - A synthesized answer that draws from the best insights of each method
            - A final confidence score (0-100) with explanation
            - An explanation of which methodologies were most useful and why
            
            Format as a JSON object with these three properties.
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
                    json_str = response[start:end]
                    return json.loads(json_str)
            except:
                pass
            
            # Return fallback if parsing fails
            return {
                "synthesized_answer": "Could not synthesize analyses",
                "final_confidence": 50,
                "methodology_assessment": "Analysis synthesis failed"
            }