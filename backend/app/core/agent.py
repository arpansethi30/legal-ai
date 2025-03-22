import asyncio
import json
from typing import Dict, List, Any, Optional
from enum import Enum
from app.core.llm import get_llm_response
from app.services.langtrace import trace_function

class AgentAction(Enum):
    ANALYZE_TEXT = "analyze_text"
    DRAFT_CONTRACT = "draft_contract"
    IDENTIFY_RISKS = "identify_risks"
    SUGGEST_TERMS = "suggest_terms"
    MEDIATE_DISPUTE = "mediate_dispute"
    ASK_QUESTION = "ask_question"

class LegalAgent:
    """
    Advanced legal AI agent with multi-step reasoning, planning, and execution
    """
    
    def __init__(self):
        self.conversation_history = []
        self.working_memory = {}
        self.action_history = []
    
    @trace_function(tags=["agent", "planning"])
    async def plan(self, task: str) -> List[Dict[str, Any]]:
        """
        Generate a plan to solve a complex legal task
        """
        prompt = f"""
        You are a legal AI agent tasked with: {task}
        
        Create a step-by-step plan to solve this task. Each step should include:
        1. The action to take (one of: analyze_text, draft_contract, identify_risks, suggest_terms, mediate_dispute, ask_question)
        2. The input for that action
        3. The expected output
        
        Format your response as a JSON array of steps.
        """
        
        response = await get_llm_response(prompt)
        
        try:
            plan = json.loads(response)
            return plan
        except json.JSONDecodeError:
            # Fallback planning with basic steps
            return [
                {
                    "action": "analyze_text",
                    "input": task,
                    "expected_output": "Understanding of the request"
                },
                {
                    "action": "draft_contract",
                    "input": "Based on the analysis",
                    "expected_output": "Initial contract draft"
                }
            ]
    
    @trace_function(tags=["agent", "execution"])
    async def execute_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a single step in the plan
        """
        action = step.get("action")
        action_input = step.get("input")
        
        if action == AgentAction.ANALYZE_TEXT.value:
            result = await self._analyze_text(action_input)
        elif action == AgentAction.DRAFT_CONTRACT.value:
            result = await self._draft_contract(action_input)
        elif action == AgentAction.IDENTIFY_RISKS.value:
            result = await self._identify_risks(action_input)
        elif action == AgentAction.SUGGEST_TERMS.value:
            result = await self._suggest_terms(action_input)
        elif action == AgentAction.MEDIATE_DISPUTE.value:
            result = await self._mediate_dispute(action_input)
        elif action == AgentAction.ASK_QUESTION.value:
            result = await self._formulate_question(action_input)
        else:
            result = {"error": f"Unknown action: {action}"}
        
        # Store in action history
        self.action_history.append({
            "step": step,
            "result": result
        })
        
        return result
    
    async def _analyze_text(self, text: str) -> Dict[str, Any]:
        """
        Analyze legal text to extract key information
        """
        prompt = f"""
        Analyze this legal text thoroughly:
        
        {text}
        
        Provide a comprehensive analysis including:
        1. Key parties and entities
        2. Legal obligations (must, shall, required to)
        3. Permissions and rights (may, can, allowed to)
        4. Timeframes and deadlines
        5. Conditions and contingencies
        6. Potential ambiguities or vague language
        
        Format as JSON with these categories as keys.
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
            
            # Return structured but basic response
            return {
                "key_parties": ["Unknown"],
                "legal_obligations": ["Could not extract"],
                "permissions": ["Could not extract"],
                "timeframes": ["Could not extract"],
                "conditions": ["Could not extract"],
                "ambiguities": ["Text could not be fully analyzed"]
            }
    
    async def _draft_contract(self, requirements: str) -> Dict[str, Any]:
        """
        Draft a contract based on requirements
        """
        prompt = f"""
        Draft a comprehensive legal contract based on these requirements:
        
        {requirements}
        
        The contract should include:
        1. Introduction and parties
        2. Definitions of key terms
        3. Scope of work/services/agreement
        4. Payment terms and schedule
        5. Term and termination
        6. Confidentiality
        7. Intellectual property
        8. Warranties and representations
        9. Limitation of liability
        10. Governing law and jurisdiction
        11. Miscellaneous/general provisions
        
        Return the contract as a string in valid legal format.
        """
        
        contract_text = await get_llm_response(prompt)
        
        return {
            "contract_text": contract_text,
            "sections": contract_text.split("\n\n"),
            "word_count": len(contract_text.split())
        }
    
    async def _identify_risks(self, contract_text: str) -> Dict[str, Any]:
        """
        Identify legal risks in a contract
        """
        prompt = f"""
        Analyze this contract for legal risks:
        
        {contract_text}
        
        For each identified risk:
        1. Quote the specific clause (brief quote only)
        2. Explain the potential issue
        3. Rate the severity (Low, Medium, High)
        4. Suggest an improvement
        
        Format as a JSON array of risk objects.
        """
        
        response = await get_llm_response(prompt)
        
        try:
            risks = json.loads(response)
            return {"risks": risks}
        except json.JSONDecodeError:
            # Try to extract a JSON array
            try:
                start = response.find('[')
                end = response.rfind(']') + 1
                if start >= 0 and end > 0:
                    json_str = response[start:end]
                    risks = json.loads(json_str)
                    return {"risks": risks}
            except:
                pass
            
            # Return basic structure
            return {
                "risks": [
                    {
                        "clause": "Could not extract specific clauses",
                        "issue": "Unable to parse contract",
                        "severity": "Unknown",
                        "improvement": "Have contract reviewed manually by legal counsel"
                    }
                ]
            }
    
    async def _suggest_terms(self, context: str) -> Dict[str, Any]:
        """
        Suggest fair and balanced terms for a negotiation
        """
        prompt = f"""
        Based on this negotiation context:
        
        {context}
        
        Suggest balanced terms that would be fair to all parties, including:
        1. Key contract terms
        2. Balanced obligations
        3. Fair compensation
        4. Reasonable timeframes
        5. Appropriate risk allocation
        
        Explain the rationale for each suggestion.
        Format as a JSON object with these categories as keys.
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
                    json_str = response[start:end]
                    return json.loads(json_str)
            except:
                pass
            
            # Return structured fallback
            return {
                "key_contract_terms": ["Could not generate suggestions"],
                "balanced_obligations": ["Could not generate suggestions"],
                "fair_compensation": ["Could not generate suggestions"],
                "reasonable_timeframes": ["Could not generate suggestions"],
                "appropriate_risk_allocation": ["Could not generate suggestions"]
            }
    
    async def _mediate_dispute(self, dispute_context: str) -> Dict[str, Any]:
        """
        Generate mediation suggestions for a legal dispute
        """
        prompt = f"""
        You're mediating this legal dispute:
        
        {dispute_context}
        
        Provide mediation suggestions including:
        1. Summary of each party's position
        2. Underlying interests of each party
        3. Common ground and shared interests
        4. Potential compromise solutions
        5. Next steps for resolution
        
        Format as a JSON object with these categories as keys.
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
            
            # Return structured fallback
            return {
                "party_positions": ["Could not analyze positions"],
                "underlying_interests": ["Could not identify interests"],
                "common_ground": ["Could not find common ground"],
                "compromise_solutions": ["No suggestions available"],
                "next_steps": ["Seek professional legal mediation"]
            }
    
    async def _formulate_question(self, context: str) -> Dict[str, Any]:
        """
        Formulate clarifying questions to gather missing information
        """
        prompt = f"""
        Based on this context:
        
        {context}
        
        Identify what critical information is missing and formulate specific, 
        clear questions to gather that information. 
        
        Format as a JSON array of question objects, each with:
        1. "question": The specific question to ask
        2. "purpose": Why this information is needed
        3. "impact": How it will affect the legal analysis or document
        """
        
        response = await get_llm_response(prompt)
        
        try:
            questions = json.loads(response)
            return {"questions": questions}
        except json.JSONDecodeError:
            # Try to extract JSON array
            try:
                start = response.find('[')
                end = response.rfind(']') + 1
                if start >= 0 and end > 0:
                    json_str = response[start:end]
                    questions = json.loads(json_str)
                    return {"questions": questions}
            except:
                pass
            
            # Return structured fallback
            return {
                "questions": [
                    {
                        "question": "What are the parties involved in this agreement?",
                        "purpose": "To identify the legal entities entering the contract",
                        "impact": "Defines who holds rights and obligations"
                    },
                    {
                        "question": "What is the scope of services or products being exchanged?",
                        "purpose": "To clarify what exactly is being provided",
                        "impact": "Determines core obligations and deliverables"
                    }
                ]
            }
    
    @trace_function(tags=["agent", "execution"])
    async def execute_task(self, task: str) -> Dict[str, Any]:
        """
        Execute a complete legal task with planning and step-by-step execution
        """
        # Generate plan
        plan = await self.plan(task)
        
        # Store in working memory
        self.working_memory["plan"] = plan
        self.working_memory["task"] = task
        self.working_memory["results"] = []
        
        # Execute each step
        for step in plan:
            result = await self.execute_step(step)
            self.working_memory["results"].append(result)
        
        # Synthesize results
        synthesis = await self._synthesize_results()
        
        return {
            "task": task,
            "plan": plan,
            "results": self.working_memory["results"],
            "synthesis": synthesis
        }
    
    async def _synthesize_results(self) -> Dict[str, Any]:
        """
        Synthesize the results of all steps into a final output
        """
        prompt = f"""
        Synthesize these results into a cohesive final output:
        
        Task: {self.working_memory.get("task")}
        
        Results:
        {json.dumps(self.working_memory.get("results"), indent=2)}
        
        Provide a comprehensive synthesis with:
        1. Executive summary
        2. Key findings
        3. Recommendations
        4. Next steps
        
        Format as a JSON object with these sections as keys.
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
            
            # Return structured fallback
            return {
                "executive_summary": "Synthesis could not be generated",
                "key_findings": ["Results processing failed"],
                "recommendations": ["Manual review recommended"],
                "next_steps": ["Consult with legal professional"]
            }
async def _deliberate(self, question: str, context: str = "") -> Dict[str, Any]:
    """
    Perform structured legal reasoning with explicit steps
    """
    prompt = f"""
    Legal Question: {question}
    
    Context: {context}
    
    Please think through this legal question using the following structured approach:
    
    1. Initial Assessment:
       - Identify the legal domains involved (contract law, IP, employment, etc.)
       - Clarify the key legal questions at issue
    
    2. Legal Analysis:
       - Identify applicable legal principles and standards
       - Consider precedents and common practices
       - Evaluate potential interpretations
    
    3. Party Interest Analysis:
       - Consider each party's legitimate interests
       - Identify potential conflicts of interest
       - Evaluate power imbalances
    
    4. Risk Assessment:
       - Identify potential legal risks
       - Evaluate potential financial impacts
       - Consider reputational implications
    
    5. Solution Development:
       - Generate multiple potential solutions
       - Evaluate each solution against legal standards
       - Consider practical implementation challenges
    
    6. Final Recommendation:
       - Provide clear, actionable recommendation
       - Justify with legal reasoning
       - Note any important caveats or limitations
    
    Provide your reasoning in a detailed, structured JSON format with each of these 6 steps as keys,
    and each containing the relevant sub-points.
    """
    
    response = await get_llm_response(prompt)
    
    try:
        # Try to parse as JSON
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
        
        # If all else fails, return structured but empty response
        return {
            "Initial_Assessment": {"domains": [], "key_questions": []},
            "Legal_Analysis": {"principles": [], "interpretations": []},
            "Party_Interest_Analysis": {"interests": [], "conflicts": []},
            "Risk_Assessment": {"legal_risks": [], "financial_impacts": []},
            "Solution_Development": {"solutions": [], "evaluations": []},
            "Final_Recommendation": {"recommendation": "", "justification": "", "caveats": []}
        }