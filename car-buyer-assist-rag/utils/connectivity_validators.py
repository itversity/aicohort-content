"""
Connectivity validation utilities for external services

This module provides functions to test connections to:
- GCP Vertex AI (embedding and LLM services)
- ChromaDB (vector database)
- LangSmith (observability platform)
"""

import os
from pathlib import Path
from typing import Dict, Any
import time


def validate_vertex_ai(project_id: str, region: str, credentials_path: str = None) -> Dict[str, Any]:
    """
    Test Vertex AI connection by generating a sample embedding
    
    Args:
        project_id: GCP project ID
        region: GCP region (e.g., 'us-central1')
        credentials_path: Path to service account key file
    
    Returns:
        dict with keys:
            - success (bool): Whether validation passed
            - message (str): Short status message
            - details (str): Additional technical details
            - error_type (str): Type of error if failed
    """
    try:
        # Check if required parameters are provided
        if not project_id:
            return {
                'success': False,
                'message': 'Project ID not configured',
                'details': 'GOOGLE_PROJECT_ID environment variable is not set',
                'error_type': 'configuration'
            }
        
        if not region:
            return {
                'success': False,
                'message': 'Region not configured',
                'details': 'GOOGLE_REGION environment variable is not set',
                'error_type': 'configuration'
            }
        
        # Check credentials file exists
        if credentials_path:
            creds_file = Path(credentials_path)
            if not creds_file.exists():
                return {
                    'success': False,
                    'message': 'Credentials file not found',
                    'details': f'File does not exist: {credentials_path}',
                    'error_type': 'authentication'
                }
        
        # Import Vertex AI libraries
        try:
            from langchain_google_vertexai import VertexAIEmbeddings
        except ImportError as e:
            return {
                'success': False,
                'message': 'Vertex AI library not installed',
                'details': f'Import error: {str(e)}. Run: pip install langchain-google-vertexai',
                'error_type': 'configuration'
            }
        
        # Initialize embeddings model
        start_time = time.time()
        embeddings = VertexAIEmbeddings(
            model_name="text-embedding-004",
            project=project_id,
            location=region
        )
        
        # Test with sample text
        test_text = "Test connection to Vertex AI"
        embedding_vector = embeddings.embed_query(test_text)
        elapsed_time = time.time() - start_time
        
        # Validate response
        if not isinstance(embedding_vector, list) or len(embedding_vector) == 0:
            return {
                'success': False,
                'message': 'Invalid embedding response',
                'details': 'Vertex AI returned unexpected response format',
                'error_type': 'api_error'
            }
        
        return {
            'success': True,
            'message': 'Connected successfully',
            'details': f'Generated {len(embedding_vector)}-dimensional embedding in {elapsed_time:.2f}s\nModel: text-embedding-004\nProject: {project_id}\nRegion: {region}'
        }
        
    except Exception as e:
        error_msg = str(e)
        
        # Parse specific error types
        if 'credentials' in error_msg.lower() or 'authentication' in error_msg.lower():
            error_type = 'authentication'
            message = 'Authentication failed'
            details = f'{error_msg}\n\nCheck:\n1. GOOGLE_APPLICATION_CREDENTIALS path is correct\n2. Service account has proper permissions\n3. Run: gcloud auth application-default login'
        elif 'not enabled' in error_msg.lower() or 'enable the api' in error_msg.lower():
            error_type = 'api_not_enabled'
            message = 'Vertex AI API not enabled'
            details = f'{error_msg}\n\nEnable the API:\ngcloud services enable aiplatform.googleapis.com --project={project_id}'
        elif 'quota' in error_msg.lower() or 'limit' in error_msg.lower():
            error_type = 'quota_exceeded'
            message = 'API quota exceeded'
            details = f'{error_msg}\n\nCheck billing and quotas in GCP Console'
        elif 'permission' in error_msg.lower():
            error_type = 'permission_denied'
            message = 'Permission denied'
            details = f'{error_msg}\n\nEnsure service account has roles:\n- roles/aiplatform.user\n- roles/aiplatform.serviceAgent'
        else:
            error_type = 'unknown'
            message = 'Connection failed'
            details = f'{error_msg}'
        
        return {
            'success': False,
            'message': message,
            'details': details,
            'error_type': error_type
        }


def validate_chromadb(db_path: str = "./chroma_db") -> Dict[str, Any]:
    """
    Test ChromaDB connection with read/write operations
    
    Args:
        db_path: Path to ChromaDB persistence directory
    
    Returns:
        dict with keys:
            - success (bool): Whether validation passed
            - message (str): Short status message
            - details (str): Additional technical details
            - error_type (str): Type of error if failed
    """
    try:
        # Import ChromaDB
        try:
            import chromadb
            from chromadb.config import Settings
        except ImportError as e:
            return {
                'success': False,
                'message': 'ChromaDB not installed',
                'details': f'Import error: {str(e)}. Run: pip install chromadb',
                'error_type': 'configuration'
            }
        
        # Ensure directory exists
        db_path_obj = Path(db_path)
        db_path_obj.mkdir(parents=True, exist_ok=True)
        
        # Initialize ChromaDB client
        start_time = time.time()
        client = chromadb.PersistentClient(path=db_path)
        
        # Create or get test collection
        test_collection_name = "connectivity_test"
        
        # Delete test collection if it exists (cleanup from previous tests)
        try:
            client.delete_collection(name=test_collection_name)
        except:
            pass  # Collection doesn't exist, which is fine
        
        # Create test collection
        collection = client.create_collection(
            name=test_collection_name,
            metadata={"description": "Temporary collection for connectivity testing"}
        )
        
        # Test write operation
        test_embedding = [0.1] * 768  # 768-dimensional test vector
        collection.add(
            ids=["test_doc_1"],
            embeddings=[test_embedding],
            documents=["Test document for connectivity validation"],
            metadatas=[{"source": "connectivity_test", "timestamp": time.time()}]
        )
        
        # Test read operation
        results = collection.get(ids=["test_doc_1"])
        
        if not results or not results['documents']:
            return {
                'success': False,
                'message': 'Read operation failed',
                'details': 'Could not retrieve test document from ChromaDB',
                'error_type': 'database_error'
            }
        
        # Test query operation
        query_results = collection.query(
            query_embeddings=[test_embedding],
            n_results=1
        )
        
        # Cleanup: delete test collection
        client.delete_collection(name=test_collection_name)
        
        elapsed_time = time.time() - start_time
        
        return {
            'success': True,
            'message': 'Connected successfully',
            'details': f'Database operations validated in {elapsed_time:.2f}s\nPath: {db_path_obj.resolve()}\nRead/Write: ✓\nQuery: ✓'
        }
        
    except PermissionError as e:
        return {
            'success': False,
            'message': 'Permission denied',
            'details': f'Cannot write to directory: {db_path}\n\nError: {str(e)}\n\nCheck directory permissions',
            'error_type': 'permission'
        }
    except Exception as e:
        error_msg = str(e)
        return {
            'success': False,
            'message': 'Database connection failed',
            'details': f'{error_msg}\n\nCheck:\n1. Directory path is accessible\n2. No other process is locking the database\n3. ChromaDB version is compatible',
            'error_type': 'database_error'
        }


def validate_langsmith(api_key: str = None, project: str = None) -> Dict[str, Any]:
    """
    Test LangSmith API connection
    
    Args:
        api_key: LangSmith API key
        project: LangSmith project name
    
    Returns:
        dict with keys:
            - success (bool): Whether validation passed
            - message (str): Short status message
            - details (str): Additional technical details
            - error_type (str): Type of error if failed
    """
    try:
        # Check if API key is provided
        if not api_key:
            return {
                'success': False,
                'message': 'API key not configured',
                'details': 'LANGSMITH_API_KEY environment variable is not set',
                'error_type': 'configuration'
            }
        
        # Import LangSmith
        try:
            from langsmith import Client
        except ImportError as e:
            return {
                'success': False,
                'message': 'LangSmith not installed',
                'details': f'Import error: {str(e)}. Run: pip install langsmith',
                'error_type': 'configuration'
            }
        
        # Initialize client
        start_time = time.time()
        client = Client(api_key=api_key)
        
        # Test API connection by listing projects
        projects = list(client.list_projects())
        elapsed_time = time.time() - start_time
        
        project_names = [p.name for p in projects]
        
        # Check if specified project exists
        project_status = ""
        if project:
            if project in project_names:
                project_status = f"\nConfigured project '{project}': ✓ Found"
            else:
                project_status = f"\n⚠️  Configured project '{project}' not found in available projects"
        
        return {
            'success': True,
            'message': 'Connected successfully',
            'details': f'API validated in {elapsed_time:.2f}s\nAvailable projects: {len(projects)}\nProjects: {", ".join(project_names[:5])}{"..." if len(project_names) > 5 else ""}{project_status}'
        }
        
    except Exception as e:
        error_msg = str(e)
        
        # Parse specific error types
        if 'api key' in error_msg.lower() or 'unauthorized' in error_msg.lower() or '401' in error_msg:
            error_type = 'authentication'
            message = 'Invalid API key'
            details = f'{error_msg}\n\nCheck:\n1. LANGSMITH_API_KEY is correct\n2. API key has not expired\n3. Get your API key from: https://smith.langchain.com'
        elif 'network' in error_msg.lower() or 'connection' in error_msg.lower():
            error_type = 'network'
            message = 'Network connection failed'
            details = f'{error_msg}\n\nCheck:\n1. Internet connection is active\n2. Firewall allows access to api.smith.langchain.com\n3. No proxy issues'
        else:
            error_type = 'unknown'
            message = 'Connection failed'
            details = f'{error_msg}'
        
        return {
            'success': False,
            'message': message,
            'details': details,
            'error_type': error_type
        }


def load_environment_config() -> Dict[str, Any]:
    """
    Load and validate environment variables for all services
    
    Returns:
        dict with configuration values for all services
    """
    from dotenv import load_dotenv
    
    # Load environment variables from .env file
    load_dotenv()
    
    config = {
        'google': {
            'project_id': os.getenv('GOOGLE_PROJECT_ID'),
            'region': os.getenv('GOOGLE_REGION', 'us-central1'),
            'credentials_path': os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        },
        'chromadb': {
            'path': os.getenv('CHROMADB_PATH', './chroma_db')
        },
        'langsmith': {
            'api_key': os.getenv('LANGSMITH_API_KEY'),
            'project': os.getenv('LANGSMITH_PROJECT'),
            'tracing': os.getenv('LANGSMITH_TRACING', 'false')
        }
    }
    
    return config


def get_config_status() -> Dict[str, Dict[str, bool]]:
    """
    Check which environment variables are set
    
    Returns:
        dict with service names and their configuration status
    """
    config = load_environment_config()
    
    status = {
        'google': {
            'project_id': bool(config['google']['project_id']),
            'region': bool(config['google']['region']),
            'credentials': bool(config['google']['credentials_path'])
        },
        'chromadb': {
            'path': bool(config['chromadb']['path'])
        },
        'langsmith': {
            'api_key': bool(config['langsmith']['api_key']),
            'project': bool(config['langsmith']['project']),
            'tracing': bool(config['langsmith']['tracing'])
        }
    }
    
    return status, config

