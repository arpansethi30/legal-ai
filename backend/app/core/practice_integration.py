import json
from typing import Dict, List, Any, Optional
from enum import Enum
from datetime import datetime, timedelta
from app.core.llm import get_llm_response

class PracticeManagementSystem(Enum):
    """Common legal practice management systems"""
    CLIO = "Clio"
    PRACTICE_PANTHER = "Practice Panther"
    SMOKEBALL = "Smokeball"
    MYCASE = "MyCase"
    ROCKET_MATTER = "Rocket Matter"
    LEGAL_FILES = "Legal Files"
    CUSTOM = "Custom System"

class PracticeArea(Enum):
    """Common legal practice areas"""
    LITIGATION = "Litigation"
    CORPORATE = "Corporate"
    REAL_ESTATE = "Real Estate"
    INTELLECTUAL_PROPERTY = "Intellectual Property"
    EMPLOYMENT = "Employment"
    FAMILY = "Family Law"
    ESTATE_PLANNING = "Estate Planning"
    TAX = "Tax"
    IMMIGRATION = "Immigration"
    CRIMINAL = "Criminal Defense"

class PracticeIntegration:
    """
    Integration with legal practice management systems to streamline workflows
    """
    
    @staticmethod
    async def generate_client_memo(analysis: Dict[str, Any], client_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a client-ready memo based on a legal analysis
        """
        prompt = f"""
            Generate a professional client memo based on this legal analysis:
            
            ANALYSIS:
            {json.dumps(analysis, indent=2)}
            
            CLIENT INFO:
            {json.dumps(client_info, indent=2)}
            
            The memo should be written in plain language appropriate for a client while maintaining legal precision.
            Include:
            1. Executive summary (2-3 paragraphs)
            2. Background context
            3. Key findings
            4. Practical recommendations
            5. Next steps
            
            Format as a JSON object with these sections as properties.
            The content should be ready to share with the client with appropriate formatting.
        """
        
        response = await get_llm_response(prompt)
        
        try:
            memo = json.loads(response)
            return {
                "client_name": client_info.get("name", "Client"),
                "date": datetime.now().strftime("%Y-%m-%d"),
                "memo": memo
            }
        except json.JSONDecodeError:
            # Try to extract JSON
            try:
                start = response.find('{')
                end = response.rfind('}') + 1
                if start >= 0 and end > 0:
                    json_str = response[start:end]
                    memo = json.loads(json_str)
                    return {
                        "client_name": client_info.get("name", "Client"),
                        "date": datetime.now().strftime("%Y-%m-%d"),
                        "memo": memo
                    }
            except:
                pass
            
            # Return basic structure if parsing fails
            return {
                "client_name": client_info.get("name", "Client"),
                "date": datetime.now().strftime("%Y-%m-%d"),
                "memo": {
                    "executive_summary": "Memo generation failed",
                    "background": "",
                    "key_findings": [],
                    "recommendations": [],
                    "next_steps": []
                }
            }
    
    @staticmethod
    async def generate_time_entries(activities: List[Dict[str, Any]], billing_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate formatted time entries for a practice management system
        """
        prompt = f"""
            Generate professional time entries based on these legal activities:
            
            ACTIVITIES:
            {json.dumps(activities, indent=2)}
            
            BILLING INFO:
            {json.dumps(billing_info, indent=2)}
            
            For each activity, create a time entry with:
            1. A clear, concise description appropriate for client billing
            2. Appropriate time allocation in 0.1 hour increments
            3. The correct billing code or category
            4. Any necessary explanatory notes (separate from the client-facing description)
            
            Format as a JSON array of time entry objects with these four properties.
            Ensure descriptions are professional and justify the time spent while being transparent to the client.
        """
        
        response = await get_llm_response(prompt)
        
        try:
            time_entries = json.loads(response)
            return {
                "client_matter": billing_info.get("matter_id", "Unknown Matter"),
                "timekeeper": billing_info.get("timekeeper_id", "Unknown Timekeeper"),
                "date": datetime.now().strftime("%Y-%m-%d"),
                "time_entries": time_entries,
                "total_hours": sum(entry.get("time", 0) for entry in time_entries)
            }
        except json.JSONDecodeError:
            # Try to extract a JSON array
            try:
                start = response.find('[')
                end = response.rfind(']') + 1
                if start >= 0 and end > 0:
                    json_str = response[start:end]
                    time_entries = json.loads(json_str)
                    return {
                        "client_matter": billing_info.get("matter_id", "Unknown Matter"),
                        "timekeeper": billing_info.get("timekeeper_id", "Unknown Timekeeper"),
                        "date": datetime.now().strftime("%Y-%m-%d"),
                        "time_entries": time_entries,
                        "total_hours": sum(entry.get("time", 0) for entry in time_entries)
                    }
            except:
                pass
            
            # Return basic structure if parsing fails
            return {
                "client_matter": billing_info.get("matter_id", "Unknown Matter"),
                "timekeeper": billing_info.get("timekeeper_id", "Unknown Timekeeper"),
                "date": datetime.now().strftime("%Y-%m-%d"),
                "time_entries": [],
                "total_hours": 0,
                "error": "Time entry generation failed"
            }
    
    @staticmethod
    async def create_task_list(project: Dict[str, Any], deadline: str) -> Dict[str, Any]:
        """
        Create a task list with deadlines and assignments for a legal project
        """
        prompt = f"""
            Create a comprehensive task list for this legal project:
            
            PROJECT:
            {json.dumps(project, indent=2)}
            
            FINAL DEADLINE: {deadline}
            
            Create a detailed task list that:
            1. Breaks the project into logical phases
            2. Lists specific tasks within each phase
            3. Assigns appropriate deadlines to each task (working backward from the final deadline)
            4. Estimates hours required for each task
            5. Identifies dependencies between tasks
            
            Format as a JSON object with "phases" as an array of phase objects,
            each containing a "tasks" array with detailed task information.
        """
        
        response = await get_llm_response(prompt)
        
        try:
            task_list = json.loads(response)
            return {
                "project_name": project.get("name", "Legal Project"),
                "final_deadline": deadline,
                "created_date": datetime.now().strftime("%Y-%m-%d"),
                "task_list": task_list
            }
        except json.JSONDecodeError:
            # Try to extract JSON
            try:
                start = response.find('{')
                end = response.rfind('}') + 1
                if start >= 0 and end > 0:
                    json_str = response[start:end]
                    task_list = json.loads(json_str)
                    return {
                        "project_name": project.get("name", "Legal Project"),
                        "final_deadline": deadline,
                        "created_date": datetime.now().strftime("%Y-%m-%d"),
                        "task_list": task_list
                    }
            except:
                pass
            
            # Return basic structure if parsing fails
            return {
                "project_name": project.get("name", "Legal Project"),
                "final_deadline": deadline,
                "created_date": datetime.now().strftime("%Y-%m-%d"),
                "task_list": {
                    "phases": []
                },
                "error": "Task list generation failed"
            }
    
    @staticmethod
    async def format_for_system(data: Dict[str, Any], system: str) -> Dict[str, Any]:
        """
        Format data for a specific practice management system
        """
        prompt = f"""
            Convert this legal data to a format compatible with {system}:
            
            DATA:
            {json.dumps(data, indent=2)}
            
            Provide the converted data in a format that would be ready for import or API integration
            with {system}. Include all necessary fields and formatting required by this specific system.
            
            Format as a JSON object structured according to {system}'s data model.
        """
        
        response = await get_llm_response(prompt)
        
        try:
            formatted_data = json.loads(response)
            return {
                "original_data_type": list(data.keys())[0] if data else "unknown",
                "target_system": system,
                "formatted_data": formatted_data
            }
        except json.JSONDecodeError:
            # Try to extract JSON
            try:
                start = response.find('{')
                end = response.rfind('}') + 1
                if start >= 0 and end > 0:
                    json_str = response[start:end]
                    formatted_data = json.loads(json_str)
                    return {
                        "original_data_type": list(data.keys())[0] if data else "unknown",
                        "target_system": system,
                        "formatted_data": formatted_data
                    }
            except:
                pass
            
            # Return basic structure if parsing fails
            return {
                "original_data_type": list(data.keys())[0] if data else "unknown",
                "target_system": system,
                "error": f"Could not format data for {system}",
                "formatted_data": {}
            }