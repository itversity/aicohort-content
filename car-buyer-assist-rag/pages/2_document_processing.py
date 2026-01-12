"""
Document Processing Page

This page handles the upload and processing of Toyota specification PDFs:
- Multi-file PDF upload
- Text extraction and chunking
- Embedding generation via Vertex AI
- Vector storage in ChromaDB
- Real-time progress tracking

Follows Design Document UI Specification (Section 4.3)
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Add parent directory to path to import utils
parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir))

from utils.document_processor import (
    batch_process_pdfs,
    get_collection_stats,
    clear_collection
)
from utils.connectivity_validators import load_environment_config

# Page configuration
st.set_page_config(
    page_title="Document Processing - Car Buyer Assist",
    page_icon="📄",
    layout="wide"
)


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def display_uploaded_files(uploaded_files: List[Any]) -> None:
    """Display uploaded files in a clean card layout."""
    st.markdown("### 📁 Uploaded Files")
    
    for idx, file in enumerate(uploaded_files):
        col1, col2, col3 = st.columns([3, 2, 1])
        
        with col1:
            st.markdown(f"**{idx + 1}. {file.name}**")
        
        with col2:
            st.text(f"Size: {format_file_size(file.size)}")
        
        with col3:
            st.text(f"Type: PDF")
    
    st.divider()


def display_processing_log(logs: List[Dict[str, Any]]) -> None:
    """Display real-time processing logs."""
    if not logs:
        return
    
    with st.container():
        st.markdown("### 📋 Processing Log")
        
        log_container = st.container()
        with log_container:
            for log in logs[-10:]:  # Show last 10 logs
                timestamp = log.get('timestamp', '')
                message = log.get('message', '')
                log_type = log.get('type', 'info')
                
                if log_type == 'success':
                    st.success(f"✓ {message}")
                elif log_type == 'error':
                    st.error(f"✗ {message}")
                elif log_type == 'warning':
                    st.warning(f"⚠ {message}")
                else:
                    st.info(f"ℹ {message}")


def display_processing_results(results: Dict[str, Any]) -> None:
    """Display detailed processing results after completion."""
    st.markdown("---")
    st.markdown("## 📊 Processing Summary")
    
    # Success indicator
    if results['successful_files'] == results['total_files']:
        st.success(f"✅ Successfully processed all {results['total_files']} document(s)!")
        st.balloons()
    elif results['successful_files'] > 0:
        st.warning(f"⚠️ Processed {results['successful_files']} of {results['total_files']} documents")
    else:
        st.error("❌ Failed to process any documents")
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Documents Processed",
            value=results['successful_files'],
            delta=f"{results['total_files']} total"
        )
    
    with col2:
        st.metric(
            label="Chunks Created",
            value=results['total_chunks']
        )
    
    with col3:
        st.metric(
            label="Processing Time",
            value=f"{results['total_time']:.1f}s"
        )
    
    with col4:
        st.metric(
            label="Models Covered",
            value=len(results['models_covered'])
        )
    
    # Models covered
    if results['models_covered']:
        st.markdown("### 🚗 Vehicle Models Covered")
        cols = st.columns(min(4, len(results['models_covered'])))
        for idx, model in enumerate(results['models_covered']):
            with cols[idx % 4]:
                st.info(f"**{model}**")
    
    # Detailed results per file
    st.markdown("### 📄 Per-Document Results")
    
    for result in results['results']:
        with st.expander(f"{'✅' if result['success'] else '❌'} {result['filename']}", expanded=not result['success']):
            if result['success']:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Model", result['model_name'])
                with col2:
                    st.metric("Chunks", result['chunks_created'])
                with col3:
                    st.metric("Time", f"{result['processing_time']:.2f}s")
            else:
                st.error(f"**Error:** {result.get('error', 'Unknown error')}")
                
                # Troubleshooting suggestions
                error_msg = result.get('error', '').lower()
                if 'permission' in error_msg:
                    st.info("💡 **Tip**: Check file permissions and ensure the file is not open in another application.")
                elif 'vertex' in error_msg or 'embedding' in error_msg:
                    st.info("💡 **Tip**: Verify GCP Vertex AI connectivity on the Connectivity page.")
                elif 'chroma' in error_msg:
                    st.info("💡 **Tip**: Check ChromaDB permissions and disk space.")
    
    # ChromaDB collection statistics
    st.markdown("---")
    st.markdown("### 💾 ChromaDB Collection Status")
    
    config = load_environment_config()
    stats = get_collection_stats(db_path=config['chromadb']['path'])
    
    if stats['exists']:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Chunks", stats['total_chunks'])
        with col2:
            st.metric("Total Documents", stats['total_documents'])
        with col3:
            st.metric("Models in DB", len(stats['models_covered']))
        
        with st.expander("📋 View Stored Documents"):
            for source in stats['sources']:
                st.text(f"• {source}")
    
    # Next steps
    if results['successful_files'] > 0:
        st.markdown("---")
        st.markdown("### ✅ Ready for Next Steps!")
        st.markdown("""
        Your documents have been successfully processed and stored. You can now:
        
        1. **Use the Interactive Assistant** to ask questions about Toyota vehicles
        2. **View Observability** metrics to monitor system performance
        3. **Process more documents** if you have additional PDFs
        """)
        
        if st.button("💬 Go to Interactive Assistant", type="primary", use_container_width=True):
            st.info("Interactive Assistant page coming soon!")


def display_existing_collection() -> None:
    """Display statistics about the existing ChromaDB collection."""
    config = load_environment_config()
    stats = get_collection_stats(db_path=config['chromadb']['path'])
    
    if not stats['exists']:
        st.info("No existing collection found. Upload and process documents to create the knowledge base.")
        return
    
    if stats['total_chunks'] == 0:
        st.info("Collection exists but is empty. Upload and process documents to populate it.")
        return
    
    st.markdown("### 💾 Current Collection Statistics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Chunks", stats['total_chunks'])
    
    with col2:
        st.metric("Documents", stats['total_documents'])
    
    with col3:
        st.metric("Models", len(stats['models_covered']))
    
    # Models covered
    if stats['models_covered']:
        st.markdown("**Vehicle Models:**")
        cols = st.columns(min(4, len(stats['models_covered'])))
        for idx, model in enumerate(stats['models_covered']):
            with cols[idx % 4]:
                st.info(f"**{model}**")
    
    # Source documents
    with st.expander("📄 Stored Documents"):
        for source in stats['sources']:
            st.text(f"• {source}")
    
    # Clear collection option
    st.markdown("---")
    st.warning("⚠️ **Danger Zone**: Clearing the collection will delete all processed documents and embeddings.")
    
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("🗑️ Clear Collection", type="secondary"):
            st.session_state.confirm_clear = True
    
    if st.session_state.get('confirm_clear', False):
        with col2:
            st.error("Are you sure? This action cannot be undone!")
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("Yes, Clear Collection", type="primary"):
                    result = clear_collection(db_path=config['chromadb']['path'])
                    if result['success']:
                        st.success("Collection cleared successfully!")
                        st.session_state.confirm_clear = False
                        st.rerun()
                    else:
                        st.error(f"Failed to clear collection: {result['error']}")
            with col_b:
                if st.button("Cancel"):
                    st.session_state.confirm_clear = False
                    st.rerun()


# Initialize session state
if 'processing_status' not in st.session_state:
    st.session_state.processing_status = 'idle'  # idle, processing, complete, error

if 'processing_results' not in st.session_state:
    st.session_state.processing_results = None

if 'processing_logs' not in st.session_state:
    st.session_state.processing_logs = []

if 'uploaded_files_cache' not in st.session_state:
    st.session_state.uploaded_files_cache = []


# Main UI
st.title("📄 Document Processing")
st.markdown("""
Upload Toyota specification PDFs to create the knowledge base for the RAG system.
The system will extract text, chunk content, generate embeddings, and store them in ChromaDB.
""")

st.info("💡 **Tip**: Ensure you've validated connectivity on the Connectivity page before processing documents.")

st.markdown("---")

# Create tabs for different sections
tab1, tab2 = st.tabs(["📤 Upload & Process", "💾 Existing Collection"])

with tab1:
    st.markdown("## 📤 Upload Documents")
    
    # File uploader
    uploaded_files = st.file_uploader(
        "Select PDF files to upload",
        type=['pdf'],
        accept_multiple_files=True,
        help="Upload one or more Toyota specification PDF files"
    )
    
    # Display uploaded files
    if uploaded_files:
        display_uploaded_files(uploaded_files)
        st.session_state.uploaded_files_cache = uploaded_files
        
        # Processing controls
        col1, col2 = st.columns([2, 1])
        
        with col1:
            process_button = st.button(
                "🚀 Process Documents",
                type="primary",
                use_container_width=True,
                disabled=(st.session_state.processing_status == 'processing')
            )
        
        with col2:
            if st.button("🔄 Clear Files", use_container_width=True):
                st.session_state.uploaded_files_cache = []
                st.session_state.processing_status = 'idle'
                st.session_state.processing_results = None
                st.session_state.processing_logs = []
                st.rerun()
        
        # Process documents when button clicked
        if process_button:
            st.session_state.processing_status = 'processing'
            st.session_state.processing_logs = []
            
            st.markdown("---")
            st.markdown("## ⚙️ Processing Documents...")
            
            # Progress tracking
            progress_bar = st.progress(0.0)
            status_text = st.empty()
            log_container = st.container()
            
            # Load configuration
            config = load_environment_config()
            
            # Define progress callback
            def progress_callback(message: str, progress: float, result: Dict = None):
                # Update progress bar
                progress_bar.progress(min(progress, 1.0))
                status_text.text(message)
                
                # Add to logs
                log_entry = {
                    'timestamp': datetime.now().strftime('%H:%M:%S'),
                    'message': message,
                    'type': 'info'
                }
                
                if result:
                    if result['success']:
                        log_entry['type'] = 'success'
                        log_entry['message'] = f"✓ {result['filename']}: {result['chunks_created']} chunks in {result['processing_time']:.1f}s"
                    else:
                        log_entry['type'] = 'error'
                        log_entry['message'] = f"✗ {result['filename']}: {result.get('error', 'Unknown error')}"
                
                st.session_state.processing_logs.append(log_entry)
                
                # Display logs in real-time
                with log_container:
                    for log in st.session_state.processing_logs[-5:]:
                        if log['type'] == 'success':
                            st.success(log['message'])
                        elif log['type'] == 'error':
                            st.error(log['message'])
                        else:
                            st.info(log['message'])
            
            # Process documents
            try:
                results = batch_process_pdfs(
                    uploaded_files=uploaded_files,
                    config=config,
                    progress_callback=progress_callback
                )
                
                st.session_state.processing_results = results
                
                if results['success']:
                    st.session_state.processing_status = 'complete'
                else:
                    st.session_state.processing_status = 'error'
                
                # Clear progress indicators
                progress_bar.progress(1.0)
                status_text.text("Processing complete!")
                
                st.rerun()
                
            except Exception as e:
                st.session_state.processing_status = 'error'
                st.error(f"Critical error during processing: {str(e)}")
                
                # Troubleshooting suggestions
                st.markdown("### 🔍 Troubleshooting")
                st.markdown("""
                Please check the following:
                
                1. **Connectivity**: Verify all services are connected on the Connectivity page
                2. **Credentials**: Ensure GCP credentials are properly configured
                3. **Permissions**: Check ChromaDB directory has write permissions
                4. **Resources**: Verify sufficient disk space and memory
                """)
    
    else:
        st.info("👆 Upload PDF files to begin processing")
        
        # Show example of expected filenames
        with st.expander("📝 File Naming Convention"):
            st.markdown("""
            For best results, name your PDF files following this pattern:
            
            - `Toyota_ModelName_Specifications.pdf`
            - Examples:
              - `Toyota_Camry_Specifications.pdf`
              - `Toyota_RAV4_Specifications.pdf`
              - `Toyota_Prius_Specifications.pdf`
            
            The system will automatically extract the model name from the filename for proper metadata tagging.
            """)
    
    # Display results if processing is complete
    if st.session_state.processing_status in ['complete', 'error'] and st.session_state.processing_results:
        display_processing_results(st.session_state.processing_results)

with tab2:
    st.markdown("## 💾 Existing Collection")
    st.markdown("View and manage the current ChromaDB collection containing processed documents.")
    
    display_existing_collection()
    
    if st.button("🔄 Refresh Statistics"):
        st.rerun()

# Help section
st.markdown("---")
with st.expander("❓ Help & Documentation"):
    st.markdown("""
    ### Document Processing Pipeline
    
    The system processes documents through the following stages:
    
    1. **PDF Text Extraction** - Extract text content from PDF files using PyPDFLoader
    2. **Text Chunking** - Split text into 1000-character chunks with 200-character overlap
    3. **Embedding Generation** - Generate vector embeddings using GCP Vertex AI (text-embedding-004)
    4. **Vector Storage** - Store embeddings in ChromaDB with metadata for retrieval
    
    ### Expected Processing Times
    
    - Single PDF: ~10-30 seconds
    - Multiple PDFs: ~1-2 minutes per document
    - 8 Toyota PDFs: ~5-10 minutes total
    
    ### Metadata Schema
    
    Each chunk is stored with the following metadata:
    - **source**: Original PDF filename
    - **page**: Page number in source document
    - **chunk_index**: Sequential chunk number
    - **model_name**: Extracted vehicle model name
    
    ### Troubleshooting
    
    **Slow processing:**
    - Normal for first-time embedding generation
    - Vertex AI API rate limits may apply
    
    **Failed to extract text:**
    - Ensure PDF is not encrypted or password-protected
    - Verify PDF contains text (not just images)
    
    **ChromaDB errors:**
    - Check write permissions on chroma_db directory
    - Verify sufficient disk space
    
    **Embedding errors:**
    - Validate GCP Vertex AI connectivity
    - Check GCP project quotas and billing
    """)

# Footer
st.markdown("---")
st.caption("Car Buyer Assist RAG Application | Document Processing v1.0")
