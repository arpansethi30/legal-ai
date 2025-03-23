import re
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from app.core.llm import get_llm_response

class TemporalReasoning:
    """
    Specialized system for reasoning about time-based obligations in contracts
    """
    
    @staticmethod
    async def extract_timeframes(contract_text: str) -> Dict[str, Any]:
        """
        Extract all timeframes, deadlines, and time-based obligations from a contract
        """
        prompt = f"""
            Extract all timeframes and time-based obligations from this contract:
            
            {contract_text}
            
            For each time element, identify:
            1. The specific obligation or event
            2. The time period or deadline
            3. The triggering event (if applicable)
            4. The consequences of meeting or missing the deadline
            
            Format as a JSON array of timeframe objects, each with these four properties.
        """
        
        response = await get_llm_response(prompt)
        
        try:
            timeframes = json.loads(response)
            return {"timeframes": timeframes}
        except json.JSONDecodeError:
            # Try to extract a JSON array
            try:
                start = response.find('[')
                end = response.rfind(']') + 1
                if start >= 0 and end > 0:
                    json_str = response[start:end]
                    timeframes = json.loads(json_str)
                    return {"timeframes": timeframes}
            except:
                pass
            
            # Return basic structure if parsing fails
            return {
                "timeframes": [],
                "error": "Could not extract timeframes"
            }
    
    @staticmethod
    async def create_timeline(contract_text: str, start_date: str) -> Dict[str, Any]:
        """
        Create a timeline of all obligations and events from a contract
        starting from a specific date
        """
        # First, extract timeframes
        timeframes_result = await TemporalReasoning.extract_timeframes(contract_text)
        timeframes = timeframes_result.get("timeframes", [])
        
        prompt = f"""
            Create a timeline of events and obligations based on these extracted timeframes:
            
            {json.dumps(timeframes, indent=2)}
            
            Start date: {start_date}
            
            For each item in the timeline:
            1. Calculate the actual calendar date based on the start date
            2. Describe the obligation or event
            3. Note any dependencies or conditions
            4. Identify the responsible party
            
            Sort the items chronologically and format as a JSON array of timeline events,
            each with these properties plus a "days_from_start" property.
        """
        
        response = await get_llm_response(prompt)
        
        try:
            timeline = json.loads(response)
            return {"timeline": timeline, "start_date": start_date}
        except json.JSONDecodeError:
            # Try to extract a JSON array
            try:
                start = response.find('[')
                end = response.rfind(']') + 1
                if start >= 0 and end > 0:
                    json_str = response[start:end]
                    timeline = json.loads(json_str)
                    return {"timeline": timeline, "start_date": start_date}
            except:
                pass
            
            # Return basic structure if parsing fails
            return {
                "timeline": [],
                "start_date": start_date,
                "error": "Could not create timeline"
            }
    
    @staticmethod
    async def identify_critical_deadlines(contract_text: str) -> Dict[str, Any]:
        """
        Identify critical deadlines in a contract with risk assessment
        """
        prompt = f"""
            Analyze this contract and identify the most critical deadlines or timeframes:
            
            {contract_text}
            
            For each critical deadline, provide:
            1. The deadline description
            2. The specific clause or section it appears in
            3. The consequences of missing this deadline
            4. A risk level (High, Medium, Low)
            5. Recommendations for monitoring and ensuring compliance
            
            Focus only on the most important timeframes that could have significant
            legal or business consequences if missed.
            
            Format as a JSON array of critical deadlines with these five properties.
        """
        
        response = await get_llm_response(prompt)
        
        try:
            deadlines = json.loads(response)
            return {"critical_deadlines": deadlines}
        except json.JSONDecodeError:
            # Try to extract a JSON array
            try:
                start = response.find('[')
                end = response.rfind(']') + 1
                if start >= 0 and end > 0:
                    json_str = response[start:end]
                    deadlines = json.loads(json_str)
                    return {"critical_deadlines": deadlines}
            except:
                pass
            
            # Return basic structure if parsing fails
            return {
                "critical_deadlines": [],
                "error": "Could not identify critical deadlines"
            }