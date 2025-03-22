import os
import google.generativeai as genai
from typing import List, Dict, Any, Optional, Tuple
import json
import time
import logging
from pydantic import BaseModel
import numpy as np
from datetime import datetime

# Add new imports for enhanced capabilities
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.callbacks.manager import CallbackManager
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferMemory
from langchain.prompts import MessagesPlaceholder
from langchain.schema.messages import SystemMessage, HumanMessage
from langchain.schema.runnable import RunnablePassthrough
from langchain.tools import BaseTool, StructuredTool, tool
from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from llama_index.core import VectorStoreIndex
from llama_index.core.readers.schema.base import Document
from llama_index.core import Settings
from llama_index.embeddings.langchain import LangchainEmbedding
from langchain.pydantic_v1 import Field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    logger.error("GEMINI_API_KEY not found in environment variables")
else:
    genai.configure(api_key=GEMINI_API_KEY)

class LegalCitation(BaseModel):
    """Model for legal citations"""
    citation: str
    reporter: Optional[str] = None
    court: Optional[str] = None
    year: Optional[int] = None
    relevance_score: float = 0.0

class LegalAgentResponse(BaseModel):
    """Model for the agent's response"""
    answer: str
    citations: List[LegalCitation] = []
    reasoning_steps: List[str] = []
    confidence_score: float
    sources_used: List[str] = []
    processing_time: float
    metadata: Dict[str, Any] = {}

class LegalAIAgent:
    """Advanced Legal AI Agent with specialized legal reasoning capabilities and agentic behavior"""
    
    def __init__(self):
        """Initialize the Legal AI Agent with advanced capabilities"""
        self.model_name = "gemini-1.5-pro-latest"  # Using Gemini Pro 2
        self.legal_domains = [
            "contract_law", "intellectual_property", "corporate_law", 
            "criminal_law", "constitutional_law", "administrative_law",
            "international_law", "tax_law", "employment_law", "environmental_law"
        ]
        self.citation_patterns = self._load_citation_patterns()
        
        # Initialize vector database for legal knowledge
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        self.legal_kb = self._initialize_legal_knowledge_base()
        
        # Initialize LangChain components
        if GEMINI_API_KEY:
            # Create Gemini model through LangChain
            self.llm = ChatGoogleGenerativeAI(
                model=self.model_name,
                temperature=0.2,
                convert_system_message_to_human=True,
                verbose=True
            )
            
            # Setup tools and agent
            self.tools = self._create_legal_tools()
            self.agent_executor = self._setup_agent()
            
            # Direct Gemini model for certain tasks
            self.direct_model = genai.GenerativeModel(self.model_name)
            
            logger.info(f"Initialized Legal AI Agent using {self.model_name} with LangChain integration")
        else:
            self.llm = None
            self.direct_model = None
            self.agent_executor = None
            logger.error("Failed to initialize Legal AI Agent: No API key")
    
    def _load_citation_patterns(self) -> Dict[str, str]:
        """Load regex patterns for recognizing legal citations"""
        return {
            "us_scotus": r"\d{1,3}\s+U\.S\.\s+\d{1,4}\s+\(\d{4}\)",
            "us_circuit": r"\d{1,3}\s+F\.\d[a-z]*\s+\d{1,4}\s+\((?:\d{1,2}[a-z]{2}\s+[Cc]ir\.|[A-Z]\.[A-Z]\.)\s+\d{4}\)",
            "state": r"\d{1,3}\s+[A-Z][a-z]+\.\s+\d{1,4}\s+\(\d{4}\)",
        }
    
    def _initialize_legal_knowledge_base(self) -> Any:
        """Initialize vector database with legal knowledge"""
        # This would be populated with actual legal docs in production
        # For now, return a small sample db or empty one if no docs available
        try:
            legal_docs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "contract_templates")
            if os.path.exists(legal_docs_dir) and os.listdir(legal_docs_dir):
                docs = []
                for filename in os.listdir(legal_docs_dir):
                    file_path = os.path.join(legal_docs_dir, filename)
                    if filename.endswith('.pdf'):
                        loader = PyPDFLoader(file_path)
                        docs.extend(loader.load())
                    elif filename.endswith('.docx'):
                        loader = Docx2txtLoader(file_path)
                        docs.extend(loader.load())
                    elif filename.endswith('.txt'):
                        loader = TextLoader(file_path)
                        docs.extend(loader.load())
                
                # Create vector store if documents exist
                if docs:
                    return Chroma.from_documents(docs, self.embeddings)
            
            # Return empty db if no docs found
            return Chroma(self.embeddings)
        except Exception as e:
            logger.error(f"Error initializing legal knowledge base: {e}")
            return None
    
    def _create_legal_tools(self) -> List[BaseTool]:
        """Create specialized legal tools for the agent"""
        tools = []
        
        @tool
        def search_legal_precedents(query: str) -> str:
            """
            Search for relevant legal precedents and case law based on the query.
            Useful for finding case citations and precedents relevant to a legal question.
            """
            # This would use the knowledge base in production
            try:
                if self.legal_kb:
                    docs = self.legal_kb.similarity_search(query, k=3)
                    if docs:
                        return "\n\n".join([f"Document: {d.metadata.get('source', 'Unknown')}\n{d.page_content}" for d in docs])
                
                # Fallback to generated precedents if no KB or no results
                prompt = f"""
                You are a legal research expert. Provide 2-3 relevant legal precedents (actual case law) for the following legal question:
                {query}
                
                For each precedent, provide:
                1. Full case citation
                2. Brief summary of the case (1-2 sentences)
                3. How it relates to the question
                
                Do not make up cases. If you're uncertain, specify that these are illustrative examples only.
                """
                
                response = self.direct_model.generate_content(prompt)
                return response.text
            except Exception as e:
                logger.error(f"Error in search_legal_precedents: {e}")
                return "Error retrieving legal precedents. Please try a different query."
        
        @tool
        def analyze_legal_issues(context: str) -> str:
            """
            Identify and analyze key legal issues in a specific scenario or document.
            Useful for breaking down complex legal situations into discrete legal issues.
            """
            prompt = f"""
            You are a legal issue spotter. Analyze the following context and identify the key legal issues present:
            
            {context}
            
            For each issue:
            1. Name the issue
            2. Identify the area of law it falls under
            3. Explain why it's legally significant
            4. Note any potential jurisdictional considerations
            
            Organize your response by issue, with clear headings.
            """
            
            try:
                response = self.direct_model.generate_content(prompt)
                return response.text
            except Exception as e:
                logger.error(f"Error in analyze_legal_issues: {e}")
                return "Error analyzing legal issues. Please try again with a clearer description."
        
        @tool
        def draft_legal_language(instruction: str, context: str) -> str:
            """
            Draft specialized legal language for contracts, pleadings, or other legal documents.
            Useful for creating precise legal text based on specific requirements.
            """
            prompt = f"""
            You are an expert legal drafter. Create precise legal language based on the following instruction and context:
            
            INSTRUCTION: {instruction}
            
            CONTEXT: {context}
            
            Ensure the language is legally precise, addresses all requirements, and follows standard legal drafting conventions.
            """
            
            try:
                response = self.direct_model.generate_content(prompt)
                return response.text
            except Exception as e:
                logger.error(f"Error in draft_legal_language: {e}")
                return "Error drafting legal language. Please provide clearer instructions."
        
        @tool
        def analyze_contract_risk(contract_text: str) -> str:
            """
            Analyze a contract for legal risks and vulnerabilities.
            Useful for identifying potential issues in contracts before they're signed.
            """
            prompt = f"""
            You are a contract risk expert. Perform a comprehensive risk assessment on the following contract:

            {contract_text[:6000]}

            For each identified risk:
            1. Name the risk and the specific clause it relates to
            2. Explain why it's problematic
            3. Rate severity (High/Medium/Low)
            4. Suggest specific language changes to mitigate the risk

            Focus on:
            - Ambiguous language
            - Unreasonable obligations
            - Missing protections
            - Liability exposure
            - Termination issues
            - Compliance concerns
            """
            
            try:
                response = self.direct_model.generate_content(prompt)
                return response.text
            except Exception as e:
                logger.error(f"Error in analyze_contract_risk: {e}")
                return "Error analyzing contract risk. Please check the contract format and try again."
        
        @tool
        def regulatory_compliance_check(document_text: str, jurisdiction: str, regulation_type: str) -> str:
            """
            Check a document for compliance with specific regulations.
            Useful for regulatory compliance assessment in different jurisdictions.
            """
            prompt = f"""
            You are a regulatory compliance expert. Analyze the following document for compliance with {regulation_type} regulations in {jurisdiction}:

            {document_text[:6000]}

            Provide:
            1. Compliance assessment (Compliant/Partially Compliant/Non-Compliant)
            2. Specific compliance issues found
            3. Required changes to achieve compliance
            4. Potential penalties or risks of non-compliance
            """
            
            try:
                response = self.direct_model.generate_content(prompt)
                return response.text
            except Exception as e:
                logger.error(f"Error in regulatory_compliance_check: {e}")
                return f"Error checking compliance with {regulation_type} in {jurisdiction}. Please try again with more specific parameters."
        
        @tool
        def legal_research_synthesis(research_question: str, specific_sources: Optional[List[str]] = None) -> str:
            """
            Conduct deep legal research on a specific question and synthesize the findings.
            Useful for comprehensive analysis of complex legal questions across multiple sources.
            """
            sources_text = ""
            if specific_sources:
                sources_text = "Focus specifically on these sources:\n" + "\n".join([f"- {s}" for s in specific_sources])
            
            prompt = f"""
            You are a legal research expert. Conduct comprehensive research on the following question:

            {research_question}

            {sources_text}

            Provide:
            1. A thorough analysis of the question across relevant legal authorities
            2. Conflicting viewpoints or circuit splits if they exist
            3. The majority and minority positions
            4. Trends in how the law is evolving on this question
            5. Practical implications for legal practitioners
            
            Use specific citations to support your analysis.
            """
            
            try:
                response = self.direct_model.generate_content(prompt)
                return response.text
            except Exception as e:
                logger.error(f"Error in legal_research_synthesis: {e}")
                return "Error synthesizing legal research. Please try a more specific research question."
        
        @tool
        def clause_rewriting_assistant(clause_text: str, improvement_goal: str) -> str:
            """
            Rewrite a legal clause to improve it based on a specific goal.
            Useful for drafting and improving contract language.
            """
            prompt = f"""
            You are an expert legal drafter specializing in precise contract language. 
            Rewrite the following clause to {improvement_goal}:

            ORIGINAL CLAUSE:
            {clause_text}

            Provide:
            1. The rewritten clause
            2. Explanation of changes made
            3. How the changes accomplish the stated goal
            4. Any potential side effects of the changes
            
            The rewritten clause should maintain legal validity while achieving the goal.
            """
            
            try:
                response = self.direct_model.generate_content(prompt)
                return response.text
            except Exception as e:
                logger.error(f"Error in clause_rewriting_assistant: {e}")
                return "Error rewriting clause. Please provide a clearer improvement goal."
        
        @tool
        def jurisdictional_analysis(legal_question: str, jurisdictions: List[str]) -> str:
            """
            Analyze how a legal question would be addressed in different jurisdictions.
            Useful for understanding differences in legal interpretation across jurisdictions.
            """
            jurisdictions_text = "\n".join([f"- {j}" for j in jurisdictions])
            
            prompt = f"""
            You are a comparative law expert. Analyze how the following legal question would be addressed in different jurisdictions:

            LEGAL QUESTION: {legal_question}

            JURISDICTIONS TO ANALYZE:
            {jurisdictions_text}

            For each jurisdiction, provide:
            1. The applicable law or legal framework
            2. How courts in that jurisdiction would likely rule
            3. Key cases or precedents from that jurisdiction (if available)
            4. Significant differences from other jurisdictions
            
            Conclude with a comparative analysis highlighting the major differences in approach.
            """
            
            try:
                response = self.direct_model.generate_content(prompt)
                return response.text
            except Exception as e:
                logger.error(f"Error in jurisdictional_analysis: {e}")
                return f"Error performing jurisdictional analysis. Please check the jurisdictions specified and try again."
                
        tools.extend([
            search_legal_precedents,
            analyze_legal_issues,
            draft_legal_language,
            analyze_contract_risk,
            regulatory_compliance_check,
            legal_research_synthesis,
            clause_rewriting_assistant,
            jurisdictional_analysis
        ])
        
        return tools
    
    def _setup_agent(self) -> AgentExecutor:
        """Set up the LangChain agent with memory and tools"""
        memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        
        system_message = """
        You are LegalAssistant, an advanced AI legal expert with specialized knowledge in various domains of law.
        You have access to:
        1. A database of legal precedents and case law
        2. Legal analysis capabilities
        3. Legal drafting expertise
        4. Contract risk analysis
        5. Regulatory compliance checking
        6. Legal research synthesis
        7. Clause rewriting capabilities
        
        Follow these principles in your analysis:
        1. Apply structured legal reasoning frameworks (IRAC, CREAC) to legal questions
        2. Consider multiple perspectives and counterarguments
        3. Always use specific legal authorities to support your conclusions
        4. Be transparent about areas of legal uncertainty or competing interpretations
        5. Identify practical implications alongside theoretical legal analysis
        
        When solving legal problems, you should:
        1. FIRST identify the key legal issues
        2. THEN determine which areas of law apply
        3. THEN search for relevant precedents when needed
        4. THEN apply legal reasoning to reach a conclusion
        5. ALWAYS cite relevant authorities for your conclusions
        6. ALWAYS consider jurisdictional differences and limitations
        
        You must think step-by-step but be concise in your final answers. Only use the tools when necessary to answer the question.
        """
        
        prompt = (
            SystemMessage(content=system_message)
            + MessagesPlaceholder(variable_name="chat_history")
            + "{input}"
            + MessagesPlaceholder(variable_name="agent_scratchpad")
        )
        
        agent = create_openai_tools_agent(self.llm, self.tools, prompt)
        
        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            memory=memory,
            verbose=True,
            max_iterations=5,
            early_stopping_method="generate"
        )
    
    def legal_query(self, query: str, context: Optional[str] = None, domain: Optional[str] = None) -> LegalAgentResponse:
        """Process a legal query with specialized legal reasoning and agentic capabilities"""
        start_time = time.time()
        
        # Validate and classify the query domain
        query_domain = domain or self._classify_legal_domain(query)
        logger.info(f"Query classified as domain: {query_domain}")
        
        # Create a multi-step reasoning plan for this query
        reasoning_plan = self._create_reasoning_plan(query, query_domain)
        logger.info(f"Created reasoning plan with {len(reasoning_plan)} steps")
        
        # Prepare agent input with the reasoning plan
        agent_input = {
            "input": f"""Domain: {query_domain}
Query: {query}
Context: {context or 'No additional context provided.'}

Reasoning Plan:
{self._format_reasoning_plan(reasoning_plan)}
"""
        }
        
        # Initialize default values for error handling
        response_text = ""
        reasoning_steps = []
        citations = []
        
        try:
            # Use agent executor for complex reasoning
            if self.agent_executor:
                agent_result = self.agent_executor.invoke(agent_input)
                response_text = agent_result.get("output", "")
                
                # Extract tool usage for reasoning steps
                intermediate_steps = agent_result.get("intermediate_steps", [])
                reasoning_steps = []
                
                for step in intermediate_steps:
                    if len(step) >= 2:
                        tool_name = getattr(step[0], "name", "Unknown Tool")
                        tool_input = getattr(step[0], "args", {})
                        tool_output = step[1]
                        reasoning_steps.append(f"{tool_name}: {json.dumps(tool_input)}\nResult: {tool_output}")
                
                # Apply self-reflection to improve the response
                reflection_result = self._apply_self_reflection(query, response_text, reasoning_steps, query_domain)
                
                # If reflection suggested improvements, update the response
                if reflection_result.get("improved_response"):
                    response_text = reflection_result["improved_response"]
                
                # If reasoning steps are empty, generate them using the domain reasoning structure
                if not reasoning_steps:
                    reasoning_steps = self._apply_legal_reasoning(query, context, query_domain)
            else:
                # Fallback to basic model if agent not available
                response_text, _ = self._generate_legal_response(query, context, [], [], query_domain)
                reasoning_steps = []
            
            # Extract citations from the response
            citations = self._extract_citations_from_text(response_text)
            
            # Calculate confidence score
            confidence_score = self._calculate_confidence(response_text, query, citations)
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Get additional metadata from reasoning process
            metadata = {
                "domain": query_domain, 
                "agent_used": bool(self.agent_executor),
                "reasoning_plan": reasoning_plan,
                "self_reflection_applied": bool(self.agent_executor)
            }
            
            return LegalAgentResponse(
                answer=response_text,
                citations=citations,
                reasoning_steps=reasoning_steps,
                confidence_score=confidence_score,
                sources_used=self._get_sources_used(query_domain),
                processing_time=processing_time,
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"Error in legal_query: {e}")
            # Return a graceful failure response
            processing_time = time.time() - start_time
            return LegalAgentResponse(
                answer=f"I encountered an error while processing your query: {str(e)}. Please try again or rephrase your question.",
                citations=[],
                reasoning_steps=[],
                confidence_score=0.0,
                sources_used=[],
                processing_time=processing_time,
                metadata={"error": str(e)}
            )
    
    def _create_reasoning_plan(self, query: str, domain: str) -> List[Dict[str, str]]:
        """Create a step-by-step reasoning plan based on query and domain"""
        if not self.direct_model:
            # Return a default plan if model not available
            return [
                {"step": "Issue identification", "description": "Identify key legal issues"},
                {"step": "Rule identification", "description": "Identify applicable rules"},
                {"step": "Analysis", "description": "Apply rules to facts"},
                {"step": "Conclusion", "description": "Draw legal conclusion"}
            ]
        
        prompt = f"""
        You are a legal reasoning expert. Create a step-by-step reasoning plan to answer the following legal query.
        
        QUERY: {query}
        DOMAIN: {domain}
        
        The plan should list the logical steps needed to thoroughly analyze this legal question.
        Each step should have a name and brief description of what that step accomplishes.
        
        Format your response as a JSON array of objects, each with "step" and "description" fields.
        Ensure steps follow a logical progression based on legal reasoning frameworks like IRAC or CREAC.
        
        For example:
        [
            {{"step": "Issue identification", "description": "Identify the key breach of contract issues"}},
            {{"step": "Contract law principles", "description": "Review applicable contract formation principles"}},
            ...
        ]
        """
        
        try:
            response = self.direct_model.generate_content(prompt)
            response_text = response.text
            
            # Extract JSON from the response
            json_start = response_text.find("[")
            json_end = response_text.rfind("]") + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                plan = json.loads(json_str)
                return plan
            
            # Fallback to default plan if JSON parsing fails
            logger.warning("Could not parse reasoning plan JSON, using default plan")
            return [
                {"step": "Issue identification", "description": "Identify key legal issues"},
                {"step": "Rule identification", "description": "Identify applicable rules"},
                {"step": "Analysis", "description": "Apply rules to facts"},
                {"step": "Conclusion", "description": "Draw legal conclusion"}
            ]
            
        except Exception as e:
            logger.error(f"Error creating reasoning plan: {e}")
            # Return a default plan if there's an error
            return [
                {"step": "Issue identification", "description": "Identify key legal issues"},
                {"step": "Rule identification", "description": "Identify applicable rules"},
                {"step": "Analysis", "description": "Apply rules to facts"},
                {"step": "Conclusion", "description": "Draw legal conclusion"}
            ]
    
    def _format_reasoning_plan(self, plan: List[Dict[str, str]]) -> str:
        """Format the reasoning plan for inclusion in the prompt"""
        formatted_plan = []
        for i, step in enumerate(plan):
            formatted_plan.append(f"{i+1}. {step['step']}: {step['description']}")
        return "\n".join(formatted_plan)
    
    def _apply_self_reflection(self, query: str, response: str, reasoning_steps: List[str], domain: str) -> Dict[str, Any]:
        """Apply self-reflection to improve the response"""
        if not self.direct_model:
            return {"improved_response": None}
        
        # Extract reasoning steps text
        reasoning_text = "\n".join(reasoning_steps)
        
        prompt = f"""
        You are a legal reasoning critic. Evaluate the quality of the following legal response and identify areas for improvement.
        
        QUERY: {query}
        DOMAIN: {domain}
        
        REASONING PROCESS:
        {reasoning_text}
        
        RESPONSE:
        {response}
        
        Reflect on these aspects:
        1. Are there missing elements in the legal analysis?
        2. Are there logical gaps in the reasoning?
        3. Are there insufficient citations or authorities?
        4. Are there areas of potential bias or one-sided analysis?
        5. Is the conclusion well-supported by the reasoning?
        
        Provide:
        1. A critique of the response (brief but specific)
        2. An improved version of the response that addresses the issues
        
        Format as JSON with fields "critique" and "improved_response".
        """
        
        try:
            reflection_response = self.direct_model.generate_content(prompt)
            reflection_text = reflection_response.text
            
            # Extract JSON from the response
            json_start = reflection_text.find("{")
            json_end = reflection_text.rfind("}") + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = reflection_text[json_start:json_end]
                reflection_data = json.loads(json_str)
                return reflection_data
            
            # If JSON parsing fails, return the original response
            return {"improved_response": None, "critique": "Could not parse reflection data"}
            
        except Exception as e:
            logger.error(f"Error in self-reflection: {e}")
            return {"improved_response": None, "critique": f"Error in reflection: {str(e)}"}
    
    def _classify_legal_domain(self, query: str) -> str:
        """Classify the query into a specific legal domain using specialized classification"""
        if not self.direct_model:
            return "general"
        
        prompt = f"""
        Classify the following legal query into the most appropriate legal domain:
        
        Query: {query}
        
        Respond with exactly one of the following domains:
        - contract_law
        - intellectual_property
        - corporate_law
        - criminal_law
        - constitutional_law
        - administrative_law
        - international_law
        - tax_law
        - employment_law
        - environmental_law
        - general
        """
        
        try:
            response = self.direct_model.generate_content(prompt)
            domain = response.text.strip().lower()
            # Ensure domain is valid
            if domain in self.legal_domains:
                return domain
            return "general"
        except Exception as e:
            logger.error(f"Error classifying domain: {e}")
            return "general"
    
    def _apply_legal_reasoning(self, query: str, context: Optional[str], domain: str) -> List[str]:
        """Apply specialized legal reasoning process to the query"""
        reasoning_steps = []
        
        # Define the reasoning structure based on domain
        reasoning_structure = self._get_domain_reasoning_structure(domain)
        
        # For each reasoning step, generate the specific legal analysis
        for step_name, step_prompt in reasoning_structure.items():
            formatted_prompt = step_prompt.format(query=query, context=context or "")
            
            try:
                if self.direct_model:
                    response = self.direct_model.generate_content(formatted_prompt)
                    reasoning_steps.append(f"{step_name}: {response.text.strip()}")
                else:
                    reasoning_steps.append(f"{step_name}: Unable to generate reasoning due to API limitations")
            except Exception as e:
                logger.error(f"Error in reasoning step {step_name}: {e}")
                reasoning_steps.append(f"{step_name}: Error in reasoning generation")
        
        return reasoning_steps
    
    def _get_domain_reasoning_structure(self, domain: str) -> Dict[str, str]:
        """Get the specialized reasoning structure for a specific legal domain"""
        # These would be more extensive in a real implementation
        base_structure = {
            "Issue Identification": "Identify the key legal issues in the following query: {query}\nContext: {context}",
            "Legal Framework": "What legal framework applies to this issue? Query: {query}\nContext: {context}",
            "Precedent Analysis": "What precedents are most relevant to this query? {query}\nContext: {context}",
            "Legal Analysis": "Analyze the query using the applicable legal framework and precedents: {query}\nContext: {context}",
            "Conclusion": "Provide a legal conclusion for the query: {query}\nContext: {context}"
        }
        
        # Domain-specific reasoning structures
        domain_structures = {
            "contract_law": {
                **base_structure,
                "Contract Elements": "Identify the essential contract elements relevant to: {query}\nContext: {context}",
                "Terms Analysis": "Analyze the contractual terms in: {query}\nContext: {context}"
            },
            "intellectual_property": {
                **base_structure,
                "IP Classification": "Classify the type of intellectual property in: {query}\nContext: {context}",
                "Ownership Analysis": "Analyze ownership and rights issues in: {query}\nContext: {context}"
            },
            # Other domains would have similar specialized structures
        }
        
        return domain_structures.get(domain, base_structure)
    
    def _extract_citations_from_text(self, text: str) -> List[LegalCitation]:
        """Extract legal citations from text"""
        # This is a simplified implementation
        citations = []
        
        # Example citation extraction based on patterns
        import re
        
        # Check for common citation formats
        for pattern_name, pattern in self.citation_patterns.items():
            matches = re.finditer(pattern, text)
            for match in matches:
                citation_text = match.group(0)
                
                # Extract year if possible
                year_match = re.search(r'\((\d{4})\)', citation_text)
                year = int(year_match.group(1)) if year_match else None
                
                citations.append(LegalCitation(
                    citation=citation_text,
                            year=year,
                    relevance_score=0.85  # Default score
                ))
        
        return citations
    
    def _generate_legal_response(
        self, query: str, context: Optional[str], 
        reasoning_steps: List[str], citations: List[LegalCitation], 
        domain: str
    ) -> Tuple[str, float]:
        """Generate the final legal response with specialized legal knowledge"""
        if not self.direct_model:
            return "Unable to generate response: API key not configured", 0.0
        
        # Prepare citations for inclusion in the prompt
        citations_text = "\n".join([f"- {c.citation}" for c in citations])
        
        # Prepare reasoning steps for inclusion in the prompt
        reasoning_text = "\n".join(reasoning_steps)
        
        # Create a specialized legal prompt template based on domain
        prompt = f"""
        You are a specialized legal AI assistant with expertise in {domain}. Generate a comprehensive legal response to the query below.
        
        QUERY: {query}
        
        CONTEXT: {context or "No additional context provided."}
        
        REASONING PROCESS:
        {reasoning_text}
        
        RELEVANT LEGAL CITATIONS:
        {citations_text or "No specific citations provided."}
        
        Your response should:
        1. Start with a clear, direct answer to the legal question
        2. Support your answer with relevant legal reasoning
        3. Cite specific legal authorities where appropriate
        4. Explain any nuances or limitations in your analysis
        5. Use formal legal writing style
        6. End with a concise conclusion
        
        Also provide a confidence score between 0.0 and 1.0 that represents your confidence in this answer, formatted as [CONFIDENCE: X.XX]
        """
        
        try:
            response = self.direct_model.generate_content(prompt)
            response_text = response.text
            
            # Extract confidence score if present
            confidence = 0.85  # Default value
            if "[CONFIDENCE:" in response_text:
                confidence_parts = response_text.split("[CONFIDENCE:")
                if len(confidence_parts) > 1:
                    confidence_text = confidence_parts[1].split("]")[0].strip()
                    try:
                        confidence = float(confidence_text)
                        # Remove the confidence marker from the response
                        response_text = response_text.replace(f"[CONFIDENCE: {confidence_text}]", "").strip()
                    except ValueError:
                        pass
            
            return response_text, confidence
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"Error generating legal response: {str(e)}", 0.0
    
    def _calculate_confidence(self, response: str, query: str, citations: List[LegalCitation]) -> float:
        """Calculate confidence score based on response quality, citation relevance, etc."""
        # Start with a base confidence
        confidence = 0.7
        
        # Adjust based on number and quality of citations
        if citations:
            avg_citation_relevance = sum(c.relevance_score for c in citations) / len(citations)
            confidence += min(0.15, avg_citation_relevance * 0.2)  # Max boost of 0.15
        else:
            confidence -= 0.1  # Penalty for no citations
        
        # Adjust based on response length (assuming longer responses are more thorough)
        response_length = len(response.split())
        if response_length > 500:
            confidence += 0.05
        elif response_length < 100:
            confidence -= 0.1
        
        # Cap confidence between 0 and 1
        return min(1.0, max(0.0, confidence))
    
    def _get_sources_used(self, domain: str) -> List[str]:
        """Get the sources used for this query based on domain"""
        # This would be more sophisticated in a real implementation
        base_sources = ["Case Law Database", "Legal Knowledge Graph"]
        
        domain_sources = {
            "contract_law": base_sources + ["Contract Law Treaties", "UCC Provisions"],
            "intellectual_property": base_sources + ["Patent Office Records", "Copyright Registry"],
            "tax_law": base_sources + ["IRS Regulations", "Tax Court Decisions"],
            # Other domains would have similar specific sources
        }
        
        return domain_sources.get(domain, base_sources)

    def analyze_document(self, document_text: str, document_type: str = "general") -> Dict[str, Any]:
        """Analyze a legal document with specialized understanding of document structure and legal implications"""
        if not self.direct_model:
            return {"error": "API key not configured"}
        
        start_time = time.time()
        
        # Determine the document type-specific analysis approach
        analysis_prompts = self._get_document_analysis_prompts(document_type)
        
        # Run specialized analysis for each component
        analysis_results = {}
        for component, prompt_template in analysis_prompts.items():
            prompt = prompt_template.format(document=document_text[:8000])  # Limit text length
            try:
                response = self.direct_model.generate_content(prompt)
                analysis_results[component] = response.text
            except Exception as e:
                logger.error(f"Error analyzing document {component}: {e}")
                analysis_results[component] = f"Error: {str(e)}"
        
        # Extract key clauses and terms if applicable
        if document_type in ["contract", "agreement", "terms_of_service"]:
            analysis_results["key_clauses"] = self._extract_key_clauses(document_text)
        
        # Extract legal citations from the document
        analysis_results["citations"] = [c.dict() for c in self._extract_citations_from_text(document_text)]
        
        # Add metadata
        analysis_results["document_type"] = document_type
        analysis_results["processing_time"] = time.time() - start_time
        analysis_results["timestamp"] = datetime.now().isoformat()
        
        return analysis_results
    
    def _get_document_analysis_prompts(self, document_type: str) -> Dict[str, str]:
        """Get specialized analysis prompts based on document type"""
        # Base analysis components for all documents
        base_prompts = {
            "summary": "Provide a concise legal summary of the following document:\n\n{document}",
            "key_points": "Extract the key legal points from the following document:\n\n{document}",
            "parties": "Identify all parties mentioned in the following document and their roles:\n\n{document}",
            "obligations": "Identify the key legal obligations in the following document:\n\n{document}",
            "risks": "Identify potential legal risks in the following document:\n\n{document}"
        }
        
        # Document type-specific analysis components
        type_specific_prompts = {
            "contract": {
                **base_prompts,
                "consideration": "Identify the consideration exchanged in this contract:\n\n{document}",
                "termination": "Analyze the termination clauses in this contract:\n\n{document}",
                "dispute_resolution": "Analyze the dispute resolution mechanisms in this contract:\n\n{document}"
            },
            "court_filing": {
                **base_prompts,
                "claims": "Identify the legal claims in this court filing:\n\n{document}",
                "remedies": "Identify the remedies sought in this court filing:\n\n{document}",
                "legal_standards": "Identify the legal standards referenced in this filing:\n\n{document}"
            },
            "legislation": {
                **base_prompts,
                "scope": "Analyze the scope and applicability of this legislation:\n\n{document}",
                "definitions": "Extract key definitions from this legislation:\n\n{document}",
                "enforcement": "Analyze the enforcement mechanisms in this legislation:\n\n{document}"
            },
            # Other document types would have similar specialized prompts
        }
        
        return type_specific_prompts.get(document_type, base_prompts)
    
    def _extract_key_clauses(self, document_text: str) -> List[Dict[str, Any]]:
        """Extract key clauses from legal documents with their implications"""
        if not self.direct_model:
            return []
        
        prompt = f"""
        Extract the 5-10 most important clauses from the following legal document.
        For each clause:
        1. Provide the clause name/title
        2. Quote the relevant text (keep it brief)
        3. Explain its legal significance
        4. Rate its risk level (Low, Medium, High)
        
        Format as JSON array of objects with fields: name, text, significance, risk_level
        
        DOCUMENT:
        {document_text[:8000]}  # Limit text length
        """
        
        try:
            response = self.direct_model.generate_content(prompt)
            response_text = response.text
            
            # Extract JSON from the response
            json_start = response_text.find("[")
            json_end = response_text.rfind("]") + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                return json.loads(json_str)
            return []
            
        except Exception as e:
            logger.error(f"Error extracting key clauses: {e}")
            return []
    
    def compare_documents(self, doc1_text: str, doc2_text: str, comparison_type: str = "general") -> Dict[str, Any]:
        """Compare two legal documents with specialized legal comparison capabilities"""
        if not self.direct_model:
            return {"error": "API key not configured"}
        
        start_time = time.time()
        
        # Get specialized comparison approach based on document type
        comparison_prompts = self._get_document_comparison_prompts(comparison_type)
        
        # Run specialized comparisons for each component
        comparison_results = {}
        for component, prompt_template in comparison_prompts.items():
            # Limit text length to avoid token limits
            prompt = prompt_template.format(
                doc1=doc1_text[:4000],
                doc2=doc2_text[:4000]
            )
            
            try:
                response = self.direct_model.generate_content(prompt)
                comparison_results[component] = response.text
            except Exception as e:
                logger.error(f"Error comparing documents {component}: {e}")
                comparison_results[component] = f"Error: {str(e)}"
        
        # Add specialized metrics for legal document comparison
        if comparison_type == "contract":
            comparison_results["risk_shift"] = self._analyze_risk_shift(doc1_text, doc2_text)
        
        # Add metadata
        comparison_results["comparison_type"] = comparison_type
        comparison_results["processing_time"] = time.time() - start_time
        comparison_results["timestamp"] = datetime.now().isoformat()
        
        return comparison_results
    
    def _get_document_comparison_prompts(self, comparison_type: str) -> Dict[str, str]:
        """Get specialized comparison prompts based on document type"""
        # Base comparison components for all documents
        base_prompts = {
            "summary": "Provide a summary of the key differences between these two documents:\n\nDOCUMENT 1:\n{doc1}\n\nDOCUMENT 2:\n{doc2}",
            "additions": "Identify significant additions in Document 2 that don't appear in Document 1:\n\nDOCUMENT 1:\n{doc1}\n\nDOCUMENT 2:\n{doc2}",
            "deletions": "Identify significant deletions in Document 2 compared to Document 1:\n\nDOCUMENT 1:\n{doc1}\n\nDOCUMENT 2:\n{doc2}",
            "modifications": "Identify significant modifications between Document 1 and Document 2:\n\nDOCUMENT 1:\n{doc1}\n\nDOCUMENT 2:\n{doc2}"
        }
        
        # Document type-specific comparison components
        type_specific_prompts = {
            "contract": {
                **base_prompts,
                "obligation_changes": "Analyze how obligations have changed between these two contracts:\n\nCONTRACT 1:\n{doc1}\n\nCONTRACT 2:\n{doc2}",
                "risk_allocation": "Analyze how risk allocation has changed between these two contracts:\n\nCONTRACT 1:\n{doc1}\n\nCONTRACT 2:\n{doc2}",
                "term_changes": "Analyze changes in key terms between these two contracts:\n\nCONTRACT 1:\n{doc1}\n\nCONTRACT 2:\n{doc2}"
            },
            "legislation": {
                **base_prompts,
                "scope_changes": "Analyze how the scope has changed between these two versions:\n\nVERSION 1:\n{doc1}\n\nVERSION 2:\n{doc2}",
                "penalty_changes": "Analyze how penalties or enforcement has changed between these two versions:\n\nVERSION 1:\n{doc1}\n\nVERSION 2:\n{doc2}",
                "compliance_impact": "Analyze how compliance requirements have changed between these two versions:\n\nVERSION 1:\n{doc1}\n\nVERSION 2:\n{doc2}"
            },
            # Other comparison types would have similar specialized prompts
        }
        
        return type_specific_prompts.get(comparison_type, base_prompts)
    
    def _analyze_risk_shift(self, doc1_text: str, doc2_text: str) -> Dict[str, Any]:
        """Analyze how risk has shifted between two legal documents"""
        if not self.direct_model:
            return {"error": "API key not configured"}
        
        prompt = f"""
        Analyze how legal risk has shifted between these two legal documents. 
        Identify which party benefits from the changes and quantify the risk shift.
        
        Format your response as JSON with these fields:
        - risk_shift_direction (String: "toward_party_1", "toward_party_2", or "neutral")
        - risk_shift_magnitude (Float: 0.0 to 1.0 where 1.0 is maximum shift)
        - party_1_risk_increase (Array of specific risk increases for party 1)
        - party_2_risk_increase (Array of specific risk increases for party 2)
        - key_risk_clauses (Array of the clauses with the most significant risk changes)
        
        DOCUMENT 1:
        {doc1_text[:4000]}
        
        DOCUMENT 2:
        {doc2_text[:4000]}
        """
        
        try:
            response = self.direct_model.generate_content(prompt)
            response_text = response.text
            
            # Extract JSON from the response
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                return json.loads(json_str)
            
            # Fallback if JSON parsing fails
            return {
                "risk_shift_direction": "unknown",
                "risk_shift_magnitude": 0.0,
                "analysis": response_text
            }
            
        except Exception as e:
            logger.error(f"Error analyzing risk shift: {e}")
            return {"error": str(e)}

    def analyze_jurisdictional_differences(self, query: str, jurisdictions: List[str]) -> Dict[str, Any]:
        """Analyze legal differences across jurisdictions for a specific query"""
        if not self.direct_model:
            return {"error": "API key not configured"}
        
        start_time = time.time()
        
        try:
            # Format jurisdictions list for the prompt
            jurisdictions_text = "\n".join([f"- {j}" for j in jurisdictions])
            
            prompt = f"""
            You are a comparative law expert. Analyze the following legal question across multiple jurisdictions:
            
            LEGAL QUESTION: {query}
            
            JURISDICTIONS:
            {jurisdictions_text}
            
            For each jurisdiction, analyze:
            1. Applicable statutes and regulations
            2. Key court precedents and their holdings
            3. Procedural requirements
            4. Recent developments or pending changes
            
            Provide a comparative analysis that highlights:
            1. Major substantive differences
            2. Procedural differences
            3. Enforcement differences
            4. Practical implications for legal strategy
            
            Format your response as structured analysis by jurisdiction, followed by a comparative summary.
            """
            
            response = self.direct_model.generate_content(prompt)
            
            # Build the return structure
            results = {
                "analysis": response.text,
                "jurisdictions": jurisdictions,
                "query": query,
                "processing_time": time.time() - start_time,
                "timestamp": datetime.now().isoformat()
            }
            
            return results
            
        except Exception as e:
            logger.error(f"Error in jurisdictional analysis: {e}")
            return {
                "error": str(e),
                "jurisdictions": jurisdictions,
                "query": query,
                "processing_time": time.time() - start_time
            } 