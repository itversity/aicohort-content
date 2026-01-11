# Connectivity Validation Architecture

## System Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER BROWSER                                 │
│                    http://localhost:8501                             │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    STREAMLIT APPLICATION                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────┐  ┌──────────────────────────────────────────┐    │
│  │   Home.py    │  │         pages/                            │    │
│  │              │  │                                           │    │
│  │  • Dashboard │  │  1_connectivity.py                        │    │
│  │  • Stats     │─▶│   • Load config                           │    │
│  │  • Navigate  │  │   • Display status                        │    │
│  │              │  │   • Trigger tests                         │    │
│  └──────────────┘  │   • Show results                          │    │
│                    └───────────────┬───────────────────────────┘    │
│                                    │                                │
│                                    ▼                                │
│                    ┌───────────────────────────────┐               │
│                    │   utils/ Package               │               │
│                    │                                │               │
│                    │  connectivity_validators.py    │               │
│                    │   • load_environment_config()  │               │
│                    │   • get_config_status()        │               │
│                    │   • validate_vertex_ai()       │               │
│                    │   • validate_chromadb()        │               │
│                    │   • validate_langsmith()       │               │
│                    └───────────────┬───────────────┘               │
└────────────────────────────────────┼────────────────────────────────┘
                                     │
                 ┌───────────────────┼───────────────────┐
                 │                   │                   │
                 ▼                   ▼                   ▼
    ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
    │  GCP Vertex AI  │  │    ChromaDB     │  │   LangSmith     │
    │                 │  │                 │  │                 │
    │  • Embeddings   │  │  • Vector DB    │  │  • Traces       │
    │  • text-embed   │  │  • Persistence  │  │  • Monitoring   │
    │  • gemini-1.5   │  │  • Similarity   │  │  • Cost Track   │
    │                 │  │                 │  │                 │
    └─────────────────┘  └─────────────────┘  └─────────────────┘
         (Cloud)           (Local File)           (Cloud)
```

## Validation Flow

```
User clicks "Test All Connections"
            │
            ▼
┌───────────────────────────┐
│ Load .env Configuration   │
│  • Read environment vars  │
│  • Validate file paths    │
└────────────┬──────────────┘
             │
             ▼
┌───────────────────────────┐
│ Test GCP Vertex AI        │
│                           │
│ 1. Check project_id       │
│ 2. Check credentials      │
│ 3. Init embeddings        │
│ 4. Generate test embed    │
│ 5. Validate response      │
│                           │
│ Result: ✅ / ❌           │
└────────────┬──────────────┘
             │
             ▼
┌───────────────────────────┐
│ Test ChromaDB             │
│                           │
│ 1. Init client            │
│ 2. Create test collection │
│ 3. Write test doc         │
│ 4. Read test doc          │
│ 5. Query test doc         │
│ 6. Delete collection      │
│                           │
│ Result: ✅ / ❌           │
└────────────┬──────────────┘
             │
             ▼
┌───────────────────────────┐
│ Test LangSmith            │
│                           │
│ 1. Check API key          │
│ 2. Init client            │
│ 3. List projects          │
│ 4. Verify project exists  │
│                           │
│ Result: ✅ / ❌           │
└────────────┬──────────────┘
             │
             ▼
┌───────────────────────────┐
│ Display Results           │
│                           │
│ • Service status cards    │
│ • Success/error messages  │
│ • Detailed diagnostics    │
│ • Overall summary         │
│ • Timestamp               │
└───────────────────────────┘
```

## Error Handling Flow

```
Validation Function Called
         │
         ▼
┌─────────────────┐
│ Try Operation   │
└────┬────────────┘
     │
     ├─ Success ──────────▶ Return {success: True, message, details}
     │
     └─ Exception
            │
            ▼
    ┌───────────────────┐
    │ Parse Error Type  │
    └────┬──────────────┘
         │
         ├─ Authentication ──▶ Return {success: False, error_type: 'authentication', ...}
         │
         ├─ Permission ──────▶ Return {success: False, error_type: 'permission', ...}
         │
         ├─ Configuration ───▶ Return {success: False, error_type: 'configuration', ...}
         │
         ├─ Network ─────────▶ Return {success: False, error_type: 'network', ...}
         │
         └─ Unknown ─────────▶ Return {success: False, error_type: 'unknown', ...}
```

## Session State Management

```
┌─────────────────────────────────────────┐
│     Streamlit Session State             │
├─────────────────────────────────────────┤
│                                         │
│  st.session_state.validation_results:  │
│                                         │
│  {                                      │
│    'vertex_ai': {                       │
│      success: bool,                     │
│      message: str,                      │
│      details: str,                      │
│      error_type: str                    │
│    },                                   │
│    'chromadb': { ... },                 │
│    'langsmith': { ... },                │
│    'timestamp': datetime                │
│  }                                      │
│                                         │
└─────────────────────────────────────────┘
         │                  ▲
         │                  │
         ▼                  │
    Test Button        Page Refresh
         │                  │
         └──── Persists ────┘
```

## File Dependencies

```
Home.py
  └─ (No dependencies on utils)

pages/1_connectivity.py
  ├─ sys
  ├─ pathlib.Path
  └─ utils.connectivity_validators
      ├─ validate_vertex_ai()
      ├─ validate_chromadb()
      ├─ validate_langsmith()
      ├─ load_environment_config()
      └─ get_config_status()

utils/connectivity_validators.py
  ├─ os
  ├─ pathlib.Path
  ├─ time
  ├─ python-dotenv
  ├─ langchain_google_vertexai (runtime)
  ├─ chromadb (runtime)
  └─ langsmith (runtime)

scripts/setup/test_connectivity.py
  ├─ sys
  ├─ pathlib.Path
  └─ utils.connectivity_validators (same as above)
```

## Configuration Loading

```
Application Starts
       │
       ▼
┌──────────────────────┐
│ load_dotenv()        │
│ Reads .env file      │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ os.getenv()          │
│ Load variables:      │
│  • GOOGLE_PROJECT_ID │
│  • GOOGLE_REGION     │
│  • GOOGLE_APP_CREDS  │
│  • CHROMADB_PATH     │
│  • LANGSMITH_API_KEY │
│  • LANGSMITH_PROJECT │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ Return config dict   │
│ Used by validators   │
└──────────────────────┘
```

## UI Component Hierarchy

```
1_connectivity.py
│
├─ st.title("🔌 Connectivity Validation")
├─ st.markdown(instructions)
├─ st.info(note)
│
├─ display_configuration()
│   └─ st.expander("⚙️ Current Configuration")
│       ├─ col1: Google + ChromaDB config
│       └─ col2: LangSmith config
│
├─ Test Controls
│   ├─ Button: "Test All Connections"
│   ├─ Button: "Reset Results"
│   └─ Button: "View Logs"
│
├─ Results Display (3 columns)
│   ├─ display_service_status("GCP Vertex AI")
│   │   ├─ st.success() / st.error()
│   │   └─ st.expander("Details")
│   │
│   ├─ display_service_status("ChromaDB")
│   │   ├─ st.success() / st.error()
│   │   └─ st.expander("Details")
│   │
│   └─ display_service_status("LangSmith")
│       ├─ st.success() / st.error()
│       └─ st.expander("Details")
│
├─ Overall Status
│   └─ st.success() / st.warning() / st.info()
│
└─ Help Section
    └─ st.expander("❓ Need Help?")
        ├─ Common issues
        ├─ Solutions
        └─ Environment reference
```

---

## Legend

- `▶` = Navigation/Flow
- `▼` = Data flow down
- `▲` = Data flow up
- `┌─┐` = Component boundary
- `├─┤` = Component section
- `✅` = Success state
- `❌` = Error state
- `⏳` = Pending state

