import asyncio
from typing import Dict, List, Any, Optional
import json
import re

class LegalDocumentEmbeddings:
    """
    Vector-based representations of legal documents for semantic similarity and retrieval
    
    Note: This is a simplified version for the hackathon that simulates embeddings.
    In a production system, this would use a proper vector database and embedding model.
    """
    
    def __init__(self):
        self.document_store = {}  # doc_id -> {text, metadata, embedding}
    
    async def add_document(self, doc_id: str, text: str, metadata: Dict[str, Any] = None):
        """Add a document to the store"""
        # In a real system, this would compute actual embeddings
        # For the hackathon, we'll simulate this with keyword extraction
        keywords = await self._extract_keywords(text)
        
        self.document_store[doc_id] = {
            "text": text,
            "metadata": metadata or {},
            "keywords": keywords
        }
    
    async def find_similar_documents(self, query_text: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Find documents similar to the query text"""
        if not self.document_store:
            return []
        
        # Extract keywords from query
        query_keywords = await self._extract_keywords(query_text)
        
        # Compute similarity scores (using keyword overlap as a proxy for embedding similarity)
        scores = []
        for doc_id, doc in self.document_store.items():
            doc_keywords = doc["keywords"]
            # Simple similarity: count of overlapping keywords
            overlap = len(set(query_keywords) & set(doc_keywords))
            scores.append((doc_id, overlap))
        
        # Sort by score and get top_k
        scores.sort(key=lambda x: x[1], reverse=True)
        top_docs = scores[:top_k]
        
        # Return the top documents with their metadata
        results = []
        for doc_id, score in top_docs:
            doc = self.document_store[doc_id]
            results.append({
                "doc_id": doc_id,
                "score": score,
                "metadata": doc["metadata"],
                "text_preview": doc["text"][:200] + "..."  # First 200 chars as preview
            })
        
        return results
    
    async def semantic_clause_search(self, contract_text: str, query: str) -> Dict[str, Any]:
        """
        Semantically search for relevant clauses in a contract based on natural language query
        """
        # Split the contract into clauses (paragraphs as a simple proxy)
        clauses = [p.strip() for p in contract_text.split("\n\n") if p.strip()]
        
        # Add each clause as a document
        for i, clause in enumerate(clauses):
            await self.add_document(f"clause_{i}", clause, {"index": i})
        
        # Find similar clauses
        similar = await self.find_similar_documents(query, top_k=3)
        
        return {
            "query": query,
            "relevant_clauses": similar,
            "total_clauses_analyzed": len(clauses)
        }
    
    async def _extract_keywords(self, text: str) -> List[str]:
        """
        Extract keywords from text (simplified for the hackathon)
        In a real system, this would use a proper NLP model or embedding
        """
        # Remove punctuation and convert to lowercase
        text = re.sub(r'[^\w\s]', '', text.lower())
        
        # Split into words
        words = text.split()
        
        # Remove common words (very simplified stopword removal)
        stopwords = {'the', 'and', 'to', 'of', 'a', 'in', 'that', 'is', 'for', 'with', 'on', 'by', 'this', 'as'}
        keywords = [word for word in words if word not in stopwords and len(word) > 2]
        
        # Get unique keywords
        unique_keywords = list(set(keywords))
        
        # Return top keywords by frequency (simplified)
        return unique_keywords[:50]