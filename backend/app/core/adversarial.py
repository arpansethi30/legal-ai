import asyncio
import json
from typing import Dict, List, Any, Optional
from app.core.llm import get_llm_response
from app.services.langtrace import trace_function

class AdversarialTester:
    """
    Adversarial testing system that tries to find weaknesses in contracts
    """
    
    @staticmethod
    @trace_function(tags=["adversarial", "testing"])
    async def find_weaknesses(contract_text: str, perspective: str = "neutral") -> Dict[str, Any]:
        """
        Try to find weaknesses, loopholes, and exploitable ambiguities in a contract
        """
        
        # Generate different perspectives for testing
        perspectives = {
            "neutral": "Analyze this contract objectively to identify any potential weaknesses",
            "aggressive": "You represent a party looking to exploit any possible loophole or ambiguity in this contract",
            "defensive": "You represent a party concerned about protecting themselves from potential contract issues",
            "judge": "You are a judge evaluating this contract for potential issues that could lead to litigation"
        }
        
        perspective_prompt = perspectives.get(perspective, perspectives["neutral"])
        
        prompt = f"""
            {perspective_prompt}. The contract is as follows:
            
            {contract_text}
            
            Identify:
            1. Loopholes that could be exploited
            2. Ambiguous language that could be interpreted differently than intended
            3. Missing clauses or protections that should be present
            4. Conflicting provisions that create uncertainty
            5. Strategic weaknesses that put one party at a disadvantage
            
            For each issue found, explain:
            - The specific problematic language (quote briefly)
            - Why it's a problem
            - How it could be exploited or lead to issues
            - A suggested fix
            
            Format as a JSON array of issues, each with these four elements.
        """
        
        response = await get_llm_response(prompt)
        
        try:
            issues = json.loads(response)
            return {"issues": issues}
        except json.JSONDecodeError:
            # Try to extract a JSON array
            try:
                start = response.find('[')
                end = response.rfind(']') + 1
                if start >= 0 and end > 0:
                    json_str = response[start:end]
                    issues = json.loads(json_str)
                    return {"issues": issues}
            except:
                pass
            
            # Return basic structure if parsing fails
            return {
                "issues": [
                    {
                        "problematic_language": "Could not parse specific issues",
                        "problem": "Analysis failed",
                        "potential_exploitation": "Unknown",
                        "suggested_fix": "Have the contract reviewed manually by legal counsel"
                    }
                ]
            }
    
    @staticmethod
    @trace_function(tags=["adversarial", "simulation"])
    async def simulate_scenarios(contract_text: str, num_scenarios: int = 3) -> Dict[str, Any]:
        """
        Generate and simulate hypothetical scenarios to test contract robustness
        """
        
        # First, generate challenging scenarios
        scenarios_prompt = f"""
            Generate {num_scenarios} challenging but realistic scenarios that could test the boundaries of this contract:
            
            {contract_text}
            
            For each scenario:
            1. Describe a specific situation that might arise
            2. Explain why this situation creates a challenge for the contract
            
            Format as a JSON array of scenarios, each with "situation" and "challenge" properties.
        """
        
        scenarios_response = await get_llm_response(scenarios_prompt)
        
        try:
            scenarios = json.loads(scenarios_response)
        except json.JSONDecodeError:
            # Try to extract a JSON array
            try:
                start = scenarios_response.find('[')
                end = scenarios_response.rfind(']') + 1
                if start >= 0 and end > 0:
                    json_str = scenarios_response[start:end]
                    scenarios = json.loads(json_str)
            except:
                # Create default scenarios if parsing fails
                scenarios = [
                    {
                        "situation": "A force majeure event occurs",
                        "challenge": "Determining whether the event qualifies and what obligations are suspended"
                    },
                    {
                        "situation": "One party fails to meet a deadline",
                        "challenge": "Determining the consequences and remedies available"
                    },
                    {
                        "situation": "A dispute arises over quality of deliverables",
                        "challenge": "Resolving ambiguity in quality standards and acceptance criteria"
                    }
                ]
        
        # Now analyze each scenario
        results = []
        for scenario in scenarios:
            analysis_prompt = f"""
                Analyze how this contract would handle the following scenario:
                
                SCENARIO: {scenario.get('situation')}
                CHALLENGE: {scenario.get('challenge')}
                
                CONTRACT:
                {contract_text}
                
                Provide:
                1. The relevant contract provisions that would apply
                2. How the contract would likely be interpreted in this scenario
                3. Any ambiguities or gaps in the contract regarding this scenario
                4. The likely outcome or resolution
                
                Format as a JSON object with these four properties.
            """
            
            analysis_response = await get_llm_response(analysis_prompt)
            
            try:
                analysis = json.loads(analysis_response)
            except json.JSONDecodeError:
                # Try to extract JSON
                try:
                    start = analysis_response.find('{')
                    end = analysis_response.rfind('}') + 1
                    if start >= 0 and end > 0:
                        json_str = analysis_response[start:end]
                        analysis = json.loads(json_str)
                except:
                    # Create basic analysis if parsing fails
                    analysis = {
                        "relevant_provisions": ["Could not identify specific provisions"],
                        "interpretation": "Could not determine interpretation",
                        "ambiguities": ["Analysis failed"],
                        "likely_outcome": "Could not predict outcome"
                    }
            
            results.append({
                "scenario": scenario,
                "analysis": analysis
            })
        
        return {"simulation_results": results}