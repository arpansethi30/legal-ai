# backend/src/services/document.py
from typing import Dict, Any, Optional
import os
import tempfile
import asyncio

from src.models.document_processor import DocumentProcessor
from src.models.gemini import GeminiModel

class DocumentService:
    """Service for document analysis and processing"""
    
    def __init__(self):
        """Initialize the document service"""
        self.document_processor = DocumentProcessor()
        self.gemini_model = GeminiModel()

    async def analyze_document(self, content: bytes, filename: str, query: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze a document and extract key information
        
        Args:
            content: The raw file content
            filename: The name of the uploaded file
            query: Optional specific question about the document
            
        Returns:
            Dict with the success status and analysis results or error message
        """
        try:
            # Process the document
            doc_result = await self.document_processor.process_document(content, filename)
            
            if not doc_result["success"]:
                return {
                    "success": False,
                    "error": f"Document processing failed: {doc_result.get('error', 'Unknown error')}",
                    "status_code": 400
                }
            
            # Analyze the document with Gemini
            analysis_result = await self.gemini_model.analyze_document(
                document_text=doc_result["text"],
                document_images=doc_result["image_paths"],
                query=query
            )
            
            if not analysis_result["success"]:
                return {
                    "success": False,
                    "error": f"Analysis failed: {analysis_result.get('error', 'Unknown error')}",
                    "status_code": 500
                }
            
            # Format the response
            response = {
                "document": {
                    "filename": filename,
                    "text_length": len(doc_result["text"]),
                    "file_type": doc_result["file_type"]
                },
                "analysis": analysis_result
            }
            
            return {
                "success": True,
                "data": response
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"An error occurred: {str(e)}",
                "status_code": 500
            } 