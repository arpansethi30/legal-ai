import asyncio
import json
from typing import Dict, Any, List
import google.generativeai as genai
from app.config import settings
from app.services.langtrace import trace_llm_call

# Initialize the Gemini API
genai.configure(api_key=settings.GOOGLE_API_KEY)

# Advanced system instruction for better legal reasoning
system_instruction = """
You are LegalCounsel AI, an advanced legal assistant with expertise in contract law, negotiations, and dispute resolution.

Approach every task with these principles:
1. Be precise in legal language and reasoning
2. Consider all parties' interests fairly
3. Identify risks proactively
4. Suggest practical solutions
5. Explain reasoning transparently

When analyzing legal text:
- Identify explicit and implicit obligations
- Detect ambiguities and potential misinterpretations
- Consider enforceability and jurisdiction issues
- Assess fairness and balance between parties

When drafting contracts:
- Use clear, specific language
- Define terms precisely
- Structure logically with standard legal sections
- Include appropriate safeguards for all parties

Think step-by-step through complex legal questions before answering.
"""

# Set up the model with enhanced configuration
model = genai.GenerativeModel(
    'gemini-2.0-flash',
    system_instruction=system_instruction,
    generation_config={
        "temperature": 0.1,  # Lower for more precise legal reasoning
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8192,  # Allow for comprehensive legal analysis
    }
)

@trace_llm_call
async def get_llm_response(prompt: str) -> str:
    """
    Get a response from Google's Gemini 2.0 with enhanced legal reasoning
    """
    try:
        # Add reasoning prefix for complex legal tasks
        if len(prompt) > 200 and ("analyze" in prompt.lower() or "draft" in prompt.lower() or "identify" in prompt.lower()):
            enhanced_prompt = f"""
            {prompt}
            
            Let's think through this step-by-step:
            1. First, I'll analyze the key components of this task
            2. Then, I'll identify the relevant legal principles and considerations
            3. Next, I'll apply those principles to this specific situation
            4. Finally, I'll formulate a comprehensive response
            
            My analysis:
            """
        else:
            enhanced_prompt = prompt
        
        # Run in an executor to make it async-compatible
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None, 
            lambda: model.generate_content(enhanced_prompt).text
        )
        return response
    except Exception as e:
        print(f"Error calling Gemini API: {str(e)}")
        # Fallback response
        return "I was unable to process that legal request due to a technical error. Please try again with a more specific prompt."

@trace_llm_call
async def get_structured_legal_analysis(text: str, output_format: dict) -> dict:
    """
    Get a structured legal analysis with specific output format
    """
    prompt = f"""
    Perform a comprehensive legal analysis of the following text:
    
    {text}
    
    Provide your analysis in a structured JSON format exactly matching this schema:
    {json.dumps(output_format, indent=2)}
    
    Ensure all keys in the schema are present in your response, even if some values are empty lists or strings.
    Think step-by-step through your legal reasoning before finalizing your analysis.
    """
    
    response = await get_llm_response(prompt)
    
    try:
        # Try to parse as JSON
        return json.loads(response)
    except json.JSONDecodeError:
        # Try to extract JSON from the response
        try:
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                return json.loads(json_str)
        except:
            pass
        
        # If all parsing fails, return an empty structure matching the output format
        return {key: ([] if isinstance(value, list) else "") for key, value in output_format.items()}

async def analyze_legal_text(text: str) -> dict:
    """
    Analyze legal text for entities, obligations, and risks
    """
    output_format = {
        "entities": [],
        "obligations": [],
        "rights": [],
        "timeframes": [],
        "risks": {}
    }
    
    return await get_structured_legal_analysis(text, output_format)

async def get_legal_knowledge_with_citations(query: str) -> Dict[str, Any]:
    """
    Provide legal information with citations to relevant legal principles
    """
    prompt = f"""
    Legal Query: {query}
    
    Provide a comprehensive answer to this legal question with:
    1. Clear explanation of applicable legal principles
    2. Specific citations to relevant legal standards or authorities
    3. Practical implications and considerations
    4. Any important exceptions or edge cases
    
    Format your response as a JSON object with the following structure:
    {{
        "explanation": "Detailed explanation here",
        "legal_principles": [
            {{
                "principle": "Name of legal principle",
                "description": "Brief description",
                "citation": "Proper legal citation"
            }}
        ],
        "practical_implications": ["Implication 1", "Implication 2"],
        "exceptions": ["Exception 1", "Exception 2"]
    }}
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
            "explanation": "Unable to generate detailed explanation",
            "legal_principles": [],
            "practical_implications": [],
            "exceptions": []
        }