"""
Example: Embedding Toyota Specification Chunks with text-embedding-3-small
This script demonstrates how to embed the chunked documents and store them in ChromaDB.
"""

import json
from pathlib import Path
from openai import OpenAI
import time

def embed_chunks_with_openai():
    """Embed all chunks using OpenAI's text-embedding-3-small model"""
    
    print("=" * 80)
    print("EMBEDDING TOYOTA SPECIFICATION CHUNKS")
    print("=" * 80)
    
    # Initialize OpenAI client
    client = OpenAI()  # Requires OPENAI_API_KEY environment variable
    
    # Load chunks
    chunks_file = Path(__file__).parent / "chunks_output.json"
    print(f"\n📂 Loading chunks from: {chunks_file.name}")
    
    with open(chunks_file, 'r') as f:
        chunks = json.load(f)
    
    print(f"✓ Loaded {len(chunks)} chunks")
    
    # Embedding configuration
    EMBEDDING_MODEL = "text-embedding-3-small"
    EMBEDDING_DIMENSIONS = 1536  # Can reduce to 512 for faster search
    
    print(f"\n⚙️  Embedding Configuration:")
    print(f"   Model: {EMBEDDING_MODEL}")
    print(f"   Dimensions: {EMBEDDING_DIMENSIONS}")
    
    # Embed each chunk
    print(f"\n🔄 Embedding chunks...")
    start_time = time.time()
    total_tokens = 0
    
    for i, chunk in enumerate(chunks, 1):
        try:
            # Create embedding
            response = client.embeddings.create(
                model=EMBEDDING_MODEL,
                input=chunk['content'],
                dimensions=EMBEDDING_DIMENSIONS
            )
            
            # Add embedding to chunk
            chunk['embedding'] = response.data[0].embedding
            
            # Track usage
            total_tokens += response.usage.total_tokens
            
            # Progress indicator
            if i % 5 == 0 or i == len(chunks):
                print(f"   Processed {i}/{len(chunks)} chunks...")
        
        except Exception as e:
            print(f"   ⚠️  Error embedding chunk {i}: {e}")
            chunk['embedding'] = None
    
    elapsed_time = time.time() - start_time
    
    # Calculate cost
    COST_PER_1M_TOKENS = 0.02  # $0.02 per 1M tokens
    total_cost = (total_tokens / 1_000_000) * COST_PER_1M_TOKENS
    
    print(f"\n✓ Embedding complete!")
    print(f"\n📊 Statistics:")
    print(f"   Total chunks: {len(chunks)}")
    print(f"   Total tokens: {total_tokens:,}")
    print(f"   Total cost: ${total_cost:.6f}")
    print(f"   Time taken: {elapsed_time:.2f} seconds")
    print(f"   Avg time per chunk: {elapsed_time/len(chunks):.3f} seconds")
    
    # Save chunks with embeddings
    output_file = Path(__file__).parent / "chunks_with_embeddings.json"
    print(f"\n💾 Saving embeddings to: {output_file.name}")
    
    with open(output_file, 'w') as f:
        json.dump(chunks, f, indent=2)
    
    print(f"✓ Saved successfully!")
    
    # Display sample embedding
    print(f"\n{'=' * 80}")
    print("SAMPLE EMBEDDING")
    print(f"{'=' * 80}")
    
    sample_chunk = chunks[5]  # Camry Design chunk
    print(f"\nChunk: {sample_chunk['chunk_id']}")
    print(f"Model: {sample_chunk['metadata']['model']}")
    print(f"Section: {sample_chunk['metadata']['section']}")
    print(f"Content preview: {sample_chunk['content'][:200]}...")
    print(f"\nEmbedding (first 10 dimensions): {sample_chunk['embedding'][:10]}")
    print(f"Embedding shape: {len(sample_chunk['embedding'])} dimensions")
    
    return chunks


def store_in_chromadb(chunks_with_embeddings):
    """Store embedded chunks in ChromaDB vector database"""
    try:
        import chromadb
    except ImportError:
        print("\n⚠️  ChromaDB not installed. Install with: pip install chromadb")
        return
    
    print(f"\n{'=' * 80}")
    print("STORING IN CHROMADB")
    print(f"{'=' * 80}")
    
    # Initialize ChromaDB client
    client = chromadb.Client()
    
    # Create collection
    collection_name = "toyota_specifications"
    print(f"\n📦 Creating collection: {collection_name}")
    
    # Delete if exists (for clean start)
    try:
        client.delete_collection(collection_name)
    except:
        pass
    
    collection = client.create_collection(
        name=collection_name,
        metadata={"description": "Toyota vehicle specifications for RAG"}
    )
    
    # Prepare data for ChromaDB
    documents = [c['content'] for c in chunks_with_embeddings]
    embeddings = [c['embedding'] for c in chunks_with_embeddings if c['embedding'] is not None]
    metadatas = [c['metadata'] for c in chunks_with_embeddings]
    ids = [c['chunk_id'] for c in chunks_with_embeddings]
    
    print(f"\n🔄 Adding {len(documents)} chunks to collection...")
    
    # Add to collection
    collection.add(
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids
    )
    
    print(f"✓ Added successfully!")
    
    # Test query
    print(f"\n{'=' * 80}")
    print("TEST QUERY")
    print(f"{'=' * 80}")
    
    test_query = "What safety features does the Highlander have?"
    print(f"\nQuery: '{test_query}'")
    
    results = collection.query(
        query_texts=[test_query],
        n_results=3
    )
    
    print(f"\n📋 Top 3 Results:")
    for i, (doc, metadata, distance) in enumerate(zip(
        results['documents'][0],
        results['metadatas'][0],
        results['distances'][0]
    ), 1):
        print(f"\n{i}. {metadata['model']} - {metadata['section']}")
        print(f"   Similarity: {1 - distance:.4f}")
        print(f"   Content: {doc[:150]}...")
    
    return collection


def demonstrate_hybrid_search(collection, chunks_with_embeddings):
    """Demonstrate hybrid search (semantic + metadata filtering)"""
    
    print(f"\n{'=' * 80}")
    print("HYBRID SEARCH EXAMPLE")
    print(f"{'=' * 80}")
    
    # Example 1: Filter by model + semantic search
    query = "What's the fuel economy?"
    model_filter = "Toyota Camry"
    
    print(f"\nQuery: '{query}'")
    print(f"Filter: Model = '{model_filter}'")
    
    results = collection.query(
        query_texts=[query],
        n_results=3,
        where={"model": model_filter}
    )
    
    print(f"\n📋 Results (filtered to Camry only):")
    for i, (doc, metadata) in enumerate(zip(
        results['documents'][0],
        results['metadatas'][0]
    ), 1):
        print(f"\n{i}. {metadata['section']}")
        print(f"   Topics: {', '.join(metadata.get('topics', []))}")
        print(f"   Content: {doc[:120]}...")
    
    # Example 2: Filter by topic
    print(f"\n{'─' * 80}")
    query = "Tell me about hybrid options"
    
    print(f"\nQuery: '{query}'")
    print(f"Filter: Topic contains 'hybrid'")
    
    # Manual filtering (ChromaDB has limited array support in where clause)
    query_embedding = get_query_embedding(query)
    
    hybrid_chunks = [c for c in chunks_with_embeddings 
                     if 'hybrid' in c['metadata'].get('topics', [])]
    
    print(f"\n✓ Found {len(hybrid_chunks)} chunks with 'hybrid' topic")
    print(f"   Models: {set(c['metadata']['model'] for c in hybrid_chunks)}")


def get_query_embedding(query: str) -> list:
    """Generate embedding for a query"""
    client = OpenAI()
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=query,
        dimensions=1536
    )
    return response.data[0].embedding


def main():
    """Main execution"""
    
    # Step 1: Embed chunks
    chunks_with_embeddings = embed_chunks_with_openai()
    
    # Step 2: Store in ChromaDB
    collection = store_in_chromadb(chunks_with_embeddings)
    
    # Step 3: Demonstrate hybrid search
    if collection:
        demonstrate_hybrid_search(collection, chunks_with_embeddings)
    
    print(f"\n{'=' * 80}")
    print("✅ COMPLETE - Chunks embedded and ready for RAG!")
    print(f"{'=' * 80}")
    print("\nNext steps:")
    print("1. Integrate with your LLM (GPT-4, Claude, etc.)")
    print("2. Build retrieval pipeline with query processing")
    print("3. Add re-ranking if needed")
    print("4. Test with real user queries")
    print("5. Monitor and optimize retrieval accuracy")
    

if __name__ == "__main__":
    # Check for OpenAI API key
    import os
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY not found in environment")
        print("   Set it with: export OPENAI_API_KEY='your-key-here'")
        print("\n   Exiting...")
    else:
        main()

