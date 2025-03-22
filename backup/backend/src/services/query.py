# backend/src/services/query.py
from typing import Dict, Any, Optional
from fastapi import UploadFile

from src.models.document_processor import DocumentProcessor
from src.models.gemini import GeminiModel

class QueryService:
    """Service for processing legal queries"""
    
    def __init__(self):
        """Initialize the query service"""
        self.document_processor = DocumentProcessor()
        self.gemini_model = GeminiModel()

    async def process_query(self, query: str, context: Optional[str] = None, file: Optional[UploadFile] = None) -> Dict[str, Any]:
        """
        Process a legal query with optional context and file
        
        Args:
            query: The legal question to answer
            context: Optional additional context
            file: Optional file with relevant information
            
        Returns:
            Dict with the success status and response or error message
        """
        try:
            image_paths = []
            
            # Process uploaded file if any
            if file:
                # Read and process the file
                content = await file.read()
                doc_result = await self.document_processor.process_document(content, file.filename)
                
                if doc_result["success"]:
                    context = (context or "") + "\n\n" + doc_result["text"]
                    image_paths = doc_result["image_paths"]
                else:
                    return {
                        "success": False,
                        "error": f"Document processing failed: {doc_result.get('error', 'Unknown error')}",
                        "status_code": 400
                    }
            
            # Answer the query
            answer_result = await self.gemini_model.answer_query(
                query=query,
                context=context,
                image_paths=image_paths
            )
            
            if not answer_result["success"]:
                return {
                    "success": False,
                    "error": f"Query processing failed: {answer_result.get('error', 'Unknown error')}",
                    "status_code": 500
                }
            
            response = {
                "query": query,
                "response": answer_result
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