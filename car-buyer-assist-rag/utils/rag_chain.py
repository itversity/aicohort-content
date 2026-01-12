"""
RAG Chain Utility Module

This module handles the complete RAG query-response pipeline:
- Query processing and embedding generation
- Similarity search in ChromaDB
- Context assembly from retrieved chunks
- Response generation using Vertex AI
- Citation extraction and formatting

Follows Design Document specifications (Section 3.2)
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

# LangChain imports
from langchain_google_vertexai import VertexAIEmbeddings, ChatVertexAI
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document

# ChromaDB
import chromadb


# System prompt as per Design Document Section 3.2
SYSTEM_PROMPT = """You are a helpful Toyota car sales assistant. Answer questions based ONLY on the provided context from Toyota specification documents.

Guidelines:
- Use ONLY the information provided in the context below
- If the information is not in the context, say "I don't have that information in the available Toyota specifications."
- Always cite the source document when providing answers
- Be concise and accurate
- Format your response clearly

Context:
{context}

Question: {question}

Answer:"""


def get_vectorstore(
    db_path: str = "./chroma_db",
    collection_name: str = "toyota_specs",
    config: Optional[Dict[str, Any]] = None
) -> Tuple[Chroma, VertexAIEmbeddings]:
    """
    Get ChromaDB vectorstore with embeddings model.
    
    Args:
        db_path: Path to ChromaDB persistence directory
        collection_name: Name of the collection
        config: Configuration dictionary with GCP settings
    
    Returns:
        Tuple of (vectorstore, embeddings_model)
    """
    # Initialize embeddings model
    embeddings = VertexAIEmbeddings(
        model_name="text-embedding-004",
        project=config.get('google', {}).get('project_id') if config else None,
        location=config.get('google', {}).get('region') if config else None
    )
    
    # Initialize ChromaDB client
    client = chromadb.PersistentClient(path=db_path)
    
    # Create LangChain wrapper
    vectorstore = Chroma(
        client=client,
        collection_name=collection_name,
        embedding_function=embeddings
    )
    
    return vectorstore, embeddings


def format_context_from_documents(documents: List[Document]) -> str:
    """
    Format retrieved documents into a context string for the LLM.
    
    Args:
        documents: List of retrieved Document objects
    
    Returns:
        Formatted context string
    """
    if not documents:
        return "No relevant information found."
    
    context_parts = []
    for idx, doc in enumerate(documents, 1):
        source = doc.metadata.get('source', 'Unknown')
        model_name = doc.metadata.get('model_name', 'Unknown')
        page = doc.metadata.get('page', 'N/A')
        
        context_parts.append(
            f"[Source {idx}: {source} - {model_name}, Page {page}]\n{doc.page_content}\n"
        )
    
    return "\n---\n".join(context_parts)


def extract_unique_sources(documents: List[Document]) -> List[str]:
    """
    Extract unique source document names from retrieved documents.
    
    Args:
        documents: List of retrieved Document objects
    
    Returns:
        List of unique source filenames
    """
    sources = set()
    for doc in documents:
        source = doc.metadata.get('source')
        if source:
            sources.add(source)
    
    return sorted(list(sources))


def query_rag_system(
    query: str,
    config: Dict[str, Any],
    top_k: int = 5,
    temperature: float = 0.3,
    max_tokens: int = 1024
) -> Dict[str, Any]:
    """
    Main entry point for RAG query processing.
    
    Args:
        query: User's natural language question
        config: Configuration dictionary with:
            - google.project_id
            - google.region
            - chromadb.path
        top_k: Number of chunks to retrieve (default: 5)
        temperature: LLM temperature (default: 0.3)
        max_tokens: Maximum output tokens (default: 1024)
    
    Returns:
        Dictionary with:
        {
            'success': bool,
            'response': str,
            'sources': list of source documents,
            'retrieved_chunks': int,
            'processing_time': float,
            'error': str (if success=False)
        }
    """
    start_time = datetime.now()
    
    try:
        # Step 1: Get vectorstore and embeddings
        vectorstore, embeddings = get_vectorstore(
            db_path=config.get('chromadb', {}).get('path', './chroma_db'),
            collection_name="toyota_specs",
            config=config
        )
        
        # Step 2: Perform similarity search
        retrieved_docs = vectorstore.similarity_search(
            query=query,
            k=top_k
        )
        
        if not retrieved_docs:
            return {
                'success': True,
                'response': "I don't have that information in the available Toyota specifications.",
                'sources': [],
                'retrieved_chunks': 0,
                'processing_time': (datetime.now() - start_time).total_seconds()
            }
        
        # Step 3: Format context
        context = format_context_from_documents(retrieved_docs)
        
        # Step 4: Extract sources for citation
        sources = extract_unique_sources(retrieved_docs)
        
        # Step 5: Create prompt
        prompt_template = ChatPromptTemplate.from_template(SYSTEM_PROMPT)
        formatted_prompt = prompt_template.format(
            context=context,
            question=query
        )
        
        # Step 6: Initialize LLM and generate response
        llm = ChatVertexAI(
            model="gemini-2.5-pro",
            project=config.get('google', {}).get('project_id'),
            location=config.get('google', {}).get('region'),
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # Generate response (LangSmith will auto-trace if configured)
        response = llm.invoke(formatted_prompt)
        response_text = response.content if hasattr(response, 'content') else str(response)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return {
            'success': True,
            'response': response_text,
            'sources': sources,
            'retrieved_chunks': len(retrieved_docs),
            'processing_time': processing_time
        }
        
    except Exception as e:
        processing_time = (datetime.now() - start_time).total_seconds()
        return {
            'success': False,
            'error': str(e),
            'processing_time': processing_time
        }


def format_response_with_citations(response: str, sources: List[str]) -> str:
    """
    Format response text with citation information.
    
    Args:
        response: Generated response text
        sources: List of source document filenames
    
    Returns:
        Formatted response with citations
    """
    if not sources:
        return response
    
    if len(sources) == 1:
        citation = f"\n\n*Source: {sources[0]}*"
    else:
        citation = f"\n\n*Sources: {', '.join(sources)}*"
    
    return response + citation


def create_rag_chain(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Initialize RAG components and return them for reuse.
    
    Args:
        config: Configuration dictionary with GCP and ChromaDB settings
    
    Returns:
        Dictionary with initialized components
    """
    try:
        vectorstore, embeddings = get_vectorstore(
            db_path=config.get('chromadb', {}).get('path', './chroma_db'),
            collection_name="toyota_specs",
            config=config
        )
        
        llm = ChatVertexAI(
            model="gemini-2.5-pro",
            project=config.get('google', {}).get('project_id'),
            location=config.get('google', {}).get('region'),
            temperature=0.3,
            max_tokens=1024
        )
        
        return {
            'success': True,
            'vectorstore': vectorstore,
            'embeddings': embeddings,
            'llm': llm
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

