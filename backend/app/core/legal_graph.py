from typing import Dict, List, Any, Optional, Tuple
import json
import asyncio
from app.core.llm import get_llm_response

class LegalEntity:
    """Base class for entities in the legal knowledge graph"""
    def __init__(self, id: str, name: str, entity_type: str):
        self.id = id
        self.name = name
        self.entity_type = entity_type
        self.properties = {}
        self.relationships = []
    
    def add_property(self, key: str, value: Any):
        """Add a property to the entity"""
        self.properties[key] = value
    
    def add_relationship(self, target_id: str, relation_type: str, properties: Dict[str, Any] = None):
        """Add a relationship to another entity"""
        self.relationships.append({
            "target_id": target_id,
            "relation_type": relation_type,
            "properties": properties or {}
        })
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary representation"""
        return {
            "id": self.id,
            "name": self.name,
            "entity_type": self.entity_type,
            "properties": self.properties,
            "relationships": self.relationships
        }

class LegalKnowledgeGraph:
    """
    Knowledge graph for legal concepts, precedents, and relationships
    """
    
    def __init__(self):
        self.entities = {}  # id -> LegalEntity
    
    def add_entity(self, entity: LegalEntity):
        """Add an entity to the graph"""
        self.entities[entity.id] = entity
    
    def get_entity(self, entity_id: str) -> Optional[LegalEntity]:
        """Get an entity by ID"""
        return self.entities.get(entity_id)
    
    def get_related_entities(self, entity_id: str, relation_type: Optional[str] = None) -> List[Tuple[str, str]]:
        """Get entities related to the given entity"""
        entity = self.get_entity(entity_id)
        if not entity:
            return []
        
        related = []
        for rel in entity.relationships:
            if relation_type is None or rel["relation_type"] == relation_type:
                related.append((rel["target_id"], rel["relation_type"]))
        
        return related
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert entire graph to dictionary representation"""
        return {
            "entities": {
                entity_id: entity.to_dict()
                for entity_id, entity in self.entities.items()
            }
        }
    
    async def extract_graph_from_text(self, legal_text: str) -> Dict[str, Any]:
        """Extract a knowledge graph from legal text"""
        prompt = f"""
            Extract a legal knowledge graph from this text:
            
            {legal_text}
            
            Identify:
            1. Legal concepts (e.g., "Force Majeure", "Indemnification")
            2. Parties and entities (e.g., "Employer", "Contractor")
            3. Obligations (e.g., "Payment Obligation", "Delivery Requirement")
            4. Conditions and timeframes (e.g., "30-Day Notice Period")
            
            For each entity, provide:
            - A unique ID
            - The entity name
            - The entity type (concept, party, obligation, condition)
            - Key properties
            
            Then identify relationships between these entities, including:
            - The source entity ID
            - The target entity ID
            - The relationship type (e.g., "has_obligation", "is_subject_to", "must_comply_with")
            
            Format as a JSON object with "entities" and "relationships" arrays.
        """
        
        response = await get_llm_response(prompt)
        
        try:
            extracted = json.loads(response)
            
            # Convert the extracted data to our graph format
            graph = LegalKnowledgeGraph()
            
            # Add entities
            for entity_data in extracted.get("entities", []):
                entity = LegalEntity(
                    id=entity_data.get("id", f"entity_{len(graph.entities)}"),
                    name=entity_data.get("name", "Unknown"),
                    entity_type=entity_data.get("entity_type", "unknown")
                )
                
                # Add properties
                for key, value in entity_data.get("properties", {}).items():
                    entity.add_property(key, value)
                
                graph.add_entity(entity)
            
            # Add relationships
            for rel in extracted.get("relationships", []):
                source_id = rel.get("source_id")
                target_id = rel.get("target_id")
                relation_type = rel.get("relation_type")
                properties = rel.get("properties", {})
                
                if source_id and target_id and relation_type:
                    source_entity = graph.get_entity(source_id)
                    if source_entity:
                        source_entity.add_relationship(target_id, relation_type, properties)
            
            return graph.to_dict()
        except json.JSONDecodeError:
            # Return a basic structure if parsing fails
            return {
                "entities": [],
                "error": "Failed to extract knowledge graph"
            }
    
    async def query_graph(self, query: str, graph_data: Dict[str, Any]) -> Dict[str, Any]:
        """Query the knowledge graph using natural language"""
        
        prompt = f"""
            Given this legal knowledge graph:
            
            {json.dumps(graph_data, indent=2)}
            
            Answer this query: {query}
            
            Provide:
            1. The direct answer to the query
            2. The reasoning based on the graph structure
            3. The specific entities and relationships that support your answer
            
            Format your response as a JSON object with these three keys.
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
                "answer": "Could not process query",
                "reasoning": "Failed to parse graph or query results",
                "supporting_evidence": []
            }