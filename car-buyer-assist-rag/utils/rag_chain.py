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

# Streamlit for caching
import streamlit as st

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


@st.cache_resource
def get_cached_vectorstore(db_path: str, collection_name: str, project_id: str, region: str) -> Tuple[Chroma, VertexAIEmbeddings]:
    """Cache vectorstore to avoid recreating on every query.
    
    Args:
        db_path: Path to ChromaDB persistence directory
        collection_name: Name of the collection
        project_id: GCP project ID
        region: GCP region
    
    Returns:
        Tuple of (vectorstore, embeddings_model)
    """
    # Initialize embeddings model
    embeddings = VertexAIEmbeddings(
        model_name="text-embedding-004",
        project=project_id,
        location=region
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


@st.cache_resource
def get_cached_llm(project_id: str, region: str, model: str = "gemini-2.0-flash-exp", 
                   temperature: float = 0.3, max_tokens: int = 1024) -> ChatVertexAI:
    """Cache LLM instance to avoid recreating on every query.
    
    Args:
        project_id: GCP project ID
        region: GCP region
        model: Model name (default: gemini-2.0-flash-exp)
        temperature: LLM temperature
        max_tokens: Maximum output tokens
    
    Returns:
        Cached ChatVertexAI instance
    """
    return ChatVertexAI(
        model=model,
        project=project_id,
        location=region,
        temperature=temperature,
        max_output_tokens=max_tokens
    )


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
    conversation_history: Optional[List[Dict]] = None,
    top_k: int = 5,
    temperature: float = 0.3,
    max_tokens: int = 1024
) -> Dict[str, Any]:
    """
    Main entry point for RAG query processing with optional conversation context.
    
    Args:
        query: User's natural language question
        config: Configuration dictionary with:
            - google.project_id
            - google.region
            - chromadb.path
            - google.model (optional)
        conversation_history: Optional list of previous messages for context
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
            'error': str (if success=False),
            'error_type': str (if success=False)
        }
    """
    start_time = datetime.now()
    
    try:
        # Extract config values
        project_id = config.get('google', {}).get('project_id')
        region = config.get('google', {}).get('region')
        db_path = config.get('chromadb', {}).get('path', './chroma_db')
        model_name = config.get('google', {}).get('model', 'gemini-2.0-flash-exp')
        
        # Step 1: Get cached vectorstore and embeddings
        vectorstore, embeddings = get_cached_vectorstore(
            db_path=db_path,
            collection_name="toyota_specs",
            project_id=project_id,
            region=region
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
        
        # Step 5: Build conversation context if provided
        conv_context = ""
        if conversation_history and len(conversation_history) > 0:
            conv_context = "Previous Conversation:\n"
            # Use last 6 messages (3 exchanges)
            for msg in conversation_history[-6:]:
                if msg['role'] == 'user':
                    conv_context += f"Previous Question: {msg['content']}\n"
                elif msg['role'] == 'assistant':
                    # Truncate long responses
                    content = msg['content'][:200] + "..." if len(msg['content']) > 200 else msg['content']
                    conv_context += f"Previous Answer: {content}\n"
            conv_context += "\n"
        
        # Step 6: Create prompt with optional conversation context
        if conv_context:
            enhanced_prompt = f"""{conv_context}{SYSTEM_PROMPT}"""
            prompt_template = ChatPromptTemplate.from_template(enhanced_prompt)
        else:
            prompt_template = ChatPromptTemplate.from_template(SYSTEM_PROMPT)
        
        formatted_prompt = prompt_template.format(
            context=context,
            question=query
        )
        
        # Step 7: Get cached LLM and generate response
        llm = get_cached_llm(
            project_id=project_id,
            region=region,
            model=model_name,
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
    
    # Specific exception handling for better error messages
    except ImportError as e:
        if 'google' in str(e).lower():
            return {
                'success': False,
                'error': 'Google Cloud dependencies not found. Please check installation.',
                'error_type': 'import_error',
                'processing_time': (datetime.now() - start_time).total_seconds()
            }
        return {
            'success': False,
            'error': f'Import error: {str(e)}',
            'error_type': 'import_error',
            'processing_time': (datetime.now() - start_time).total_seconds()
        }
    
    except Exception as e:
        error_str = str(e).lower()
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Categorize errors
        if 'not found' in error_str or '404' in error_str:
            return {
                'success': False,
                'error': 'Model not found. Please check model configuration in settings.',
                'error_type': 'model_not_found',
                'processing_time': processing_time
            }
        elif 'rate limit' in error_str or 'quota' in error_str or '429' in error_str:
            return {
                'success': False,
                'error': 'API rate limit exceeded. Please wait a moment and try again.',
                'error_type': 'rate_limit',
                'processing_time': processing_time
            }
        elif 'timeout' in error_str or 'deadline' in error_str:
            return {
                'success': False,
                'error': 'Request timed out. Please try again.',
                'error_type': 'timeout',
                'processing_time': processing_time
            }
        elif 'connection' in error_str or 'network' in error_str:
            return {
                'success': False,
                'error': 'Connection failed. Please check your internet connection.',
                'error_type': 'connection_error',
                'processing_time': processing_time
            }
        else:
            return {
                'success': False,
                'error': str(e),
                'error_type': 'unknown',
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
    Initialize RAG components and return them for reuse (uses cached resources).
    
    Args:
        config: Configuration dictionary with GCP and ChromaDB settings
    
    Returns:
        Dictionary with initialized components
    """
    try:
        project_id = config.get('google', {}).get('project_id')
        region = config.get('google', {}).get('region')
        db_path = config.get('chromadb', {}).get('path', './chroma_db')
        model_name = config.get('google', {}).get('model', 'gemini-2.0-flash-exp')
        
        # Use cached functions
        vectorstore, embeddings = get_cached_vectorstore(
            db_path=db_path,
            collection_name="toyota_specs",
            project_id=project_id,
            region=region
        )
        
        llm = get_cached_llm(
            project_id=project_id,
            region=region,
            model=model_name,
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

