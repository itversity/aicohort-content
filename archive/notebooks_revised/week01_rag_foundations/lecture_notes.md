# Week 1 Lecture Notes: RAG Foundations & Dataset Exploration

## Session Overview

**Duration:** 2 hours
**Format:** Live coding session with Q&A
**Goal:** Build first Toyota Q&A system with RAG

---

## Part 1: RAG Introduction (30 minutes)

### What is RAG?

**RAG = Retrieval-Augmented Generation**

A technique that combines:
1. **Information Retrieval** - Find relevant documents from a knowledge base
2. **Context Augmentation** - Add retrieved information to the prompt
3. **Text Generation** - LLM generates answer grounded in the retrieved context

### The Problem RAG Solves

**Without RAG:**
- LLMs only know what's in their training data
- Can't access private/proprietary information
- May hallucinate facts about recent information
- Expensive to fine-tune for domain-specific knowledge

**Example Problem:**
```
User: "What's the horsepower of the 2024 Toyota Camry?"
LLM (without RAG): "I don't have specific information about the 2024 Toyota Camry..."
```

**With RAG:**
```
User: "What's the horsepower of the 2024 Toyota Camry?"
System:
  1. Retrieves: "Toyota Camry Specifications... 2.5L 4-Cylinder: 203 HP..."
  2. Augments: Adds this to the prompt
  3. Generates: "The 2024 Toyota Camry offers 203 HP with the 2.5L engine..."
```

### RAG vs Alternatives

| Approach | Pros | Cons | Best For |
|----------|------|------|----------|
| **RAG** | ✅ Access to external knowledge<br>✅ Easy to update<br>✅ Cost-effective<br>✅ Transparent (see sources) | ❌ Depends on retrieval quality<br>❌ Additional complexity | Q&A systems, documentation search, customer support |
| **Fine-tuning** | ✅ Specialized domain knowledge<br>✅ Improved performance | ❌ Expensive<br>❌ Hard to update<br>❌ Requires lots of data | Specialized language tasks, style mimicry |
| **Prompt Engineering** | ✅ Simple<br>✅ No setup | ❌ Limited context window<br>❌ Can't access external data | General tasks with known information |

### RAG Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     RAG PIPELINE                             │
└─────────────────────────────────────────────────────────────┘

1. INGESTION (One-time setup)
   ┌──────────┐    ┌─────────┐    ┌──────────┐    ┌─────────┐
   │ PDF Docs │ -> │ Chunking│ -> │ Embedding│ -> │ Vector  │
   │          │    │         │    │          │    │ Database│
   └──────────┘    └─────────┘    └──────────┘    └─────────┘

2. QUERY (Real-time)
   ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌────────┐
   │User Query│ -> │ Retrieve │ -> │ Augment  │ -> │Generate│
   │          │    │ Top-K    │    │ Prompt   │    │Answer  │
   └──────────┘    └──────────┘    └──────────┘    └────────┘
```

### Key Components

**1. Document Loader**
- Extracts text from various sources (PDF, HTML, databases)
- This week: `pypdf` for Toyota PDFs

**2. Text Splitter / Chunker**
- Breaks documents into smaller pieces (chunks)
- This week: Simple 500-character chunks
- Week 2: Intelligent section-based chunking

**3. Embedding Model**
- Converts text to numerical vectors
- Captures semantic meaning
- This week: Vertex AI `text-embedding-004`

**4. Vector Database**
- Stores document chunks with their embeddings
- Enables fast similarity search
- This week: ChromaDB (in-memory)

**5. Retriever**
- Finds most relevant chunks for a query
- Uses cosine similarity between vectors
- Returns top-k results (e.g., top 3 chunks)

**6. LLM (Generator)**
- Receives query + retrieved context
- Generates natural language answer
- This week: Vertex AI Gemini Pro

---

## Part 2: Toyota Dataset Analysis (45 minutes)

### Dataset Overview

**What We Have:**
- 8 PDF files with Toyota vehicle specifications
- Total size: ~590 KB
- Content: Structured specification documents
- Goal: Build Q&A system for car buyers

### File Analysis

| Filename | Size | Pages | Content Type |
|----------|------|-------|--------------|
| Introduction_to_Toyota_Car_Sales.pdf | 49 KB | 2 | Brand overview |
| Toyota_Camry_Specifications.pdf | 74 KB | 1 | Midsize sedan |
| Toyota_Corolla_Specifications.pdf | 73 KB | 1 | Compact sedan |
| Toyota_Highlander_Specifications.pdf | 75 KB | 1 | Midsize SUV |
| Toyota_Prius_Specifications.pdf | 75 KB | 1 | Hybrid sedan |
| Toyota_RAV4_Specifications.pdf | 76 KB | 1 | Compact SUV |
| Toyota_Tacoma_Specifications.pdf | 74 KB | 1 | Midsize truck |
| Toyota_bZ4X_Specifications.pdf | 84 KB | 4 | Electric SUV |

### Document Structure Pattern

**Common sections across all spec documents:**

1. **Overview**
   - Vehicle description
   - Target audience
   - Key highlights

2. **Engine Options**
   - Power output (HP)
   - Transmission type
   - Fuel economy (MPG)
   - Multiple variants (gas, hybrid, etc.)

3. **Design**
   - Exterior styling
   - Interior features
   - Dimensions

4. **Comfort & Technology**
   - Infotainment system
   - Connectivity (Apple CarPlay, Android Auto)
   - Interior features

5. **Competitor Comparison** (some models)
   - How Toyota compares to rivals
   - Key differentiators

6. **Sales Strategies** (some models)
   - Key selling points
   - Target customer profiles

### Typical Car Buyer Queries

Understanding user intent helps design better RAG systems:

**1. Specification Queries (Factual)**
- "What is the Camry's horsepower?"
- "What's the fuel economy of the RAV4 hybrid?"
- "How much can the Tacoma tow?"

**2. Feature Queries (Exploratory)**
- "What safety features does the Highlander have?"
- "Does the Prius have wireless CarPlay?"
- "What technology is in the bZ4X?"

**3. Comparison Queries (Analytical)**
- "Compare Camry vs Corolla fuel economy"
- "What's the difference between RAV4 and Highlander?"
- "Which Toyota has the best MPG?"

**4. General Queries (Informational)**
- "Tell me about Toyota reliability"
- "What is Toyota Safety Sense?"
- "What warranty does Toyota offer?"

### Success Criteria

Our RAG system should:
- ✅ Answer spec queries with correct numbers
- ✅ Cite sources (which document/model)
- ✅ Handle multi-model questions
- ✅ Admit when it doesn't know ("I don't have information on...")
- ✅ Respond in under 5 seconds

---

## Part 3: Building First RAG System (45 minutes)

### Step 1: Environment Setup

**Install required packages:**
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

**Key libraries:**
- `pypdf` - PDF text extraction
- `langchain-google-vertexai` - Vertex AI integration
- `chromadb` - Vector database
- `langchain` - RAG orchestration

### Step 2: Load PDFs

**Goal:** Extract text from all 8 Toyota PDFs

```python
from pathlib import Path
import pypdf

def load_pdf(pdf_path):
    """Extract text from a PDF file."""
    with open(pdf_path, 'rb') as f:
        reader = pypdf.PdfReader(f)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    return text

# Load all PDFs
data_dir = Path("../data/car-specs/toyota-specs")
pdfs = list(data_dir.glob("*.pdf"))

documents = []
for pdf in sorted(pdfs):
    text = load_pdf(pdf)
    documents.append({
        "content": text,
        "source": pdf.name,
        "model": pdf.stem.replace("_", " ")
    })

print(f"Loaded {len(documents)} documents")
```

**Expected output:**
```
Loaded 8 documents
```

### Step 3: Chunking

**Goal:** Split documents into smaller pieces for better retrieval

**Why chunk?**
- Embeddings work best on focused text (200-1000 tokens)
- Retrieve only relevant sections, not entire documents
- Better signal-to-noise ratio for the LLM

**Simple chunking strategy (Week 1):**
```python
def simple_chunk(text, chunk_size=500, overlap=50):
    """Split text into overlapping chunks."""
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap  # Overlap to avoid splitting sentences
    
    return chunks

# Chunk all documents
all_chunks = []
for doc in documents:
    chunks = simple_chunk(doc["content"], chunk_size=500)
    for i, chunk in enumerate(chunks):
        all_chunks.append({
            "content": chunk,
            "model": doc["model"],
            "source": doc["source"],
            "chunk_id": f"{doc['source']}_{i}"
        })

print(f"Created {len(all_chunks)} chunks")
```

**Expected output:**
```
Created ~80-100 chunks
```

### Step 4: Create Embeddings

**Goal:** Convert text chunks to numerical vectors

**What are embeddings?**
- Vectors that capture semantic meaning
- Similar text → Similar vectors
- Enable "semantic search" (meaning-based, not keyword-based)

```python
from langchain_google_vertexai import VertexAIEmbeddings

# Initialize embedding model
embeddings = VertexAIEmbeddings(
    model_name="text-embedding-004"
)

# Example: Embed a query
query = "What's the Camry's horsepower?"
query_embedding = embeddings.embed_query(query)

print(f"Embedding dimensions: {len(query_embedding)}")
print(f"First 5 values: {query_embedding[:5]}")
```

**Expected output:**
```
Embedding dimensions: 768
First 5 values: [0.023, -0.045, 0.067, -0.012, 0.034]
```

### Step 5: Store in Vector Database

**Goal:** Store chunks with embeddings for fast retrieval

```python
import chromadb
from chromadb.utils import embedding_functions

# Initialize ChromaDB
client = chromadb.Client()
collection = client.create_collection(
    name="toyota_specs_week1",
    metadata={"description": "Toyota specifications - Week 1"}
)

# Prepare data
documents_list = [chunk["content"] for chunk in all_chunks]
metadatas = [{"model": chunk["model"], "source": chunk["source"]} 
             for chunk in all_chunks]
ids = [chunk["chunk_id"] for chunk in all_chunks]

# Add to collection (ChromaDB will create embeddings)
collection.add(
    documents=documents_list,
    metadatas=metadatas,
    ids=ids
)

print(f"✓ Stored {len(documents_list)} chunks in ChromaDB")
```

### Step 6: Query and Retrieve

**Goal:** Find relevant chunks for a user query

```python
# Test query
query = "What is the Toyota Camry's horsepower?"

# Retrieve top 3 most relevant chunks
results = collection.query(
    query_texts=[query],
    n_results=3
)

print("Top 3 relevant chunks:")
for i, (doc, metadata) in enumerate(zip(
    results['documents'][0],
    results['metadatas'][0]
), 1):
    print(f"\n{i}. Model: {metadata['model']}")
    print(f"   Content: {doc[:200]}...")
```

**Expected output:**
```
Top 3 relevant chunks:
1. Model: Toyota Camry
   Content: Engine Options
   2.5L 4-Cylinder Gasoline Engine
   Power Output: 203 HP...
```

### Step 7: Generate Answer with LLM

**Goal:** Use retrieved context to generate a natural language answer

```python
from langchain_google_vertexai import VertexAI

# Initialize LLM
llm = VertexAI(
    model_name="gemini-pro",
    temperature=0  # Deterministic for factual answers
)

# Build prompt with context
context = "\n\n".join(results['documents'][0])

prompt = f"""You are a helpful Toyota sales assistant. Answer the customer's question based on the provided information.

Context from Toyota specifications:
{context}

Customer question: {query}

Provide a clear, accurate answer. If the information isn't in the context, say so.

Answer:"""

# Generate answer
answer = llm.invoke(prompt)
print(f"\nQuestion: {query}")
print(f"Answer: {answer}")
```

**Expected output:**
```
Question: What is the Toyota Camry's horsepower?
Answer: The Toyota Camry offers multiple engine options with different horsepower ratings:
- 2.5L 4-Cylinder: 203 HP
- 3.5L V6: 301 HP
- Hybrid: 208 HP (combined)
```

### Step 8: Complete RAG Function

**Goal:** Wrap everything in a reusable function

```python
def ask_toyota_question(question, collection, llm):
    """
    Ask a question about Toyota vehicles using RAG.
    
    Args:
        question: User's question
        collection: ChromaDB collection with Toyota specs
        llm: Language model for generation
        
    Returns:
        tuple: (answer, sources)
    """
    # 1. Retrieve relevant chunks
    results = collection.query(
        query_texts=[question],
        n_results=3
    )
    
    # 2. Build context
    context = "\n\n".join(results['documents'][0])
    sources = results['metadatas'][0]
    
    # 3. Create prompt
    prompt = f"""You are a helpful Toyota sales assistant. Answer based on the provided information.

Context:
{context}

Question: {question}

Answer:"""
    
    # 4. Generate answer
    answer = llm.invoke(prompt)
    
    return answer, sources

# Test with multiple queries
test_queries = [
    "What's the Camry's horsepower?",
    "What safety features does the RAV4 have?",
    "Tell me about Toyota reliability"
]

for q in test_queries:
    answer, sources = ask_toyota_question(q, collection, llm)
    print(f"\nQ: {q}")
    print(f"A: {answer}")
    print(f"Sources: {[s['model'] for s in sources]}")
```

---

## Key Takeaways

### What We Built Today

✅ **Complete RAG pipeline** for Toyota specifications
✅ **Document loading** from PDFs
✅ **Simple chunking** strategy (500 characters)
✅ **Vector embeddings** with Vertex AI
✅ **Vector storage** in ChromaDB
✅ **Semantic retrieval** with cosine similarity
✅ **Answer generation** with Gemini Pro

### Limitations of Week 1 Approach

❌ **Fixed-size chunking** may split important information
❌ **No metadata filtering** (can't search by model, section)
❌ **No conversation history** (can't handle follow-up questions)
❌ **Simple retrieval** (Week 5 will improve this)

### Coming in Week 2

**Intelligent Chunking:**
- Section-based chunking (respects document structure)
- Metadata extraction (model, section, topics)
- Optimized for car buyer query patterns
- Better retrieval accuracy

---

## Additional Resources

### Documentation
- [LangChain Documentation](https://python.langchain.com/)
- [Vertex AI Gemini API](https://cloud.google.com/vertex-ai/docs/generative-ai/model-reference/gemini)
- [ChromaDB Documentation](https://docs.trychroma.com/)

### Research Papers
- [RAG: Retrieval-Augmented Generation](https://arxiv.org/abs/2005.11401) - Original paper by Lewis et al.
- [Improving Language Models by Retrieving from Trillions of Tokens](https://arxiv.org/abs/2112.04426) - RETRO model

### Videos
- [RAG Explained](https://www.youtube.com/watch?v=T-D1OfcDW1M) - 10 minute overview
- [Building RAG Applications](https://www.youtube.com/watch?v=LhnCsygAvzY) - Hands-on tutorial

---

## Practice Exercises

1. **Modify chunk size:** Try 200, 500, and 1000 characters. Which works best?

2. **Add more metadata:** Include page numbers, section names in metadata.

3. **Experiment with retrieval:** Try retrieving 1, 3, 5, 10 chunks. What's optimal?

4. **Test edge cases:** Ask questions that span multiple models or require inference.

5. **Improve prompts:** Add few-shot examples, adjust system prompt, format output.

---

**Next Session:** Week 2 - Smart Chunking Strategies

See you next week! 🚗


