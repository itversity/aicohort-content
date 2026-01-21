"""
Car Buyer Assist RAG Application - Landing Page
"""

import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Car Buyer Assist RAG",
    page_icon="🚗",
    layout="centered"
)

# Application title
st.title("Car Buyer Assist RAG Application")

# Brief description
st.markdown("""
A conversational AI system that helps prospective car buyers get instant, accurate answers 
about Toyota vehicles using Retrieval-Augmented Generation (RAG) technology.
""")

# Current status
st.info("""
**Application Status**: Under Development

This application is currently in active development. Additional features and pages will be added as the system evolves.
""")
