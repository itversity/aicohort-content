import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="Car Buyer Assist",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Color Palette (ITVersity Branding)
PRIMARY_RED = "#D81F26"
GRAY = "#757576"
BEIGE = "#F0EDE8"
BLACK = "#000000"

# ===========================
# Section 1: Header
# ===========================
st.markdown(f'<h1 style="color: {PRIMARY_RED};">Car Buyer Assist</h1>', unsafe_allow_html=True)
st.markdown(f'<h3 style="color: {GRAY};">AI-Powered Toyota Vehicle Information Assistant</h3>', unsafe_allow_html=True)

st.write("Get instant answers about Toyota vehicles using natural language questions.")
st.write("Powered by RAG technology with official Toyota specification documents.")

st.divider()

# ===========================
# Section 2: System Status Dashboard
# ===========================
st.subheader("System Overview")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="System Status", value="⚠️ Not Configured")

with col2:
    st.metric(label="📚 Documents Processed", value="0 documents")

with col3:
    st.metric(label="🚗 Toyota Models", value="0 models")

st.divider()

# ===========================
# Section 3: Quick Navigation Cards
# ===========================
st.subheader("Quick Navigation")

# First Row - 2 Cards
row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    with st.container(border=True):
        st.markdown(f"""
        <div style="background-color: {BEIGE}; padding: 20px; border-radius: 5px;">
            <h3>🔌 Connectivity Check</h3>
            <p style="color: {GRAY};">Verify GCP Vertex AI and ChromaDB connections</p>
        </div>
        """, unsafe_allow_html=True)
        st.page_link("pages/1_Connectivity.py", label="Check Connections", use_container_width=True)

with row1_col2:
    with st.container(border=True):
        st.markdown(f"""
        <div style="background-color: {BEIGE}; padding: 20px; border-radius: 5px;">
            <h3>📄 Document Processing</h3>
            <p style="color: {GRAY};">Upload and process Toyota specification PDFs</p>
        </div>
        """, unsafe_allow_html=True)
        st.page_link("pages/2_Document_Processing.py", label="Process Documents", use_container_width=True)

# Second Row - 2 Cards
row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    with st.container(border=True):
        st.markdown(f"""
        <div style="background-color: {BEIGE}; padding: 20px; border-radius: 5px;">
            <h3>💬 Ask Questions</h3>
            <p style="color: {GRAY};">Chat with AI about Toyota vehicles</p>
        </div>
        """, unsafe_allow_html=True)
        st.page_link("pages/3_Interactive_Assistant.py", label="Start Chatting", use_container_width=True)

with row2_col2:
    with st.container(border=True):
        st.markdown(f"""
        <div style="background-color: {BEIGE}; padding: 20px; border-radius: 5px;">
            <h3>📊 System Insights</h3>
            <p style="color: {GRAY};">View performance metrics and usage analytics</p>
        </div>
        """, unsafe_allow_html=True)
        st.page_link("pages/4_Observability.py", label="View Insights", use_container_width=True)

st.divider()

# ===========================
# Section 4: Sample Queries (Collapsible)
# ===========================
with st.expander("Not sure what to ask? Try these examples:"):
    st.markdown("""
    - What is the fuel efficiency of the Camry hybrid?
    - Compare RAV4 and Highlander for families
    - What safety features does the Corolla have?
    - What is the towing capacity of the Tacoma?
    - Which hybrid has the longest electric range?
    """)

