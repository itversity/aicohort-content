"""
Car Buyer Assist RAG Application
Home Page / Dashboard

Landing page providing system overview, navigation, and quick stats.
"""

import streamlit as st
from pathlib import Path
import sys

# Add parent directory to path
parent_dir = Path(__file__).parent
sys.path.append(str(parent_dir))

# Import utilities for dynamic stats
from utils.document_processor import get_collection_stats
from utils.connectivity_validators import load_environment_config

# Page configuration
st.set_page_config(
    page_title="Car Buyer Assist - Home",
    page_icon="🚗",
    layout="wide"
)

# Title and description
st.title("🚗 Car Buyer Assist RAG Application")
st.markdown("""
### AI-Powered Toyota Vehicle Information Assistant

Welcome to the Car Buyer Assist application! This system uses Retrieval-Augmented Generation (RAG) 
to provide accurate, context-aware answers about Toyota vehicles based on official specification documents.
""")

st.markdown("---")

# System overview
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("## 🎯 What This System Does")
    st.markdown("""
    - **Natural Language Queries**: Ask questions in plain English about Toyota vehicles
    - **Accurate Answers**: Responses grounded in official Toyota specification documents
    - **Source Citations**: Every answer includes references to source documents
    - **Multi-Vehicle Comparison**: Compare features across different Toyota models
    - **Comprehensive Coverage**: Covers sedans, SUVs, hybrids, trucks, and electric vehicles
    """)
    
    st.markdown("## 📚 Vehicle Coverage")
    st.markdown("""
    Our knowledge base includes specifications for:
    - **Sedans**: Corolla, Camry
    - **SUVs**: RAV4, Highlander
    - **Hybrids**: Prius, Prius Prime
    - **Truck**: Tacoma
    - **Electric**: bZ4X
    """)

with col2:
    st.markdown("## 📊 Quick Stats")
    
    # Get dynamic stats from ChromaDB
    try:
        config = load_environment_config()
        stats = get_collection_stats(db_path=config['chromadb']['path'])
        
        docs_count = stats.get('total_documents', 0)
        chunks_count = stats.get('total_chunks', 0)
        models_count = len(stats.get('models_covered', []))
        
    except:
        # Fallback to zeros if there's an error
        docs_count = 0
        chunks_count = 0
        models_count = 0
    
    stat_col1, stat_col2 = st.columns(2)
    
    with stat_col1:
        st.metric(
            label="Documents",
            value=docs_count,
            help="Total PDFs processed"
        )
        st.metric(
            label="Chunks",
            value=chunks_count,
            help="Text segments in vector database"
        )
    
    with stat_col2:
        st.metric(
            label="Models",
            value=models_count if models_count > 0 else "8",
            help="Toyota vehicle models covered"
        )
        st.metric(
            label="Queries",
            value="0",
            help="Total questions answered"
        )
    
    if docs_count == 0:
        st.info("💡 **Tip**: Process documents first to see updated statistics")
    else:
        st.success(f"✓ Knowledge base ready with {models_count} models!")

st.markdown("---")

# Navigation cards
st.markdown("## 🧭 Get Started")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("### 1️⃣ Connectivity")
    st.markdown("""
    **Validate Services**
    
    Test connections to:
    - GCP Vertex AI
    - ChromaDB
    - LangSmith
    
    """)
    if st.button("🔌 Check Connectivity", use_container_width=True):
        st.switch_page("pages/1_connectivity.py")

with col2:
    st.markdown("### 2️⃣ Documents")
    st.markdown("""
    **Process PDFs**
    
    Upload and index:
    - Toyota specs
    - Extract text
    - Generate embeddings
    
    """)
    if st.button("📄 Process Docs", use_container_width=True):
        st.switch_page("pages/2_document_processing.py")

with col3:
    st.markdown("### 3️⃣ Assistant")
    st.markdown("""
    **Ask Questions**
    
    Interactive chat:
    - Natural language
    - Instant answers
    - Source citations
    
    """)
    if st.button("💬 Chat Now", use_container_width=True):
        st.switch_page("pages/3_interactive_assistant.py")

with col4:
    st.markdown("### 4️⃣ Metrics")
    st.markdown("""
    **View Analytics**
    
    Monitor:
    - Performance
    - Token usage
    - Costs
    
    """)
    if st.button("📈 See Metrics", use_container_width=True, disabled=True):
        st.info("Coming soon: Observability")

st.markdown("---")

# Example queries
st.markdown("## 💡 Example Queries")

st.markdown("""
Once you've processed the documents, you can ask questions like:
""")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **Specifications**
    - "What is the fuel efficiency of the Camry hybrid?"
    - "How much horsepower does the RAV4 Prime have?"
    - "What is the towing capacity of the Tacoma?"
    - "What is the electric range of the bZ4X?"
    """)
    
    st.markdown("""
    **Features & Safety**
    - "What safety features does the Corolla have?"
    - "Does the Highlander have third-row seating?"
    - "What technology features are in the RAV4?"
    - "Is AWD available on the Camry?"
    """)

with col2:
    st.markdown("""
    **Comparisons**
    - "Compare fuel efficiency between Prius and Prius Prime"
    - "What are the differences between RAV4 and Highlander?"
    - "Which sedan is better for first-time buyers?"
    - "How does the Camry compare to the Honda Accord?"
    """)
    
    st.markdown("""
    **Recommendations**
    - "What Toyota vehicle is best for a family of five?"
    - "I need a fuel-efficient car for city driving, what do you recommend?"
    - "Which hybrid has the longest electric range?"
    """)

st.markdown("---")

# System architecture
with st.expander("🏗️ System Architecture"):
    st.markdown("""
    ### Technology Stack
    
    **Frontend**
    - Streamlit: Web application framework
    
    **Orchestration**
    - LangChain: RAG pipeline coordination
    - PyPDF: Document text extraction
    
    **Storage & Retrieval**
    - ChromaDB: Vector database for embeddings
    - Semantic search: Cosine similarity
    
    **AI Services**
    - GCP Vertex AI: Embeddings (text-embedding-004)
    - GCP Vertex AI: Text generation (gemini-1.5-pro)
    
    **Observability**
    - LangSmith: Tracing, monitoring, cost tracking
    
    ### Data Flow
    
    1. **Document Processing**: PDFs → Text extraction → Chunking → Embeddings → Vector storage
    2. **Query Processing**: User question → Embedding → Similarity search → Context retrieval
    3. **Response Generation**: Query + Context → LLM → Natural language answer with citations
    """)

# Setup instructions
with st.expander("⚙️ Setup Instructions"):
    st.markdown("""
    ### Prerequisites
    
    1. **Python 3.10+** installed
    2. **GCP Account** with Vertex AI enabled
    3. **LangSmith Account** (optional, for observability)
    
    ### Installation Steps
    
    1. **Clone the repository and navigate to project directory**
    
    2. **Create and activate virtual environment**
       ```bash
       python -m venv cbag-venv
       source cbag-venv/bin/activate  # On Windows: cbag-venv\\Scripts\\activate
       ```
    
    3. **Install dependencies**
       ```bash
       pip install -r requirements.txt
       ```
    
    4. **Configure environment variables**
       
       Create a `.env` file in the project root:
       ```bash
       GOOGLE_PROJECT_ID=your-gcp-project-id
       GOOGLE_REGION=us-central1
       GOOGLE_APPLICATION_CREDENTIALS=./credentials/gcp-service-account-key.json
       
       CHROMADB_PATH=./chroma_db
       
       LANGSMITH_API_KEY=your-langsmith-api-key
       LANGSMITH_PROJECT=car-buyer-assist
       LANGSMITH_TRACING=v2
       ```
    
    5. **Set up GCP Service Account**
       ```bash
       python scripts/setup/setup_gcp_sa.py
       ```
    
    6. **Validate LangSmith connection**
       ```bash
       python scripts/setup/langsmith_validate.py
       ```
    
    7. **Run the application**
       ```bash
       streamlit run Home.py
       ```
    
    8. **Navigate to Connectivity page** to verify all services are working
    """)

# Footer
st.markdown("---")
st.caption("Car Buyer Assist RAG Application | POC v1.0 | Built with Streamlit, LangChain, and GCP Vertex AI")

