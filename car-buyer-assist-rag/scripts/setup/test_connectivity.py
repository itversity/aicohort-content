#!/usr/bin/env python3
"""
Test script for connectivity validators

Run this script to test the validation logic before using the Streamlit UI.
This helps verify that all validators work correctly with your configuration.
"""

import sys
from pathlib import Path

# Add parent directory to path
parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir))

from utils.connectivity_validators import (
    validate_vertex_ai,
    validate_chromadb,
    validate_langsmith,
    load_environment_config,
    get_config_status
)


def print_section(title: str):
    """Print a formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def print_result(service_name: str, result: dict):
    """Print validation result in a formatted way"""
    status = "✅ PASSED" if result['success'] else "❌ FAILED"
    print(f"{service_name}: {status}")
    print(f"  Message: {result['message']}")
    if result.get('details'):
        print(f"  Details:")
        for line in result['details'].split('\n'):
            if line.strip():
                print(f"    {line}")
    if result.get('error_type'):
        print(f"  Error Type: {result['error_type']}")
    print()


def main():
    print_section("Connectivity Validators Test Script")
    
    # Load configuration
    print("Loading environment configuration...")
    config = load_environment_config()
    status, config = get_config_status()
    
    print("\n📋 Configuration Status:")
    print(f"  Google Project ID: {'✓ Set' if status['google']['project_id'] else '✗ Not Set'}")
    print(f"  Google Region: {'✓ Set' if status['google']['region'] else '✗ Not Set'}")
    print(f"  Google Credentials: {'✓ Set' if status['google']['credentials'] else '✗ Not Set'}")
    print(f"  ChromaDB Path: {'✓ Set' if status['chromadb']['path'] else '✗ Not Set'}")
    print(f"  LangSmith API Key: {'✓ Set' if status['langsmith']['api_key'] else '✗ Not Set'}")
    print(f"  LangSmith Project: {'✓ Set' if status['langsmith']['project'] else '✗ Not Set'}")
    
    # Test GCP Vertex AI
    print_section("Testing GCP Vertex AI")
    vertex_result = validate_vertex_ai(
        project_id=config['google']['project_id'],
        region=config['google']['region'],
        credentials_path=config['google']['credentials_path']
    )
    print_result("GCP Vertex AI", vertex_result)
    
    # Test ChromaDB
    print_section("Testing ChromaDB")
    chromadb_result = validate_chromadb(
        db_path=config['chromadb']['path']
    )
    print_result("ChromaDB", chromadb_result)
    
    # Test LangSmith
    print_section("Testing LangSmith")
    langsmith_result = validate_langsmith(
        api_key=config['langsmith']['api_key'],
        project=config['langsmith']['project']
    )
    print_result("LangSmith", langsmith_result)
    
    # Summary
    print_section("Test Summary")
    
    results = {
        'GCP Vertex AI': vertex_result,
        'ChromaDB': chromadb_result,
        'LangSmith': langsmith_result
    }
    
    passed = sum(1 for r in results.values() if r['success'])
    failed = len(results) - passed
    
    print(f"Total Services Tested: {len(results)}")
    print(f"Passed: {passed} ✅")
    print(f"Failed: {failed} ❌")
    
    if failed == 0:
        print("\n🎉 All connectivity tests passed! You're ready to use the application.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please review the errors above and fix your configuration.")
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

