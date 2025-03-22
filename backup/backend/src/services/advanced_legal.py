# backend/src/services/advanced_legal.py
from typing import Dict, Any, Optional
from fastapi import UploadFile
import os
import tempfile
import asyncio

from src.models.document_processor import DocumentProcessor
from src.models.gemini import GeminiModel
from src.models.document_comparison import DocumentComparison

class AdvancedLegalService:
    """Service for advanced legal AI operations"""
    
    def __init__(self):
        """Initialize the advanced legal service"""
        self.document_processor = DocumentProcessor()
        self.gemini_model = GeminiModel()
        self.document_comparison = DocumentComparison()

    async def process_query(self, query: str, context: Optional[str] = None, domain: Optional[str] = None) -> Dict[str, Any]:
        """
        Process an advanced legal query
        
        Args:
            query: The legal question to answer
            context: Optional additional context
            domain: Optional legal domain for specialized processing
            
        Returns:
            Dict with the success status and response or error message
        """
        try:
            # Process the advanced query
            result = await self.gemini_model.answer_advanced_query(
                query=query,
                context=context,
                domain=domain
            )
            
            if not result["success"]:
                return {
                    "success": False,
                    "error": f"Advanced query processing failed: {result.get('error', 'Unknown error')}",
                    "status_code": 500
                }
            
            return {
                "success": True,
                "data": result
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"An error occurred: {str(e)}",
                "status_code": 500
            }
    
    async def analyze_document(self, file: UploadFile, document_type: str = "general") -> Dict[str, Any]:
        """
        Analyze a legal document using advanced AI techniques
        
        Args:
            file: The document to analyze
            document_type: Type of document for specialized processing
            
        Returns:
            Dict with the success status and analysis results or error message
        """
        try:
            # Read and process the file
            content = await file.read()
            doc_result = await self.document_processor.process_document(content, file.filename)
            
            if not doc_result["success"]:
                return {
                    "success": False,
                    "error": f"Document processing failed: {doc_result.get('error', 'Unknown error')}",
                    "status_code": 400
                }
            
            # Perform advanced analysis based on document type
            analysis_result = await self.gemini_model.analyze_specialized_document(
                document_text=doc_result["text"],
                document_images=doc_result["image_paths"],
                document_type=document_type
            )
            
            if not analysis_result["success"]:
                return {
                    "success": False,
                    "error": f"Advanced analysis failed: {analysis_result.get('error', 'Unknown error')}",
                    "status_code": 500
                }
            
            return {
                "success": True,
                "data": analysis_result
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"An error occurred: {str(e)}",
                "status_code": 500
            }
    
    async def compare_documents(self, file1: UploadFile, file2: UploadFile, document_type: str = "general") -> Dict[str, Any]:
        """
        Compare two legal documents and identify differences
        
        Args:
            file1: First document to compare
            file2: Second document to compare
            document_type: Type of documents for specialized processing
            
        Returns:
            Dict with the success status and comparison results or error message
        """
        try:
            # Process both documents
            content1 = await file1.read()
            content2 = await file2.read()
            
            doc_result1 = await self.document_processor.process_document(content1, file1.filename)
            doc_result2 = await self.document_processor.process_document(content2, file2.filename)
            
            if not doc_result1["success"]:
                return {
                    "success": False,
                    "error": f"First document processing failed: {doc_result1.get('error', 'Unknown error')}",
                    "status_code": 400
                }
                
            if not doc_result2["success"]:
                return {
                    "success": False,
                    "error": f"Second document processing failed: {doc_result2.get('error', 'Unknown error')}",
                    "status_code": 400
                }
            
            # Compare the documents
            compare_result = await self.document_comparison.compare_documents(
                doc1_text=doc_result1["text"],
                doc2_text=doc_result2["text"],
                doc_type=document_type
            )
            
            if not compare_result["success"]:
                return {
                    "success": False,
                    "error": f"Document comparison failed: {compare_result.get('error', 'Unknown error')}",
                    "status_code": 500
                }
            
            return {
                "success": True,
                "data": compare_result
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"An error occurred: {str(e)}",
                "status_code": 500
            } 