# backend/models/gemini.py
import time
import google.generativeai as genai
from typing import Dict, List, Optional, Any
import base64
from PIL import Image
import io
import json
import sys
import os

# Fix import path for config
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from app.config import settings

class GeminiModel:
    """Interface to Google's Gemini models for legal AI tasks"""
    
    def __init__(self):
        # Check for API key
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not provided in environment variables")
            
        # Configure Gemini
        genai.configure(api_key=settings.GEMINI_API_KEY)
        
        # Legal prompt template
        self.legal_system_prompt = """
        You are a legal assistant specialized in document analysis and legal queries.
        You should:
        1. Provide clear and concise summaries of legal documents
        2. Identify potential legal risks and flag them
        3. Answer legal questions based on provided documents or general legal knowledge
        4. Organize information in a structured manner with sections and bullet points
        5. Be clear about uncertainties and when further professional legal advice is needed
        6. Never provide definitive legal advice that could be construed as practicing law
        7. Always include a disclaimer that you are an AI assistant and not a licensed attorney
        
        Format your responses professionally with clear headings and structured information.
        """
        
        # Available models
        self.models = {
            "flash": genai.GenerativeModel(settings.GEMINI_FLASH_MODEL),
            "pro": genai.GenerativeModel(settings.GEMINI_PRO_MODEL)
        }
    
    def _prepare_image_parts(self, image_paths: List[str]) -> List[Dict[str, Any]]:
        """Convert image paths to format required by Gemini API"""
        image_parts = []
        for img_path in image_paths:
            try:
                img = Image.open(img_path)
                buffer = io.BytesIO()
                img.save(buffer, format="PNG")
                image_parts.append({
                    "mime_type": "image/png",
                    "data": buffer.getvalue()
                })
            except Exception as e:
                print(f"Error processing image {img_path}: {e}")
        return image_parts
    
    async def analyze_document(self, 
                         document_text: str, 
                         document_images: Optional[List[str]] = None,
                         query: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze a legal document using Gemini Pro model
        
        Args:
            document_text: Extracted text from document
            document_images: List of paths to document images
            query: Optional specific query about the document
        
        Returns:
            Dictionary with analysis results
        """
        prompt = f"{self.legal_system_prompt}\n\nAnalyze the following legal document and provide:"
        
        if query:
            prompt += f"\n\nUser's specific query: {query}\n\nPlease address this query and provide a complete analysis."
        else:
            prompt += """
            
            1. DOCUMENT SUMMARY
            Provide a concise summary (2-3 paragraphs) highlighting the key purpose and main points.
            
            2. KEY LEGAL POINTS
            Identify and explain the main legal provisions, rights, obligations, and conditions.
            
            3. POTENTIAL RISKS OR ISSUES
            Flag any concerning clauses, vague language, or potential legal issues.
            
            4. RECOMMENDATIONS
            Suggest areas that may need further review or professional legal attention.
            
            Format your response with clear section headings and bullet points where appropriate.
            """
        
        # Prepare content parts
        content_parts = [prompt, document_text]
        
        # Add images if provided
        if document_images and len(document_images) > 0:
            image_parts = self._prepare_image_parts(document_images)
            content_parts.extend(image_parts)
        
        try:
            # Use Pro model for document analysis
            response = await self.models["pro"].generate_content_async(content_parts)
            
            result = {
                "success": True,
                "analysis": response.text,
                "processing_time": time.time(),
                "model_used": settings.GEMINI_PRO_MODEL
            }
            
            # Add disclaimer
            result["analysis"] += "\n\n---\n\n**Disclaimer**: This analysis was generated by an AI assistant and should not be considered legal advice. Please consult with a licensed attorney for professional legal counsel."
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "model_used": settings.GEMINI_PRO_MODEL
            }
    
    async def answer_query(self, 
                    query: str, 
                    context: Optional[str] = None,
                    image_paths: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Answer a legal query using the appropriate Gemini model
        
        Args:
            query: The legal question to answer
            context: Optional additional context or document text
            image_paths: Optional list of paths to images
            
        Returns:
            Dictionary with query response
        """
        # Determine which model to use based on query complexity and context
        use_pro_model = False
        if len(query) > 200 or (context and len(context) > 500):
            use_pro_model = True
        if image_paths and len(image_paths) > 0:
            use_pro_model = True
            
        model_key = "pro" if use_pro_model else "flash"
        model_name = settings.GEMINI_PRO_MODEL if use_pro_model else settings.GEMINI_FLASH_MODEL
        
        prompt = f"{self.legal_system_prompt}\n\nPlease answer the following legal question:\n\n{query}"
        
        if context:
            prompt += f"\n\nAdditional context:\n\n{context}"
        
        # Prepare content parts
        content_parts = [prompt]
        
        # Add images if provided
        if image_paths and len(image_paths) > 0:
            image_parts = self._prepare_image_parts(image_paths)
            content_parts.extend(image_parts)
        
        try:
            response = await self.models[model_key].generate_content_async(content_parts)
            
            result = {
                "success": True,
                "answer": response.text,
                "processing_time": time.time(),
                "model_used": model_name
            }
            
            # Add disclaimer
            result["answer"] += "\n\n---\n\n**Disclaimer**: This response was generated by an AI assistant and should not be considered legal advice. Please consult with a licensed attorney for professional legal counsel."
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "model_used": model_name
            }