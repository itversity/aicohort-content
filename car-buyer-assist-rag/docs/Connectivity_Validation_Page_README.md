# Connectivity Validation Page

## Overview

The Connectivity Validation page is the first step in the Car Buyer Assist RAG Application workflow. It verifies that all external services are properly configured and accessible before proceeding with document processing or queries.

## Purpose

This page performs comprehensive connectivity tests for:

1. **GCP Vertex AI** - Validates embedding generation and LLM access
2. **ChromaDB** - Tests vector database read/write operations
3. **LangSmith** - Verifies observability platform connection

## Features

### Configuration Display
- Shows current environment variable settings
- Indicates which values are set/missing
- Masks sensitive information (API keys)
- Provides file path validation

### Service Testing
- **Real-time validation** - Tests services on demand
- **Detailed feedback** - Success messages with timing and configuration details
- **Error diagnostics** - Specific error messages with troubleshooting tips
- **Visual indicators** - Green checkmarks for success, red X for failures

### Test Results
- Individual service status cards
- Expandable details for success/error information
- Overall status summary
- Last tested timestamp
- Session state persistence

## Usage

### Running Tests

1. Ensure your `.env` file is configured with all required credentials
2. Navigate to the Connectivity Validation page
3. Click "🧪 Test All Connections"
4. Review the results for each service
5. Fix any configuration issues if needed
6. Retest to verify fixes

### Environment Variables Required

```bash
# Google Cloud Platform
GOOGLE_PROJECT_ID=your-gcp-project-id
GOOGLE_REGION=us-central1
GOOGLE_APPLICATION_CREDENTIALS=./credentials/gcp-service-account-key.json

# ChromaDB
CHROMADB_PATH=./chroma_db

# LangSmith
LANGSMITH_API_KEY=your-langsmith-api-key
LANGSMITH_PROJECT=car-buyer-assist
LANGSMITH_TRACING=v2
```

## Validation Logic

### GCP Vertex AI Validation

**Test**: Generate a sample embedding using `text-embedding-004`

**Success Criteria**:
- Returns a 768-dimensional vector
- Completes within reasonable time
- No authentication or permission errors

**Common Failures**:
- Authentication failed → Check credentials file path
- API not enabled → Enable Vertex AI API in GCP console
- Permission denied → Verify service account has required roles
- Quota exceeded → Check billing and API quotas

### ChromaDB Validation

**Test**: Create test collection, write/read/query operations

**Success Criteria**:
- Database directory is accessible
- Can create collections
- Can write and retrieve documents
- Query operation works

**Common Failures**:
- Permission denied → Check directory write permissions
- Import error → Install ChromaDB: `pip install chromadb`
- Database locked → Close other processes accessing the database

### LangSmith Validation

**Test**: Authenticate and list available projects

**Success Criteria**:
- API key is valid
- Can list projects
- Configured project exists (if specified)

**Common Failures**:
- Invalid API key → Get new key from LangSmith console
- Network error → Check internet connection and firewall
- Project not found → Optional, validation still passes

## Implementation Details

### Files

- `pages/1_connectivity.py` - Streamlit UI page
- `utils/connectivity_validators.py` - Validation logic
- `utils/__init__.py` - Package initialization

### Architecture

```
User clicks "Test All Connections"
    ↓
Load environment configuration
    ↓
Test Vertex AI
    ↓
Test ChromaDB
    ↓
Test LangSmith
    ↓
Display results with status indicators
    ↓
Store results in session state
```

### Session State

The page uses Streamlit session state to persist validation results:

```python
st.session_state.validation_results = {
    'vertex_ai': {success, message, details, error_type},
    'chromadb': {success, message, details, error_type},
    'langsmith': {success, message, details, error_type},
    'timestamp': datetime
}
```

## Troubleshooting

### "Project ID not configured"
**Solution**: Set `GOOGLE_PROJECT_ID` in your `.env` file

### "Credentials file not found"
**Solution**: 
1. Run `python scripts/setup/setup_gcp_sa.py` to create service account
2. Verify `GOOGLE_APPLICATION_CREDENTIALS` path is correct
3. Ensure the JSON key file exists at the specified location

### "API not enabled"
**Solution**: Enable required APIs:
```bash
gcloud services enable aiplatform.googleapis.com --project=YOUR_PROJECT_ID
```

### "Permission denied" for ChromaDB
**Solution**: Create directory with proper permissions:
```bash
mkdir -p ./chroma_db
chmod 755 ./chroma_db
```

### "Invalid API key" for LangSmith
**Solution**:
1. Visit https://smith.langchain.com
2. Generate new API key
3. Update `LANGSMITH_API_KEY` in `.env` file

## Next Steps

After all services pass validation:

1. **Navigate to Document Processing** - Upload and index Toyota PDFs
2. **Proceed to Interactive Assistant** - Start asking questions
3. **Monitor with Observability** - Track performance and costs

## Design Document Reference

This implementation follows the specifications in:
- **Design Document Section 4.2**: Connectivity Validation Page UI Specification
- **Design Document Section 5.3**: Environment Configuration requirements

## Testing Checklist

- [ ] All environment variables missing → Shows clear errors
- [ ] Invalid GCP credentials → Displays authentication error
- [ ] Invalid LangSmith API key → Shows API error
- [ ] ChromaDB directory doesn't exist → Creates automatically
- [ ] All services valid → All green checkmarks
- [ ] Retry after fixing issues → Updates correctly
- [ ] Page refresh → Retains last test results

## Version

**v1.0** - Initial implementation with full validation suite

