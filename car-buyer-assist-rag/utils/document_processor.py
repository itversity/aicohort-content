"""
Document Processor Utility Module

This module handles the complete document processing pipeline for the RAG system:
- PDF text extraction
- Text chunking
- Embedding generation
- Vector storage in ChromaDB

Follows Design Document specifications (Section 3.1)
"""

import os
import re
import tempfile
from pathlib import Path
from typing import Dict, List, Any, Callable, Optional, Tuple
from datetime import datetime

# LangChain imports
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_vertexai import VertexAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

# ChromaDB
import chromadb


def extract_model_name(filename: str) -> str:
    """
    Extract vehicle model name from PDF filename.
    
    Args:
        filename: PDF filename (e.g., "Toyota_Camry_Specifications.pdf")
    
    Returns:
        Model name (e.g., "Camry") or "Unknown" if pattern doesn't match
    
    Examples:
        "Toyota_Camry_Specifications.pdf" -> "Camry"
        "Toyota_RAV4_Specifications.pdf" -> "RAV4"
        "Introduction_to_Toyota_Car_Sales.pdf" -> "Introduction"
    """
    # Remove .pdf extension
    name = filename.replace('.pdf', '').replace('.PDF', '')
    
    # Pattern 1: Toyota_ModelName_Specifications
    pattern1 = r'Toyota_([A-Za-z0-9]+)_Specifications'
    match = re.search(pattern1, name)
    if match:
        return match.group(1)
    
    # Pattern 2: Any file with Toyota in name, extract word after Toyota_
    pattern2 = r'Toyota_([A-Za-z0-9]+)'
    match = re.search(pattern2, name)
    if match:
        return match.group(1)
    
    # Pattern 3: Introduction or other special files
    if 'Introduction' in name:
        return 'Introduction'
    
    # Default: return first significant word
    words = name.split('_')
    significant_words = [w for w in words if len(w) > 2 and w.lower() not in ['the', 'and', 'for']]
    return significant_words[0] if significant_words else 'Unknown'


def get_chromadb_collection(
    db_path: str = "./chroma_db",
    collection_name: str = "toyota_specs",
    embedding_function: Optional[Any] = None
) -> Tuple[Any, chromadb.Collection]:
    """
    Get or create a ChromaDB collection.
    
    Args:
        db_path: Path to ChromaDB persistence directory
        collection_name: Name of the collection
        embedding_function: LangChain embedding function (optional for metadata-only access)
    
    Returns:
        Tuple of (vectorstore, raw_collection)
        - vectorstore: LangChain Chroma wrapper (None if no embedding_function)
        - raw_collection: Direct ChromaDB collection object
    """
    # Create persistence directory if it doesn't exist
    os.makedirs(db_path, exist_ok=True)
    
    # Initialize ChromaDB client with persistence
    client = chromadb.PersistentClient(path=db_path)
    
    # Get or create collection
    try:
        collection = client.get_collection(name=collection_name)
    except:
        collection = client.create_collection(
            name=collection_name,
            metadata={"description": "Toyota vehicle specifications for RAG"}
        )
    
    # Create LangChain wrapper if embedding function provided
    vectorstore = None
    if embedding_function:
        vectorstore = Chroma(
            client=client,
            collection_name=collection_name,
            embedding_function=embedding_function
        )
    
    return vectorstore, collection


def get_collection_stats(db_path: str = "./chroma_db", collection_name: str = "toyota_specs") -> Dict[str, Any]:
    """
    Get statistics about the current ChromaDB collection.
    
    Args:
        db_path: Path to ChromaDB persistence directory
        collection_name: Name of the collection
    
    Returns:
        Dictionary with collection statistics
    """
    try:
        client = chromadb.PersistentClient(path=db_path)
        collection = client.get_collection(name=collection_name)
        
        # Get count
        count = collection.count()
        
        # Get all metadata to analyze
        if count > 0:
            results = collection.get(limit=count, include=['metadatas'])
            metadatas = results.get('metadatas', [])
            
            # Extract unique sources and models
            sources = set()
            models = set()
            for meta in metadatas:
                if meta.get('source'):
                    sources.add(meta['source'])
                if meta.get('model_name'):
                    models.add(meta['model_name'])
            
            return {
                'total_chunks': count,
                'total_documents': len(sources),
                'models_covered': list(models),
                'sources': list(sources),
                'exists': True
            }
        else:
            return {
                'total_chunks': 0,
                'total_documents': 0,
                'models_covered': [],
                'sources': [],
                'exists': True
            }
    except Exception as e:
        return {
            'total_chunks': 0,
            'total_documents': 0,
            'models_covered': [],
            'sources': [],
            'exists': False,
            'error': str(e)
        }


def process_single_pdf(
    file_path: str,
    embeddings_model: VertexAIEmbeddings,
    vectorstore: Any,
    progress_callback: Optional[Callable[[str, float], None]] = None
) -> Dict[str, Any]:
    """
    Process a single PDF through the complete RAG pipeline.
    
    Args:
        file_path: Path to PDF file
        embeddings_model: Vertex AI embeddings model
        vectorstore: ChromaDB vectorstore (LangChain wrapper)
        progress_callback: Optional callback function(message: str, progress: float)
    
    Returns:
        Dictionary with processing results:
        {
            'success': bool,
            'filename': str,
            'model_name': str,
            'chunks_created': int,
            'processing_time': float,
            'error': str (if success=False)
        }
    """
    start_time = datetime.now()
    filename = Path(file_path).name
    
    try:
        # Extract model name
        model_name = extract_model_name(filename)
        
        # Step 1: Extract text from PDF
        if progress_callback:
            progress_callback(f"Extracting text from {filename}...", 0.25)
        
        loader = PyPDFLoader(file_path)
        pages = loader.load()
        
        if not pages:
            return {
                'success': False,
                'filename': filename,
                'error': 'No content extracted from PDF'
            }
        
        # Step 2: Chunk text
        if progress_callback:
            progress_callback(f"Chunking text from {filename}...", 0.50)
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        chunks = text_splitter.split_documents(pages)
        
        # Add metadata to chunks
        for idx, chunk in enumerate(chunks):
            chunk.metadata['source'] = filename
            chunk.metadata['chunk_index'] = idx
            chunk.metadata['model_name'] = model_name
            # page is already in metadata from PyPDFLoader
        
        # Step 3: Generate embeddings and store
        if progress_callback:
            progress_callback(f"Generating embeddings for {filename}...", 0.75)
        
        # Add documents to vectorstore (embeddings generated automatically)
        vectorstore.add_documents(chunks)
        
        if progress_callback:
            progress_callback(f"Completed processing {filename}", 1.0)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return {
            'success': True,
            'filename': filename,
            'model_name': model_name,
            'chunks_created': len(chunks),
            'processing_time': processing_time,
            'pages_processed': len(pages)
        }
        
    except Exception as e:
        processing_time = (datetime.now() - start_time).total_seconds()
        return {
            'success': False,
            'filename': filename,
            'error': str(e),
            'processing_time': processing_time
        }


def batch_process_pdfs(
    uploaded_files: List[Any],
    config: Dict[str, Any],
    progress_callback: Optional[Callable[[str, float, Dict], None]] = None
) -> Dict[str, Any]:
    """
    Process multiple PDFs through the RAG pipeline.
    
    Args:
        uploaded_files: List of Streamlit UploadedFile objects
        config: Configuration dictionary with:
            - google.project_id
            - google.region
            - google.credentials_path
            - chromadb.path
        progress_callback: Optional callback(message: str, overall_progress: float, result: dict)
    
    Returns:
        Dictionary with batch processing results:
        {
            'success': bool,
            'total_files': int,
            'successful_files': int,
            'failed_files': int,
            'total_chunks': int,
            'total_time': float,
            'models_covered': list,
            'results': list of individual results,
            'error': str (if critical failure)
        }
    """
    start_time = datetime.now()
    results = []
    total_chunks = 0
    models_covered = set()
    
    try:
        # Initialize embeddings model
        embeddings = VertexAIEmbeddings(
            model_name="text-embedding-004",
            project=config['google']['project_id'],
            location=config['google']['region']
        )
        
        # Get or create ChromaDB collection
        vectorstore, _ = get_chromadb_collection(
            db_path=config['chromadb']['path'],
            collection_name="toyota_specs",
            embedding_function=embeddings
        )
        
        # Process each file
        total_files = len(uploaded_files)
        
        for idx, uploaded_file in enumerate(uploaded_files):
            # Save uploaded file to temporary location
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                tmp_file.write(uploaded_file.read())
                tmp_path = tmp_file.name
            
            try:
                # Process PDF
                def file_progress(message, file_progress):
                    # Calculate overall progress
                    overall = (idx + file_progress) / total_files
                    if progress_callback:
                        progress_callback(message, overall, None)
                
                result = process_single_pdf(
                    file_path=tmp_path,
                    embeddings_model=embeddings,
                    vectorstore=vectorstore,
                    progress_callback=file_progress
                )
                
                results.append(result)
                
                if result['success']:
                    total_chunks += result['chunks_created']
                    models_covered.add(result['model_name'])
                
                # Report individual file completion
                if progress_callback:
                    progress_callback(
                        f"Completed {idx + 1}/{total_files} files",
                        (idx + 1) / total_files,
                        result
                    )
                
            finally:
                # Clean up temporary file
                try:
                    os.unlink(tmp_path)
                except:
                    pass
        
        # Calculate summary statistics
        successful_files = sum(1 for r in results if r['success'])
        failed_files = sum(1 for r in results if not r['success'])
        total_time = (datetime.now() - start_time).total_seconds()
        
        return {
            'success': True,
            'total_files': total_files,
            'successful_files': successful_files,
            'failed_files': failed_files,
            'total_chunks': total_chunks,
            'total_time': total_time,
            'models_covered': sorted(list(models_covered)),
            'results': results
        }
        
    except Exception as e:
        total_time = (datetime.now() - start_time).total_seconds()
        return {
            'success': False,
            'error': str(e),
            'total_time': total_time,
            'results': results
        }


def clear_collection(db_path: str = "./chroma_db", collection_name: str = "toyota_specs") -> Dict[str, Any]:
    """
    Clear all documents from the ChromaDB collection.
    
    Args:
        db_path: Path to ChromaDB persistence directory
        collection_name: Name of the collection to clear
    
    Returns:
        Dictionary with operation result
    """
    try:
        client = chromadb.PersistentClient(path=db_path)
        
        # Delete and recreate collection
        try:
            client.delete_collection(name=collection_name)
        except:
            pass  # Collection might not exist
        
        # Recreate empty collection
        client.create_collection(
            name=collection_name,
            metadata={"description": "Toyota vehicle specifications for RAG"}
        )
        
        return {
            'success': True,
            'message': 'Collection cleared successfully'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }
