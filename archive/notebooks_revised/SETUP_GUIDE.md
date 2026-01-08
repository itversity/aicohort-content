# Setup Guide - RAG Bootcamp Environment

This guide will help you set up everything you need for the 10-week RAG bootcamp. Follow each section carefully.

## Table of Contents

1. [Python Environment Setup](#python-environment-setup)
2. [Install Dependencies](#install-dependencies)
3. [Google Cloud Platform Setup](#google-cloud-platform-setup)
4. [LangSmith Setup](#langsmith-setup)
5. [Environment Variables](#environment-variables)
6. [Verify Installation](#verify-installation)
7. [Troubleshooting](#troubleshooting)

---

## Python Environment Setup

### Prerequisites

Ensure you have Python 3.10 or higher installed:

```bash
python --version
# Should show Python 3.10.x or higher
```

If not installed, download from [python.org](https://www.python.org/downloads/).

### Create Virtual Environment

Navigate to the project directory and use the existing `.venv`:

```bash
cd /path/to/notebooks_revised
```

If `.venv` doesn't exist, create it:

```bash
python -m venv .venv
```

### Activate Virtual Environment

**On macOS/Linux:**
```bash
source .venv/bin/activate
```

**On Windows:**
```bash
.venv\Scripts\activate
```

You should see `(.venv)` in your terminal prompt.

**Important:** Always activate the virtual environment before working on assignments!

---

## Install Dependencies

With the virtual environment activated, install all required packages:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This installs:
- LangChain ecosystem (LangChain, LangGraph, LangSmith)
- Google Cloud AI Platform libraries
- Vector databases (ChromaDB, Pinecone)
- PDF processing (pypdf)
- Jupyter notebook support
- Utility libraries

**Installation time:** 3-5 minutes depending on your internet speed.

### Verify Installation

```bash
python -c "import langchain; print(f'LangChain: {langchain.__version__}')"
python -c "import chromadb; print('ChromaDB: OK')"
python -c "import pypdf; print('PyPDF: OK')"
```

All imports should succeed without errors.

---

## Google Cloud Platform Setup

### Step 1: Create GCP Account

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Sign in with your Google account
3. If first time, you'll get **$300 free credit** (valid for 90 days)

### Step 2: Create a Project

1. Click "Select a project" in the top navigation
2. Click "New Project"
3. Project name: `rag-bootcamp` (or your choice)
4. Click "Create"
5. **Note your Project ID** (you'll need this later)

### Step 3: Enable Required APIs

Enable these APIs for your project:

```bash
# Set your project
gcloud config set project YOUR_PROJECT_ID

# Enable APIs
gcloud services enable aiplatform.googleapis.com
gcloud services enable compute.googleapis.com
gcloud services enable storage.googleapis.com
```

Or enable via Console:
1. Go to "APIs & Services" > "Library"
2. Search and enable:
   - **Vertex AI API**
   - **Compute Engine API**
   - **Cloud Storage API**

### Step 4: Set Up Authentication

#### Option A: Using gcloud CLI (Recommended)

1. Install gcloud CLI: [Installation Guide](https://cloud.google.com/sdk/docs/install)

2. Initialize and authenticate:
```bash
gcloud init
gcloud auth application-default login
```

3. This creates credentials at:
   - macOS/Linux: `~/.config/gcloud/application_default_credentials.json`
   - Windows: `%APPDATA%\gcloud\application_default_credentials.json`

#### Option B: Using Service Account

1. Go to "IAM & Admin" > "Service Accounts"
2. Click "Create Service Account"
3. Name: `rag-bootcamp-sa`
4. Grant roles:
   - **Vertex AI User**
   - **Storage Object Viewer**
5. Click "Create Key" > JSON
6. Save the JSON file securely
7. Set environment variable (see next section)

### Step 5: Set GCP Project ID

You'll need your project ID in your `.env` file (covered in next section).

To find your project ID:
```bash
gcloud config get-value project
```

---

## LangSmith Setup

LangSmith provides tracing, monitoring, and evaluation for LLM applications.

### Step 1: Create Account

1. Go to [LangSmith](https://smith.langchain.com/)
2. Sign up with your email or GitHub
3. Free tier includes:
   - 5,000 traces per month
   - 14 days of trace retention
   - Basic evaluation features

### Step 2: Get API Key

1. Click on your profile (bottom left)
2. Go to "Settings" > "API Keys"
3. Click "Create API Key"
4. Name it: `RAG Bootcamp`
5. **Copy the key immediately** (shown only once)

### Step 3: Create Project

1. Click "New Project"
2. Name: `toyota-rag-assistant`
3. Description: "10-week RAG bootcamp project"

---

## Environment Variables

Create a `.env` file in the `notebooks_revised/` directory with your credentials.

### Step 1: Copy Template

```bash
cp .env.example .env
```

### Step 2: Edit `.env` File

Open `.env` in a text editor and fill in your values:

```bash
# Google Cloud Platform
GCP_PROJECT_ID=your-project-id-here
GCP_REGION=us-central1

# If using service account (Option B):
# GOOGLE_APPLICATION_CREDENTIALS=/path/to/your-service-account-key.json

# LangSmith
LANGSMITH_API_KEY=your-langsmith-api-key-here
LANGSMITH_PROJECT=toyota-rag-assistant
LANGSMITH_TRACING_V2=true

# Optional: If using Pinecone in later weeks
# PINECONE_API_KEY=your-pinecone-key-here
# PINECONE_ENVIRONMENT=your-environment

# Optional: If using OpenAI for comparison
# OPENAI_API_KEY=your-openai-key-here
```

### Step 3: Load Environment Variables

The notebooks will automatically load variables from `.env` using python-dotenv.

To test manually:
```bash
source .env  # macOS/Linux
# Or in Python:
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('GCP_PROJECT_ID'))"
```

### Security Note

**Never commit `.env` to git!** It's already in `.gitignore`.

---

## Verify Installation

Run this verification script to check everything is set up correctly.

Create `verify_setup.py`:

```python
"""Verify RAG Bootcamp environment setup"""
import sys
from pathlib import Path

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    if version >= (3, 10):
        print(f"✓ Python version: {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"✗ Python version too old: {version.major}.{version.minor}")
        print("  Required: Python 3.10+")
        return False

def check_imports():
    """Check required packages can be imported"""
    packages = [
        "langchain",
        "langchain_community",
        "langchain_google_vertexai",
        "chromadb",
        "pypdf",
        "google.cloud.aiplatform",
        "dotenv",
    ]
    
    all_ok = True
    for package in packages:
        try:
            __import__(package)
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package} - not installed")
            all_ok = False
    
    return all_ok

def check_env_vars():
    """Check environment variables"""
    from dotenv import load_dotenv
    import os
    
    load_dotenv()
    
    required_vars = [
        "GCP_PROJECT_ID",
        "LANGSMITH_API_KEY",
    ]
    
    all_ok = True
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Mask sensitive values
            masked = value[:8] + "..." if len(value) > 8 else "***"
            print(f"✓ {var}: {masked}")
        else:
            print(f"✗ {var} - not set")
            all_ok = False
    
    return all_ok

def check_data_files():
    """Check Toyota spec PDFs exist"""
    data_dir = Path("data/car-specs/toyota-specs")
    
    if not data_dir.exists():
        print(f"✗ Data directory not found: {data_dir}")
        return False
    
    pdfs = list(data_dir.glob("*.pdf"))
    if len(pdfs) >= 8:
        print(f"✓ Found {len(pdfs)} Toyota specification PDFs")
        return True
    else:
        print(f"✗ Expected 8 PDFs, found {len(pdfs)}")
        return False

def check_gcp_auth():
    """Check GCP authentication"""
    try:
        import google.auth
        from dotenv import load_dotenv
        import os
        
        load_dotenv()
        credentials, project = google.auth.default()
        
        project_id = os.getenv("GCP_PROJECT_ID")
        print(f"✓ GCP authentication configured")
        print(f"  Project: {project or project_id}")
        return True
    except Exception as e:
        print(f"✗ GCP authentication failed: {e}")
        print("  Run: gcloud auth application-default login")
        return False

def main():
    """Run all checks"""
    print("=" * 60)
    print("RAG Bootcamp Environment Verification")
    print("=" * 60)
    
    checks = [
        ("Python Version", check_python_version),
        ("Package Imports", check_imports),
        ("Environment Variables", check_env_vars),
        ("Data Files", check_data_files),
        ("GCP Authentication", check_gcp_auth),
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n{name}:")
        print("-" * 60)
        results.append(check_func())
    
    print("\n" + "=" * 60)
    if all(results):
        print("✓ All checks passed! You're ready to start the bootcamp.")
    else:
        print("✗ Some checks failed. Please fix the issues above.")
        print("  Refer to SETUP_GUIDE.md for detailed instructions.")
    print("=" * 60)

if __name__ == "__main__":
    main()
```

Run the verification:

```bash
python verify_setup.py
```

---

## Troubleshooting

### Common Issues

#### 1. `ModuleNotFoundError: No module named 'X'`

**Solution:** Make sure virtual environment is activated and dependencies installed:
```bash
source .venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

#### 2. GCP Authentication Errors

**Error:** `Could not automatically determine credentials`

**Solutions:**

**Option A - Using gcloud:**
```bash
gcloud auth application-default login
```

**Option B - Using service account:**
```bash
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
```

Add to `.env`:
```
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
```

#### 3. LangSmith Not Tracing

**Check:** API key is set correctly:
```python
import os
from dotenv import load_dotenv
load_dotenv()
print(os.getenv("LANGSMITH_API_KEY"))  # Should not be None
```

**Solution:** Ensure `.env` has:
```
LANGSMITH_API_KEY=lsv2_pt_...
LANGSMITH_TRACING_V2=true
```

#### 4. Vertex AI Quota Errors

**Error:** `429 Resource has been exhausted`

**Solution:** Free tier has limits. Either:
- Wait and retry (quotas reset)
- Enable billing for higher limits
- Use smaller batch sizes

#### 5. ChromaDB Persistence Errors

**Error:** `Error creating collection`

**Solution:** Delete existing collection:
```python
import chromadb
client = chromadb.Client()
try:
    client.delete_collection("collection_name")
except:
    pass
```

#### 6. Jupyter Kernel Not Found

**Solution:** Install ipykernel in your virtual environment:
```bash
source .venv/bin/activate
pip install ipykernel
python -m ipykernel install --user --name=rag-bootcamp
```

Then select "rag-bootcamp" kernel in Jupyter.

### Still Having Issues?

1. Check `shared_resources/troubleshooting_guide.md`
2. Search discussion forum
3. Attend office hours
4. Email instructor with:
   - Error message (full traceback)
   - What you were trying to do
   - Operating system
   - Output of `python --version` and `pip list`

---

## Next Steps

Once your setup is verified:

1. ✅ Read the main `README.md`
2. ✅ Navigate to `week01_rag_foundations/`
3. ✅ Start with the Week 1 README
4. ✅ Begin `01_lecture_demo.ipynb`

---

## Additional Resources

### Documentation
- [LangChain Docs](https://python.langchain.com/)
- [Vertex AI Documentation](https://cloud.google.com/vertex-ai/docs)
- [LangSmith Documentation](https://docs.smith.langchain.com/)
- [ChromaDB Documentation](https://docs.trychroma.com/)

### Useful Commands

```bash
# Activate virtual environment
source .venv/bin/activate

# Deactivate virtual environment
deactivate

# Update all packages
pip install --upgrade -r requirements.txt

# List installed packages
pip list

# Check GCP configuration
gcloud config list

# Test GCP authentication
gcloud auth application-default print-access-token

# Launch Jupyter
jupyter notebook
```

---

**Setup complete!** 🎉 You're ready to start building RAG applications!

