"""
Connectivity Validation Page

This page verifies all external service connections before document processing:
- GCP Vertex AI (embeddings and LLM)
- ChromaDB (vector database)
- LangSmith (observability)
"""

import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path to import utils
parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir))

from utils.connectivity_validators import (
    validate_vertex_ai,
    validate_chromadb,
    validate_langsmith,
    load_environment_config,
    get_config_status
)


# Page configuration
st.set_page_config(
    page_title="Connectivity Validation - Car Buyer Assist",
    page_icon="🔌",
    layout="wide"
)


def display_service_status(service_name: str, icon: str, result: dict = None):
    """
    Display a service connection status card
    
    Args:
        service_name: Name of the service
        icon: Emoji icon for the service
        result: Validation result dictionary (None if not tested)
    """
    with st.container():
        st.markdown(f"### {icon} {service_name}")
        
        if result is None:
            st.info("⏳ Not tested yet")
        elif result['success']:
            st.success(f"✅ {result['message']}")
            if result.get('details'):
                with st.expander("📋 View Details"):
                    st.code(result['details'], language=None)
        else:
            st.error(f"❌ {result['message']}")
            if result.get('details'):
                with st.expander("🔍 View Error Details"):
                    st.code(result['details'], language=None)
                    
                    # Provide troubleshooting tips based on error type
                    error_type = result.get('error_type', 'unknown')
                    if error_type == 'authentication':
                        st.info("💡 **Troubleshooting Tip**: Check your service account credentials and ensure they are properly configured.")
                    elif error_type == 'api_not_enabled':
                        st.info("💡 **Troubleshooting Tip**: Enable the required API in your GCP project console.")
                    elif error_type == 'configuration':
                        st.info("💡 **Troubleshooting Tip**: Verify all required environment variables are set in your .env file.")
        
        st.divider()


def display_configuration(config: dict, status: dict):
    """
    Display current configuration from environment variables
    
    Args:
        config: Configuration dictionary
        status: Status dictionary showing which values are set
    """
    with st.expander("⚙️ Current Configuration", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Google Cloud Platform**")
            project_id = config['google']['project_id']
            region = config['google']['region']
            creds_path = config['google']['credentials_path']
            
            if status['google']['project_id']:
                st.success(f"✓ Project ID: `{project_id}`")
            else:
                st.error("✗ Project ID: Not Set")
            
            if status['google']['region']:
                st.success(f"✓ Region: `{region}`")
            else:
                st.error("✗ Region: Not Set")
            
            if status['google']['credentials']:
                # Check if file actually exists
                if Path(creds_path).exists():
                    st.success(f"✓ Credentials: File found")
                    st.caption(f"`{creds_path}`")
                else:
                    st.warning(f"⚠️ Credentials: Path set but file not found")
                    st.caption(f"`{creds_path}`")
            else:
                st.error("✗ Credentials: Not Set")
            
            st.markdown("**ChromaDB**")
            db_path = config['chromadb']['path']
            st.success(f"✓ Database Path: `{db_path}`")
        
        with col2:
            st.markdown("**LangSmith**")
            api_key = config['langsmith']['api_key']
            project = config['langsmith']['project']
            tracing = config['langsmith']['tracing']
            
            if status['langsmith']['api_key']:
                # Mask API key for security
                masked_key = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "***"
                st.success(f"✓ API Key: `{masked_key}`")
            else:
                st.error("✗ API Key: Not Set")
            
            if status['langsmith']['project']:
                st.success(f"✓ Project: `{project}`")
            else:
                st.warning("⚠️ Project: Not Set (optional)")
            
            if tracing.lower() in ['true', 'v2']:
                st.success(f"✓ Tracing: Enabled ({tracing})")
            else:
                st.info(f"ℹ️ Tracing: {tracing}")


def get_overall_status(results: dict) -> tuple[bool, str]:
    """
    Determine overall connectivity status
    
    Args:
        results: Dictionary of validation results
    
    Returns:
        tuple of (all_passed, status_message)
    """
    # Exclude 'timestamp' key from service results
    service_results = {k: v for k, v in results.items() if k != 'timestamp'}
    
    tested_services = [k for k, v in service_results.items() if v is not None]
    
    if not tested_services:
        return False, "No services tested yet"
    
    passed_services = [k for k, v in service_results.items() if v is not None and v['success']]
    failed_services = [k for k, v in service_results.items() if v is not None and not v['success']]
    
    if len(failed_services) == 0:
        return True, f"✅ All {len(passed_services)} services connected successfully!"
    else:
        return False, f"❌ {len(failed_services)} service(s) failed, {len(passed_services)} passed"


# Initialize session state
if 'validation_results' not in st.session_state:
    st.session_state.validation_results = {
        'vertex_ai': None,
        'chromadb': None,
        'langsmith': None,
        'timestamp': None
    }

if 'test_in_progress' not in st.session_state:
    st.session_state.test_in_progress = False


# Main UI
st.title("🔌 Connectivity Validation")
st.markdown("""
Verify all external service connections before processing documents or making queries.
This page tests connectivity to **GCP Vertex AI**, **ChromaDB**, and **LangSmith**.
""")

st.info("📝 **Note**: Ensure your `.env` file is configured with all required credentials before testing.")

# Load configuration
config = load_environment_config()
status, config = get_config_status()

# Display configuration
display_configuration(config, status)

st.markdown("---")

# Test controls
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    test_button = st.button("🧪 Test All Connections", type="primary", use_container_width=True)

with col2:
    if st.button("🔄 Reset Results", use_container_width=True):
        st.session_state.validation_results = {
            'vertex_ai': None,
            'chromadb': None,
            'langsmith': None,
            'timestamp': None
        }
        st.rerun()

with col3:
    if st.button("📊 View Logs", use_container_width=True):
        st.info("Log viewer coming in Observability page")

st.markdown("---")

# Run tests if button clicked
if test_button:
    st.session_state.test_in_progress = True
    
    # Test GCP Vertex AI
    st.markdown("### Testing Services...")
    
    with st.spinner("Testing GCP Vertex AI..."):
        vertex_result = validate_vertex_ai(
            project_id=config['google']['project_id'],
            region=config['google']['region'],
            credentials_path=config['google']['credentials_path']
        )
        st.session_state.validation_results['vertex_ai'] = vertex_result
    
    # Test ChromaDB
    with st.spinner("Testing ChromaDB..."):
        chromadb_result = validate_chromadb(
            db_path=config['chromadb']['path']
        )
        st.session_state.validation_results['chromadb'] = chromadb_result
    
    # Test LangSmith
    with st.spinner("Testing LangSmith..."):
        langsmith_result = validate_langsmith(
            api_key=config['langsmith']['api_key'],
            project=config['langsmith']['project']
        )
        st.session_state.validation_results['langsmith'] = langsmith_result
    
    # Update timestamp
    from datetime import datetime
    st.session_state.validation_results['timestamp'] = datetime.now()
    st.session_state.test_in_progress = False
    
    st.rerun()

# Display results
st.markdown("## 📊 Connection Status")

# Create three columns for service status
col1, col2, col3 = st.columns(3)

with col1:
    display_service_status(
        "GCP Vertex AI",
        "🔹",
        st.session_state.validation_results['vertex_ai']
    )

with col2:
    display_service_status(
        "ChromaDB",
        "🔹",
        st.session_state.validation_results['chromadb']
    )

with col3:
    display_service_status(
        "LangSmith",
        "🔹",
        st.session_state.validation_results['langsmith']
    )

# Overall status
st.markdown("---")
st.markdown("## 📈 Overall Status")

all_passed, status_message = get_overall_status(st.session_state.validation_results)

if all_passed:
    st.success(status_message)
    st.balloons()
    st.markdown("""
    ### ✅ Ready to Proceed!
    
    All services are connected successfully. You can now:
    
    1. **Process Documents** - Upload and index Toyota specification PDFs
    2. **Use Interactive Assistant** - Ask questions about Toyota vehicles
    3. **View Observability** - Monitor system performance and costs
    """)
elif st.session_state.validation_results['vertex_ai'] is not None:
    st.warning(status_message)
    st.markdown("""
    ### ⚠️ Action Required
    
    Some services failed connectivity tests. Please:
    
    1. Review the error details above
    2. Fix configuration issues in your `.env` file
    3. Rerun the connectivity tests
    
    You can proceed with partial functionality, but some features may not work properly.
    """)
else:
    st.info("Click **Test All Connections** to begin validation")

# Display timestamp if tests have been run
if st.session_state.validation_results['timestamp']:
    st.caption(f"Last tested: {st.session_state.validation_results['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")

# Help section
with st.expander("❓ Need Help?"):
    st.markdown("""
    ### Common Issues and Solutions
    
    #### GCP Vertex AI Issues
    - **Authentication Failed**: Verify `GOOGLE_APPLICATION_CREDENTIALS` points to a valid service account key file
    - **API Not Enabled**: Run `gcloud services enable aiplatform.googleapis.com --project=YOUR_PROJECT_ID`
    - **Permission Denied**: Ensure service account has `roles/aiplatform.user` role
    
    #### ChromaDB Issues
    - **Permission Denied**: Check write permissions on the `./chroma_db` directory
    - **Import Error**: Ensure ChromaDB is installed: `pip install chromadb`
    
    #### LangSmith Issues
    - **Invalid API Key**: Get your API key from [LangSmith Console](https://smith.langchain.com)
    - **Network Error**: Check internet connectivity and firewall settings
    - **Project Not Found**: The project name is optional; validation will still pass
    
    ### Environment Variables Reference
    
    Create a `.env` file in the project root with:
    
    ```bash
    # Google Cloud Platform
    GOOGLE_PROJECT_ID=your-project-id
    GOOGLE_REGION=us-central1
    GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
    
    # ChromaDB
    CHROMADB_PATH=./chroma_db
    
    # LangSmith
    LANGSMITH_API_KEY=your-api-key
    LANGSMITH_PROJECT=car-buyer-assist
    LANGSMITH_TRACING=v2
    ```
    
    ### Setup Scripts
    
    Run these scripts to automate setup:
    - `scripts/setup/setup_gcp_sa.py` - Create GCP service account
    - `scripts/setup/langsmith_validate.py` - Validate LangSmith connection
    """)

# Footer
st.markdown("---")
st.caption("Car Buyer Assist RAG Application | Connectivity Validation v1.0")

