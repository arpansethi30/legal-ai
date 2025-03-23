import asyncio
import json
from typing import Dict, List, Any, Optional
from enum import Enum
from app.core.llm import get_llm_response
from app.services.langtrace import trace_function

class ThoughtProcess(Enum):
    """Types of legal thought processes"""
    ISSUE_SPOTTING = "Issue Spotting"
    RISK_ANALYSIS = "Risk Analysis"
    STRATEGY_PLANNING = "Strategy Planning"
    SCENARIO_ANALYSIS = "Scenario Analysis"
    STAKEHOLDER_IMPACT = "Stakeholder Impact Analysis"

class CognitiveSystem:
    """
    Interactive cognitive system that provides visibility into legal reasoning process
    and enables conversational exploration of legal issues
    """
    
    def __init__(self):
        self.context = {}
        self.memory = []
        self.current_focus = None
    
    @trace_function(tags=["cognitive", "issue_spotting"])
    async def identify_issues(self, document: str) -> Dict[str, Any]:
        """
        Identify key legal issues in a document
        """
        prompt = f"""
            Perform comprehensive legal issue spotting on this document:
            
            {document[:3000]}...
            
            Identify all potential legal issues, including:
            1. Explicit issues directly addressed in the document
            2. Implicit issues that may arise from the document
            3. Potential future issues based on the current terms
            4. Stakeholder-specific issues for different parties
            5. Jurisdictional or enforcement issues
            
            For each issue identified, provide:
            - A clear description of the issue
            - The specific text or context that raises the issue
            - Potential implications or consequences
            - Level of seriousness (Critical, Significant, Minor)
            
            Format as a JSON object with "issues" as an array of issue objects.
        """
        
        response = await get_llm_response(prompt)
        
        try:
            result = json.loads(response)
            # Store in context
            self.context["issues"] = result.get("issues", [])
            self.current_focus = "issues"
            # Add to memory
            self.memory.append({
                "action": "identify_issues",
                "result_summary": f"Identified {len(result.get('issues', []))} issues"
            })
            return result
        except json.JSONDecodeError:
            # Try to extract issues array
            try:
                start = response.find('"issues"')
                if start >= 0:
                    array_start = response.find('[', start)
                    array_end = response.rfind(']') + 1
                    if array_start >= 0 and array_end > array_start:
                        issues_str = response[array_start:array_end]
                        issues = json.loads(issues_str)
                        result = {"issues": issues}
                        self.context["issues"] = issues
                        self.current_focus = "issues"
                        self.memory.append({
                            "action": "identify_issues",
                            "result_summary": f"Identified {len(issues)} issues"
                        })
                        return result
            except:
                pass
            
            # Return basic structure if parsing fails
            issues = []
            self.context["issues"] = issues
            self.current_focus = "issues"
            self.memory.append({
                "action": "identify_issues",
                "result_summary": "Issue identification failed"
            })
            return {"issues": issues}
    
    @trace_function(tags=["cognitive", "risk_assessment"])
    async def assess_risks(self, document: str, issues: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Assess legal risks based on identified issues
        """
        # Use issues from context if not provided
        if issues is None:
            issues = self.context.get("issues", [])
        
        prompt = f"""
            Perform a comprehensive legal risk assessment based on these identified issues:
            
            ISSUES:
            {json.dumps(issues, indent=2)}
            
            DOCUMENT:
            {document[:2000]}...
            
            For each issue, assess:
            1. Likelihood of the risk materializing (High, Medium, Low)
            2. Potential impact if the risk materializes (Severe, Moderate, Minor)
            3. Timeframe for the risk (Immediate, Medium-term, Long-term)
            4. Mitigating factors present in the document
            5. Recommended risk management strategies
            
            Calculate an overall risk score for each issue (1-10) based on likelihood and impact.
            
            Format as a JSON object with "risk_assessment" as an array of risk objects,
            plus a "highest_risks" array highlighting the top 3 risks by score.
        """
        
        response = await get_llm_response(prompt)
        
        try:
            result = json.loads(response)
            # Store in context
            self.context["risks"] = result.get("risk_assessment", [])
            self.context["highest_risks"] = result.get("highest_risks", [])
            self.current_focus = "risks"
            # Add to memory
            self.memory.append({
                "action": "assess_risks",
                "result_summary": f"Assessed {len(result.get('risk_assessment', []))} risks"
            })
            return result
        except json.JSONDecodeError:
            # Try to extract risk assessment
            try:
                start = response.find('"risk_assessment"')
                if start >= 0:
                    array_start = response.find('[', start)
                    array_end = response.find(']', array_start) + 1
                    if array_start >= 0 and array_end > array_start:
                        risks_str = response[array_start:array_end]
                        risks = json.loads(risks_str)
                        
                        # Try to extract highest risks too
                        highest_risks = []
                        hr_start = response.find('"highest_risks"')
                        if hr_start >= 0:
                            hr_array_start = response.find('[', hr_start)
                            hr_array_end = response.find(']', hr_array_start) + 1
                            if hr_array_start >= 0 and hr_array_end > hr_array_start:
                                highest_risks_str = response[hr_array_start:hr_array_end]
                                highest_risks = json.loads(highest_risks_str)
                        
                        result = {
                            "risk_assessment": risks,
                            "highest_risks": highest_risks
                        }
                        
                        self.context["risks"] = risks
                        self.context["highest_risks"] = highest_risks
                        self.current_focus = "risks"
                        self.memory.append({
                            "action": "assess_risks",
                            "result_summary": f"Assessed {len(risks)} risks"
                        })
                        return result
            except:
                pass
            
            # Return basic structure if parsing fails
            risks = []
            highest_risks = []
            self.context["risks"] = risks
            self.context["highest_risks"] = highest_risks
            self.current_focus = "risks"
            self.memory.append({
                "action": "assess_risks",
                "result_summary": "Risk assessment failed"
            })
            return {"risk_assessment": risks, "highest_risks": highest_risks}
    
    @trace_function(tags=["cognitive", "strategy"])
    async def develop_strategy(self, objectives: List[str], risks: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Develop a legal strategy based on objectives and identified risks
        """
        # Use risks from context if not provided
        if risks is None:
            risks = self.context.get("risks", [])
            highest_risks = self.context.get("highest_risks", [])
        else:
            highest_risks = risks[:3]  # Just use top 3 if no specific highest_risks provided
        
        prompt = f"""
            Develop a comprehensive legal strategy based on these objectives and risks:
            
            OBJECTIVES:
            {json.dumps(objectives, indent=2)}
            
            HIGHEST RISKS:
            {json.dumps(highest_risks, indent=2)}
            
            ALL RISKS:
            {json.dumps(risks, indent=2)}
            
            Your strategy should include:
            1. Overall strategic approach
            2. Specific tactics for addressing each objective
            3. Risk mitigation measures for the highest risks
            4. Strategic sequencing of actions
            5. Contingency plans for potential obstacles
            6. Key success metrics and indicators
            
            Format as a JSON object with these six categories as properties.
        """
        
        response = await get_llm_response(prompt)
        
        try:
            strategy = json.loads(response)
            # Store in context
            self.context["strategy"] = strategy
            self.current_focus = "strategy"
            # Add to memory
            self.memory.append({
                "action": "develop_strategy",
                "result_summary": "Developed strategy with " + 
                                 f"{len(strategy.get('specific_tactics', []))} tactics and " +
                                 f"{len(strategy.get('risk_mitigation', []))} risk mitigations"
            })
            return strategy
        except json.JSONDecodeError:
            # Try to extract JSON
            try:
                start = response.find('{')
                end = response.rfind('}') + 1
                if start >= 0 and end > 0:
                    json_str = response[start:end]
                    strategy = json.loads(json_str)
                    
                    self.context["strategy"] = strategy
                    self.current_focus = "strategy"
                    self.memory.append({
                        "action": "develop_strategy",
                        "result_summary": "Developed strategy (parsed from response)"
                    })
                    return strategy
            except:
                pass
            
            # Return basic structure if parsing fails
            strategy = {
                "overall_approach": "Strategy development failed",
                "specific_tactics": [],
                "risk_mitigation": [],
                "strategic_sequencing": [],
                "contingency_plans": [],
                "success_metrics": []
            }
            self.context["strategy"] = strategy
            self.current_focus = "strategy"
            self.memory.append({
                "action": "develop_strategy",
                "result_summary": "Strategy development failed"
            })
            return strategy
    
    @trace_function(tags=["cognitive", "follow_up"])
    async def ask_follow_up(self, question: str) -> Dict[str, Any]:
        """
        Process a follow-up question about the current context
        """
        # Determine what context to include based on current focus
        context_json = {}
        
        if self.current_focus == "issues":
            context_json["issues"] = self.context.get("issues", [])
        elif self.current_focus == "risks":
            context_json["risks"] = self.context.get("risks", [])
            context_json["highest_risks"] = self.context.get("highest_risks", [])
        elif self.current_focus == "strategy":
            context_json["strategy"] = self.context.get("strategy", {})
        else:
            # Include everything if no specific focus
            context_json = self.context
        
        prompt = f"""
            Answer this follow-up question based on the current context:
            
            QUESTION: {question}
            
            CURRENT CONTEXT:
            {json.dumps(context_json, indent=2)}
            
            CONVERSATION HISTORY:
            {json.dumps(self.memory, indent=2)}
            
            Provide a clear, direct answer to the question using the available context.
            If the question cannot be answered with the current context, explain what 
            additional information or analysis would be needed.
            
            Format as a JSON object with "answer", "confidence" (0-100), and
            "additional_information_needed" properties.
        """
        
        response = await get_llm_response(prompt)
        
        try:
            result = json.loads(response)
            # Add to memory
            self.memory.append({
                "action": "ask_follow_up",
                "question": question,
                "answer_preview": result.get("answer", "")[:50] + "..."
            })
            return result
        except json.JSONDecodeError:
            # Try to extract JSON
            try:
                start = response.find('{')
                end = response.rfind('}') + 1
                if start >= 0 and end > 0:
                    json_str = response[start:end]
                    result = json.loads(json_str)
                    
                    self.memory.append({
                        "action": "ask_follow_up",
                        "question": question,
                        "answer_preview": result.get("answer", "")[:50] + "..."
                    })
                    return result
            except:
                pass
            
            # Return basic answer if parsing fails
            result = {
                "answer": "I apologize, but I encountered an error processing your question.",
                "confidence": 0,
                "additional_information_needed": ["Full context processing failed"]
            }
            self.memory.append({
                "action": "ask_follow_up",
                "question": question,
                "error": "Processing failed"
            })
            return result
    
    @trace_function(tags=["cognitive", "explanation"])
    async def explain_reasoning(self, topic: str) -> Dict[str, Any]:
        """
        Explain the reasoning behind a particular aspect of the analysis
        """
        prompt = f"""
            Explain the reasoning behind this aspect of the legal analysis:
            
            TOPIC: {topic}
            
            CONTEXT:
            {json.dumps(self.context, indent=2)}
            
            MEMORY:
            {json.dumps(self.memory, indent=2)}
            
            Provide:
            1. The key factors considered in the analysis
            2. Alternative perspectives or approaches considered
            3. How conclusions were reached
            4. Confidence level in the reasoning
            5. Limitations or assumptions in the analysis
            
            Format as a JSON object with these five properties.
        """
        
        response = await get_llm_response(prompt)
        
        try:
            explanation = json.loads(response)
            # Add to memory
            self.memory.append({
                "action": "explain_reasoning",
                "topic": topic,
                "explanation_preview": str(explanation)[:50] + "..."
            })
            return explanation
        except json.JSONDecodeError:
            # Try to extract JSON
            try:
                start = response.find('{')
                end = response.rfind('}') + 1
                if start >= 0 and end > 0:
                    json_str = response[start:end]
                    explanation = json.loads(json_str)
                    
                    self.memory.append({
                        "action": "explain_reasoning",
                        "topic": topic,
                        "explanation_preview": str(explanation)[:50] + "..."
                    })
                    return explanation
            except:
                pass
            
            # Return basic structure if parsing fails
            explanation = {
                "key_factors": ["Explanation generation failed"],
                "alternative_perspectives": [],
                "conclusion_process": "Could not reconstruct reasoning process",
                "confidence_level": "Low",
                "limitations": ["Full explanation unavailable"]
            }
            self.memory.append({
                "action": "explain_reasoning",
                "topic": topic,
                "error": "Explanation failed"
            })
            return explanation
