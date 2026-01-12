"""
Interactive AI Assistant Page

Chat interface for asking questions about Toyota vehicles using RAG.
Follows Design Document specifications (Section 4.4)
"""

import streamlit as st
from pathlib import Path
import sys

# Add parent directory to path
parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir))

# Import utilities
from utils.connectivity_validators import load_environment_config
from utils.document_processor import get_collection_stats
from utils.rag_chain import query_rag_system, format_response_with_citations

# Page configuration
st.set_page_config(
    page_title="AI Assistant - Car Buyer Assist",
    page_icon="🤖",
    layout="wide"
)

# Initialize session state for messages
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Load configuration
try:
    config = load_environment_config()
    config_loaded = True
except Exception as e:
    config_loaded = False
    config_error = str(e)

# Header
st.title("🤖 Interactive AI Assistant")
st.markdown("""
Ask me anything about Toyota vehicles! I'll search through official specification documents 
to provide accurate, citation-backed answers.
""")

st.markdown("---")

# Sidebar - Statistics and Controls
with st.sidebar:
    st.header("📊 Assistant Stats")
    
    # Get collection statistics
    if config_loaded:
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
        st.rerun()

# Main content area
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
                    st.session_state.example_query = example
                    st.rerun()
        
        st.markdown("---")
    
    # Display chat messages
    chat_container = st.container()
    
    with chat_container:
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
    
    # Handle example query if set
    if hasattr(st.session_state, 'example_query'):
        query = st.session_state.example_query
        del st.session_state.example_query
        
        # Add user message
        st.session_state.messages.append({
            'role': 'user',
            'content': query,
            'citations': []
        })
        
        # Display user message
        with st.chat_message("user"):
            st.write(query)
        
        # Process query and display response
        with st.chat_message("assistant"):
            with st.spinner("🤔 Thinking..."):
                result = query_rag_system(query, config)
            
            if result['success']:
                response = result['response']
                sources = result['sources']
                
                st.write(response)
                
                if sources:
                    if len(sources) == 1:
                        st.caption(f"📄 Source: {sources[0]}")
                    else:
                        st.caption(f"📄 Sources: {', '.join(sources)}")
                
                # Add to session state
                st.session_state.messages.append({
                    'role': 'assistant',
                    'content': response,
                    'citations': sources
                })
            else:
                error_msg = f"Sorry, I encountered an error: {result.get('error', 'Unknown error')}"
                st.error(error_msg)
                
                st.session_state.messages.append({
                    'role': 'assistant',
                    'content': error_msg,
                    'citations': []
                })
        
        st.rerun()
    
    # Chat input
    if prompt := st.chat_input("Ask me anything about Toyota vehicles..."):
        # Add user message
        st.session_state.messages.append({
            'role': 'user',
            'content': prompt,
            'citations': []
        })
        
        # Display user message
        with st.chat_message("user"):
            st.write(prompt)
        
        # Process query and display response
        with st.chat_message("assistant"):
            with st.spinner("🤔 Thinking..."):
                result = query_rag_system(prompt, config)
            
            if result['success']:
                response = result['response']
                sources = result['sources']
                
                st.write(response)
                
                if sources:
                    if len(sources) == 1:
                        st.caption(f"📄 Source: {sources[0]}")
                    else:
                        st.caption(f"📄 Sources: {', '.join(sources)}")
                
                # Add to session state
                st.session_state.messages.append({
                    'role': 'assistant',
                    'content': response,
                    'citations': sources
                })
            else:
                error_msg = f"Sorry, I encountered an error: {result.get('error', 'Unknown error')}"
                st.error(error_msg)
                
                st.session_state.messages.append({
                    'role': 'assistant',
                    'content': error_msg,
                    'citations': []
                })
        
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
    """)

