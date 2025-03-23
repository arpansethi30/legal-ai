import asyncio
import json
from typing import Dict, List, Any, Optional
from enum import Enum
from app.core.llm import get_llm_response
from app.services.langtrace import trace_function

class AgentRole(Enum):
    """Specialized legal agent roles in a multi-agent system"""
    DRAFTER = "Contract Drafter"
    ANALYZER = "Risk Analyzer"
    ADVOCATE = "Client Advocate"
    OPPONENT = "Opposition Advocate"
    MEDIATOR = "Neutral Mediator"
    JUDGE = "Legal Evaluator"

class LegalMultiAgentSystem:
    """
    Advanced multi-agent system where specialized legal agents debate and collaborate
    """
    
    def __init__(self):
        self.conversation = []
        self.conclusions = {}
        self.trace_id = None
    
    @trace_function(tags=["multi-agent", "deliberation"])
    async def deliberate(self, legal_question: str, context: str, rounds: int = 3) -> Dict[str, Any]:
        """
        Conduct a multi-agent deliberation on a legal question
        """
        # Initialize the conversation with the question
        self.conversation = [{
            "role": "SYSTEM",
            "content": f"LEGAL QUESTION: {legal_question}\n\nCONTEXT: {context}"
        }]
        
        # First, have each agent provide their initial analysis
        for agent_role in [AgentRole.DRAFTER, AgentRole.ANALYZER, AgentRole.ADVOCATE, AgentRole.OPPONENT]:
            analysis = await self._get_agent_analysis(agent_role, legal_question, context)
            
            self.conversation.append({
                "role": agent_role.value,
                "content": analysis
            })
        
        # Conduct deliberation rounds
        for round_num in range(rounds):
            # Mediator summarizes current positions
            if round_num > 0:  # Only after first round of statements
                summary = await self._get_mediator_summary()
                self.conversation.append({
                    "role": AgentRole.MEDIATOR.value,
                    "content": summary
                })
            
            # Each agent responds to others' points
            for agent_role in [AgentRole.ADVOCATE, AgentRole.OPPONENT, AgentRole.DRAFTER, AgentRole.ANALYZER]:
                response = await self._get_agent_response(agent_role)
                self.conversation.append({
                    "role": agent_role.value,
                    "content": response
                })
        
        # Final evaluation from judge
        evaluation = await self._get_judge_evaluation()
        self.conversation.append({
            "role": AgentRole.JUDGE.value,
            "content": evaluation
        })
        
        # Extract conclusions
        conclusions = await self._extract_conclusions()
        
        return {
            "conversation": self.conversation,
            "conclusions": conclusions,
            "trace_id": self.trace_id
        }
    
    async def _get_agent_analysis(self, agent_role: AgentRole, question: str, context: str) -> str:
        """Get initial analysis from an agent"""
        
        prompts = {
            AgentRole.DRAFTER: f"""
                As an expert legal document drafter, provide your initial analysis of this legal question:
                
                QUESTION: {question}
                
                CONTEXT: {context}
                
                Focus on clear language, proper structure, and standard legal provisions.
                Identify the key elements that should be addressed in any legal document for this situation.
                """,
                
            AgentRole.ANALYZER: f"""
                As a risk analysis specialist, provide your initial analysis of this legal question:
                
                QUESTION: {question}
                
                CONTEXT: {context}
                
                Focus on identifying potential risks, ambiguities, and enforcement issues.
                Highlight any regulatory concerns or compliance requirements.
                """,
                
            AgentRole.ADVOCATE: f"""
                As an advocate for the primary party in this matter, provide your initial analysis of this legal question:
                
                QUESTION: {question}
                
                CONTEXT: {context}
                
                Focus on protecting your client's interests, ensuring favorable terms, and minimizing obligations.
                Identify positions that would be most advantageous to your client.
                """,
                
            AgentRole.OPPONENT: f"""
                As an advocate for the counterparty in this matter, provide your initial analysis of this legal question:
                
                QUESTION: {question}
                
                CONTEXT: {context}
                
                Focus on protecting your client's interests, ensuring balanced terms, and addressing concerns.
                Challenge any one-sided or unfair provisions from your client's perspective.
                """
        }
        
        prompt = prompts.get(agent_role, "Provide your analysis of the legal question.")
        return await get_llm_response(prompt)
    
    async def _get_agent_response(self, agent_role: AgentRole) -> str:
        """Get a response from an agent based on the conversation history"""
        
        # Format conversation history
        conversation_text = "\n\n".join([
            f"{entry['role']}: {entry['content']}"
            for entry in self.conversation[-4:]  # Include only recent messages for context
        ])
        
        prompts = {
            AgentRole.DRAFTER: f"""
                As an expert legal document drafter, review the discussion so far:
                
                {conversation_text}
                
                Respond to the points raised, focusing on how the document structure and language 
                could address the concerns raised. Suggest specific clause wording where appropriate.
                """,
                
            AgentRole.ANALYZER: f"""
                As a risk analysis specialist, review the discussion so far:
                
                {conversation_text}
                
                Identify any new risks or issues raised in the discussion. Evaluate the suggestions
                made by others from a risk perspective. Propose risk mitigation strategies.
                """,
                
            AgentRole.ADVOCATE: f"""
                As an advocate for the primary party, review the discussion so far:
                
                {conversation_text}
                
                Respond to the points made by others, particularly the opposing advocate.
                Defend your client's interests and propose terms that balance client protection
                with agreement viability.
                """,
                
            AgentRole.OPPONENT: f"""
                As an advocate for the counterparty, review the discussion so far:
                
                {conversation_text}
                
                Challenge any unfair positions, respond to the main advocate's arguments,
                and propose alternative terms that would be more acceptable to your client
                while still allowing the agreement to proceed.
                """
        }
        
        prompt = prompts.get(agent_role, "Provide your response to the discussion.")
        return await get_llm_response(prompt)
    
    async def _get_mediator_summary(self) -> str:
        """Get a summary from the mediator"""
        
        # Format conversation history
        conversation_text = "\n\n".join([
            f"{entry['role']}: {entry['content']}"
            for entry in self.conversation
        ])
        
        prompt = f"""
            As a neutral legal mediator, summarize the current state of the discussion:
            
            {conversation_text}
            
            Identify:
            1. Points of agreement between the parties
            2. Key areas of disagreement
            3. Potential compromise positions
            
            Suggest a path forward for the deliberation that addresses the core concerns
            while moving toward consensus.
        """
        
        return await get_llm_response(prompt)
    
    async def _get_judge_evaluation(self) -> str:
        """Get a final evaluation from the judge"""
        
        # Format conversation history
        conversation_text = "\n\n".join([
            f"{entry['role']}: {entry['content']}"
            for entry in self.conversation
        ])
        
        prompt = f"""
            As a judicial evaluator, review the entire deliberation and provide your final assessment:
            
            {conversation_text}
            
            Provide:
            1. An evaluation of the strongest legal arguments presented
            2. A determination of the most balanced and legally sound position
            3. Specific recommendations for resolving the legal question
            4. Identification of any legal principles or precedents that should guide the final outcome
            
            Format your response to clearly separate these four sections.
        """
        
        return await get_llm_response(prompt)
    
    async def _extract_conclusions(self) -> Dict[str, Any]:
        """Extract structured conclusions from the deliberation"""
        
        # Get the judge's evaluation
        judge_content = ""
        for entry in reversed(self.conversation):
            if entry["role"] == AgentRole.JUDGE.value:
                judge_content = entry["content"]
                break
        
        prompt = f"""
            Based on this judicial evaluation from a legal deliberation:
            
            {judge_content}
            
            Extract the following information in JSON format:
            1. "key_findings": The main legal findings (array)
            2. "recommended_position": The recommended legal position (string)
            3. "action_items": Specific actions to implement (array)
            4. "guiding_principles": Legal principles that should be followed (array)
            
            Return only the JSON object.
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
            
            # Return basic structure if parsing fails
            return {
                "key_findings": ["Could not extract findings"],
                "recommended_position": "Could not determine recommended position",
                "action_items": ["Consult with legal counsel"],
                "guiding_principles": ["Standard legal principles apply"]
            }