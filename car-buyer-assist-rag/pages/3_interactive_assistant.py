"""
Interactive AI Assistant Page

Chat interface for asking questions about Toyota vehicles using RAG.
Follows Design Document specifications (Section 4.4)
"""

import streamlit as st
from pathlib import Path
import sys
import time
from typing import Dict, Any, Tuple

# Add parent directory to path
parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir))

# Import utilities
from utils.connectivity_validators import load_environment_config
from utils.document_processor import get_collection_stats
from utils.rag_chain import query_rag_system

# Page configuration
st.set_page_config(
    page_title="AI Assistant - Car Buyer Assist",
    page_icon="🤖",
    layout="wide"
)


# ============================================================================
# Helper Functions
# ============================================================================

def validate_query(query: str) -> Tuple[bool, str]:
    """Validate user query.
    
    Returns:
        (is_valid, error_message)
    """
    query = query.strip()
    
    if not query:
        return False, "Please enter a question."
    
    if len(query) < 5:
        return False, "Question too short. Please be more specific."
    
    if len(query) > 500:
        return False, "Question too long. Please keep it under 500 characters."
    
    # Check for potentially harmful content (basic)
    if any(char in query for char in ['<', '>', '{', '}']):
        return False, "Invalid characters detected."
    
    return True, ""


def check_rate_limit(cooldown_seconds: int = 2) -> Tuple[bool, str]:
    """Check if user is within rate limits.
    
    Returns:
        (is_allowed, message)
    """
    if 'last_query_time' not in st.session_state:
        st.session_state.last_query_time = 0
    
    current_time = time.time()
    time_since_last = current_time - st.session_state.last_query_time
    
    if time_since_last < cooldown_seconds:
        remaining = cooldown_seconds - time_since_last
        return False, f"Please wait {remaining:.1f} seconds before asking another question."
    
    st.session_state.last_query_time = current_time
    return True, ""


def process_query(query: str, config: Dict[str, Any]) -> None:
    """Process a query through RAG and add to session state.
    
    This function handles validation, rate limiting, processing,
    and updates session state. It does NOT display messages inline
    to avoid double rendering.
    
    Args:
        query: User's question
        config: Configuration dictionary
    """
    # Validate query
    is_valid, validation_msg = validate_query(query)
    if not is_valid:
        st.warning(validation_msg)
        st.stop()
    
    # Check rate limit
    is_allowed, rate_limit_msg = check_rate_limit(cooldown_seconds=2)
    if not is_allowed:
        st.warning(rate_limit_msg)
        st.stop()
    
    # Add user message to session state
    st.session_state.messages.append({
        'role': 'user',
        'content': query,
        'citations': []
    })
    
    # Process query with spinner
    with st.spinner("🤔 Thinking..."):
        # Pass conversation history for context
        conversation_history = st.session_state.messages[:-1]  # Exclude current query
        result = query_rag_system(query, config, conversation_history=conversation_history)
    
    # Handle response
    if result['success']:
        response = result['response']
        sources = result['sources']
        
        # Add assistant message to session state
        st.session_state.messages.append({
            'role': 'assistant',
            'content': response,
            'citations': sources
        })
    else:
        # Format error message based on error type
        error_type = result.get('error_type', 'unknown')
        error = result.get('error', 'Unknown error')
        
        if error_type == 'model_not_found':
            error_msg = "⚠️ Model configuration issue. Please contact administrator."
        elif error_type == 'rate_limit':
            error_msg = "⚠️ API rate limit exceeded. Please wait a moment and try again."
        elif error_type == 'timeout':
            error_msg = "⏱️ Request timed out. Please try again."
        elif error_type == 'connection_error':
            error_msg = "🔌 Connection failed. Please check your internet connection."
        else:
            error_msg = f"❌ Error: {error}"
        
        st.session_state.messages.append({
            'role': 'assistant',
            'content': error_msg,
            'citations': []
        })


# ============================================================================
# Initialize Session State
# ============================================================================

if 'messages' not in st.session_state:
    st.session_state.messages = []

# Load configuration
try:
    config = load_environment_config()
    config_loaded = True
except Exception as e:
    config_loaded = False
    config_error = str(e)


# ============================================================================
# Header
# ============================================================================

st.title("🤖 Interactive AI Assistant")
st.markdown("""
Ask me anything about Toyota vehicles! I'll search through official specification documents 
to provide accurate, citation-backed answers.
""")

st.markdown("---")


# ============================================================================
# Sidebar - Statistics and Controls
# ============================================================================

with st.sidebar:
    st.header("📊 Assistant Stats")
    
    # Get collection statistics with loading indicator
    if config_loaded:
        with st.spinner("Loading knowledge base stats..."):
            stats = get_collection_stats(
                db_path=config.get('chromadb', {}).get('path', './chroma_db')
            )
        
        if stats['exists'] and stats['total_chunks'] > 0:
            st.success("✅ Knowledge Base Ready")
            st.metric("Total Chunks", stats['total_chunks'])
            st.metric("Documents Loaded", stats['total_documents'])
            
            if stats['models_covered']:
                st.write("**Models Available:**")
                for model in sorted(stats['models_covered']):
                    st.write(f"• {model}")
            
            collection_ready = True
        else:
            st.warning("⚠️ No documents in knowledge base")
            st.info("Please upload documents in the Document Processing page first.")
            collection_ready = False
    else:
        st.error("❌ Configuration Error")
        st.write(f"Error: {config_error}")
        collection_ready = False
    
    st.markdown("---")
    
    # Conversation stats
    st.header("💬 Conversation")
    st.metric("Messages", len(st.session_state.messages))
    
    # Clear conversation button
    if st.button("🗑️ Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        if 'last_query_time' in st.session_state:
            del st.session_state.last_query_time
        st.rerun()


# ============================================================================
# Main Content Area
# ============================================================================

col1, col2 = st.columns([3, 1])

with col1:
    # Prerequisites check
    if not config_loaded:
        st.error("⚠️ **Configuration Error**")
        st.write(f"Cannot load environment configuration: {config_error}")
        st.write("Please check your .env file and credentials.")
        st.stop()
    
    if not collection_ready:
        st.warning("⚠️ **Knowledge Base Empty**")
        st.write("No documents have been processed yet. Please:")
        st.write("1. Go to the **Document Processing** page")
        st.write("2. Upload Toyota specification PDFs")
        st.write("3. Return here to start asking questions")
        st.page_link("pages/2_document_processing.py", label="→ Go to Document Processing", icon="📄")
        st.stop()
    
    # Example queries (show only when conversation is empty)
    if len(st.session_state.messages) == 0:
        st.info("👋 **Welcome! Here are some example questions you can ask:**")
        
        example_queries = [
            "What is the fuel efficiency of the Camry hybrid?",
            "Compare RAV4 and Highlander for families",
            "What safety features does the Corolla have?",
            "What is the towing capacity of the Tacoma?"
        ]
        
        cols = st.columns(2)
        for idx, example in enumerate(example_queries):
            with cols[idx % 2]:
                if st.button(f"💡 {example}", key=f"example_{idx}", use_container_width=True):
                    # Set the example as the query to be processed
                    st.session_state.pending_query = example
                    st.rerun()
        
        st.markdown("---")
    
    # Display chat messages from session state (single source of truth)
    for message in st.session_state.messages:
        role = message['role']
        content = message['content']
        citations = message.get('citations', [])
        
        with st.chat_message(role):
            st.write(content)
            
            # Show citations for assistant messages
            if role == 'assistant' and citations:
                if len(citations) == 1:
                    st.caption(f"📄 Source: {citations[0]}")
                else:
                    st.caption(f"📄 Sources: {', '.join(citations)}")
    
    # Handle pending query from example button
    if hasattr(st.session_state, 'pending_query'):
        query = st.session_state.pending_query
        del st.session_state.pending_query
        process_query(query, config)
        st.rerun()
    
    # Chat input
    if prompt := st.chat_input("Ask me anything about Toyota vehicles..."):
        process_query(prompt, config)
        st.rerun()

with col2:
    st.markdown("### 💡 Tips")
    st.markdown("""
    **Ask about:**
    - Specifications
    - Features & safety
    - Comparisons
    - Pricing & trims
    - Recommendations
    
    **For best results:**
    - Be specific
    - Mention model names
    - Ask one thing at a time
    """)
    
    st.markdown("---")
    
    st.markdown("### ℹ️ How it works")
    st.markdown("""
    1. Your question is converted to a vector
    2. Similar content is retrieved from documents
    3. AI generates an answer based on that content
    4. Sources are cited for transparency
    5. **New!** Conversation context is maintained
    """)
