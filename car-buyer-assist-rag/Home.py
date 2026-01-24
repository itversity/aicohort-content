"""
Car Buyer Assist RAG Application - Landing Page
"""

import streamlit as st
from services.chromadb_service import ChromaDBService
from config.constants import RAGConfig

# Page configuration
st.set_page_config(
    page_title="Car Buyer Assist RAG",
    page_icon="🚗",
    layout="wide"
)

# Application title
st.title("🚗 Car Buyer Assist RAG Application")

# Brief description
st.markdown("""
A conversational AI system that helps prospective car buyers get instant, accurate answers 
about Toyota vehicles using Retrieval-Augmented Generation (RAG) technology.
""")

st.divider()

# ============================================================================
# System Status
# ============================================================================

col1, col2, col3 = st.columns(3)

# Check ChromaDB status
try:
    chromadb_service = ChromaDBService()
    collection_stats = chromadb_service.get_collection_stats(RAGConfig.DEFAULT_COLLECTION)
    
    with col1:
        st.metric(
            label="Documents Processed",
            value=collection_stats['document_count'] if collection_stats['exists'] else 0
        )
    
    with col2:
        st.metric(
            label="Collection Status",
            value="Ready" if collection_stats['exists'] and collection_stats['document_count'] > 0 else "Empty"
        )
    
    with col3:
        st.metric(
            label="Models Available",
            value="8 Toyota Models"
        )
except Exception as e:
    with col1:
        st.metric(label="Documents Processed", value="N/A")
    with col2:
        st.metric(label="Collection Status", value="Unknown")
    with col3:
        st.metric(label="Models Available", value="N/A")

st.divider()

# ============================================================================
# Navigation Cards
# ============================================================================

st.markdown("### 🧭 Quick Navigation")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    #### 🔌 1. Connectivity Validation
    Verify connections to all external services:
    - ChromaDB (Vector Database)
    - Google Vertex AI (Embeddings & LLM)
    - LangSmith (Observability)
    
    **Start here** if this is your first time using the application.
    """)

with col2:
    st.markdown("""
    #### 📄 2. Document Processing
    Upload and process Toyota specification PDFs:
    - Extract text from PDFs
    - Generate embeddings
    - Store in vector database
    
    **Process documents** before using the assistant.
    """)

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    #### 💬 3. Interactive Assistant
    Ask questions about Toyota vehicles:
    - Natural language queries
    - Multi-turn conversations
    - Context-aware responses
    - Source citations
    
    **Chat with the AI** to get vehicle information.
    """)

with col2:
    st.markdown("""
    #### 📊 4. Operations Monitor
    View system metrics and recent activity:
    - Document processing operations
    - Query execution traces
    - Performance metrics
    - LangSmith integration
    
    **Monitor** the system's operations and performance.
    """)

st.divider()

# ============================================================================
# Getting Started
# ============================================================================

st.markdown("### 🚀 Getting Started")

st.markdown("""
Follow these steps to use the Car Buyer Assist RAG Application:

1. **Connectivity Validation** - Go to the Connectivity page and test all service connections
2. **Document Processing** - Upload and process Toyota specification PDFs on the Document Processing page
3. **Interactive Assistant** - Start asking questions about Toyota vehicles on the Interactive Assistant page
4. **Operations Monitor** - View system performance and trace data on the Monitor page

**Example Conversation:**
- **You:** "What are the safety features of the Corolla?"
- **Assistant:** *Provides detailed safety features with citations*
- **You:** "What is the base price of it?"
- **Assistant:** *Understands "it" refers to Corolla and provides pricing*
""")

st.divider()

# ============================================================================
# Technology Stack
# ============================================================================

with st.expander("🛠️ Technology Stack"):
    st.markdown("""
    - **Frontend**: Streamlit
    - **Orchestration**: LangChain
    - **Vector Database**: ChromaDB
    - **LLM & Embeddings**: Google Vertex AI (Gemini 2.0 Flash, text-embedding-004)
    - **Observability**: LangSmith
    - **Language**: Python 3.11+
    """)
