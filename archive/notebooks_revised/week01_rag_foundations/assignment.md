# Week 1 Assignment: Build Your First Toyota RAG System

## Assignment Overview

**Goal:** Build a complete RAG (Retrieval-Augmented Generation) system that answers questions about Toyota vehicles using the 8 specification PDFs.

**What You'll Build:**
- PDF loading and text extraction pipeline
- Simple chunking implementation
- Vector embedding and storage system
- Query and retrieval mechanism
- Answer generation with Gemini Pro

**Deliverable:** Completed Jupyter notebook with all functions working and test queries answered.

---

## Learning Objectives

By completing this assignment, you will:
- ✅ Load and extract text from PDF documents
- ✅ Implement a chunking strategy
- ✅ Create vector embeddings using Vertex AI
- ✅ Store and retrieve documents from a vector database
- ✅ Build an end-to-end RAG pipeline
- ✅ Generate accurate answers grounded in retrieved context

---

## Setup

### Prerequisites

1. **Environment activated:**
   ```bash
   source .venv/bin/activate
   ```

2. **Dependencies installed:**
   ```bash
   pip install -r requirements.txt
   ```

3. **GCP credentials configured:**
   ```bash
   gcloud auth application-default login
   ```

4. **Environment variables set:**
   - Copy `env_template.txt` to `.env`
   - Fill in your GCP_PROJECT_ID and other required values

### Files You'll Use

- **Starter notebook:** `02_assignment_starter.ipynb`
- **Test queries:** `test_queries.json`
- **Toyota PDFs:** `../data/car-specs/toyota-specs/*.pdf`
- **Utilities:** `../shared_resources/utils.py`

---

## Part 1: Data Exploration (15 points)

### Task 1.1: List All PDF Files
Write code to list all Toyota specification PDFs with their file sizes.

**Requirements:**
- Use Python's `Path` or `glob` to find all `.pdf` files
- Display filename and size in KB
- Sort alphabetically

**Expected Output:**
```
Introduction_to_Toyota_Car_Sales.pdf: 49.2 KB
Toyota_Camry_Specifications.pdf: 74.3 KB
...
```

### Task 1.2: Extract and Analyze Text
Load one PDF (Toyota_Camry_Specifications.pdf) and analyze its content.

**Requirements:**
- Extract text using `pypdf`
- Count characters, words, and lines
- Display first 500 characters

**Expected Output:**
```
Characters: 3,073
Words: 434
Lines: 45
First 500 chars: Overview\nThe Toyota Camry is a premium...
```

### Task 1.3: Identify Document Structure
Manually review 2-3 PDFs and identify common sections.

**Requirements:**
- List the main sections found in spec documents
- Note which sections appear in all documents
- Write 2-3 sentences describing the structure

**Deliverable:** Written analysis in a markdown cell

---

## Part 2: PDF Loading Pipeline (10 points)

### Task 2.1: Implement load_pdf Function

Complete the `load_pdf()` function in the starter notebook.

**Function signature:**
```python
def load_pdf(pdf_path: str) -> str:
    """
    Load and extract text from a PDF file.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        str: Full text content extracted from the PDF
    """
    # TODO: Your implementation here
    pass
```

**Requirements:**
- Use `pypdf.PdfReader` to read the PDF
- Extract text from all pages
- Concatenate all text into a single string
- Return the full text

**Test:**
```python
text = load_pdf("../data/car-specs/toyota-specs/Toyota_Camry_Specifications.pdf")
assert len(text) > 2000, "Should extract substantial text"
assert "Camry" in text, "Should contain model name"
print(f"✓ Loaded {len(text)} characters")
```

### Task 2.2: Load All Toyota PDFs

Load all 8 PDFs into a list of dictionaries.

**Requirements:**
- Create a list called `documents`
- Each document should be a dict with keys:
  - `content`: Full text
  - `source`: Filename (e.g., "Toyota_Camry_Specifications.pdf")
  - `model`: Model name (e.g., "Toyota Camry")
- Use the provided `extract_model_name()` utility function

**Test:**
```python
assert len(documents) == 8, "Should load all 8 PDFs"
assert all('content' in doc for doc in documents), "All docs should have content"
print(f"✓ Loaded {len(documents)} documents")
```

---

## Part 3: Chunking Implementation (15 points)

### Task 3.1: Implement simple_chunk Function

Complete the `simple_chunk()` function.

**Function signature:**
```python
def simple_chunk(text: str, chunk_size: int = 500, overlap: int = 50) -> list:
    """
    Split text into overlapping chunks.
    
    Args:
        text: Text to chunk
        chunk_size: Size of each chunk in characters
        overlap: Number of overlapping characters between chunks
        
    Returns:
        list: List of text chunks
    """
    # TODO: Your implementation here
    pass
```

**Requirements:**
- Split text into chunks of `chunk_size` characters
- Include `overlap` characters between adjacent chunks
- Handle edge cases (text shorter than chunk_size)

**Test:**
```python
text = "A" * 1000
chunks = simple_chunk(text, chunk_size=500, overlap=50)
assert len(chunks) == 3, "Should create 3 chunks"
assert len(chunks[0]) == 500, "First chunk should be 500 chars"
print(f"✓ Created {len(chunks)} chunks")
```

### Task 3.2: Chunk All Documents

Apply chunking to all loaded documents.

**Requirements:**
- Create a list called `all_chunks`
- Each chunk should be a dict with keys:
  - `content`: Chunk text
  - `model`: Model name (from parent document)
  - `source`: Source filename
  - `chunk_id`: Unique ID (e.g., "Toyota_Camry_Specifications.pdf_0")
- Use chunk_size=500 and overlap=50

**Test:**
```python
assert len(all_chunks) > 50, "Should create many chunks"
assert all('content' in chunk for chunk in all_chunks), "All chunks should have content"
print(f"✓ Created {len(all_chunks)} chunks from {len(documents)} documents")
```

---

## Part 4: Embeddings and Storage (20 points)

### Task 4.1: Initialize Vertex AI Embeddings

Set up the Vertex AI embedding model.

**Requirements:**
- Import `VertexAIEmbeddings` from `langchain_google_vertexai`
- Initialize with model `text-embedding-004`
- Test by embedding a sample query

**Test:**
```python
query = "What's the Camry's horsepower?"
embedding = embeddings.embed_query(query)
assert len(embedding) == 768, "Should return 768-dimensional vector"
print(f"✓ Embedding model working, dimensions: {len(embedding)}")
```

### Task 4.2: Create ChromaDB Collection

Set up a ChromaDB collection to store chunks.

**Requirements:**
- Initialize ChromaDB client
- Create collection named "toyota_specs_week1"
- Add metadata: description

**Code:**
```python
import chromadb

client = chromadb.Client()
collection = client.create_collection(
    name="toyota_specs_week1",
    metadata={"description": "Toyota specifications - Week 1 assignment"}
)
```

### Task 4.3: Store Chunks in ChromaDB

Add all chunks to the collection.

**Requirements:**
- Prepare three lists: documents, metadatas, ids
- Use `collection.add()` to store chunks
- ChromaDB will automatically create embeddings

**Test:**
```python
# After adding chunks
count = collection.count()
assert count == len(all_chunks), "All chunks should be stored"
print(f"✓ Stored {count} chunks in ChromaDB")
```

---

## Part 5: Query and Retrieval (20 points)

### Task 5.1: Implement Retrieval Function

Complete the `retrieve_chunks()` function.

**Function signature:**
```python
def retrieve_chunks(query: str, collection, n_results: int = 3) -> dict:
    """
    Retrieve top-k most relevant chunks for a query.
    
    Args:
        query: User's question
        collection: ChromaDB collection
        n_results: Number of chunks to retrieve
        
    Returns:
        dict: Results with 'documents' and 'metadatas' keys
    """
    # TODO: Your implementation here
    pass
```

**Requirements:**
- Use `collection.query()` to find relevant chunks
- Return top `n_results` chunks
- Include both documents and metadata

**Test:**
```python
query = "What is the Camry's horsepower?"
results = retrieve_chunks(query, collection, n_results=3)
assert len(results['documents'][0]) == 3, "Should retrieve 3 chunks"
print(f"✓ Retrieved {len(results['documents'][0])} chunks")
```

### Task 5.2: Test Retrieval Quality

Test retrieval with 3 queries from `test_queries.json`.

**Requirements:**
- Load test queries from `test_queries.json`
- For each query, retrieve top 3 chunks
- Display query, retrieved chunks, and source models
- Manually verify that retrieved chunks are relevant

**Deliverable:** Output showing 3 queries with their retrieved chunks

---

## Part 6: Answer Generation (15 points)

### Task 6.1: Initialize Gemini Pro

Set up the Vertex AI LLM for generation.

**Requirements:**
- Import `VertexAI` from `langchain_google_vertexai`
- Initialize with model `gemini-pro`
- Set temperature=0 for factual responses

**Code:**
```python
from langchain_google_vertexai import VertexAI

llm = VertexAI(
    model_name="gemini-pro",
    temperature=0
)
```

### Task 6.2: Implement RAG Function

Complete the `ask_toyota_question()` function.

**Function signature:**
```python
def ask_toyota_question(question: str, collection, llm) -> tuple:
    """
    Answer a question about Toyota vehicles using RAG.
    
    Args:
        question: User's question
        collection: ChromaDB collection with Toyota specs
        llm: Language model for generation
        
    Returns:
        tuple: (answer, sources)
    """
    # TODO: Your implementation here
    pass
```

**Requirements:**
- Retrieve top 3 relevant chunks
- Build a prompt with context and question
- Use this prompt template:
  ```
  You are a helpful Toyota sales assistant. Answer based on the provided information.
  
  Context:
  {context}
  
  Question: {question}
  
  Answer:
  ```
- Generate answer using `llm.invoke()`
- Return answer and source metadata

**Test:**
```python
question = "What's the Camry's horsepower?"
answer, sources = ask_toyota_question(question, collection, llm)
assert len(answer) > 20, "Should generate substantial answer"
assert "203" in answer or "301" in answer, "Should mention horsepower values"
print(f"✓ Generated answer: {answer[:100]}...")
```

### Task 6.3: Test with All Query Types

Test your RAG system with all 10 queries from `test_queries.json`.

**Requirements:**
- Load all test queries
- For each query:
  - Generate answer using your RAG function
  - Display: Query, Answer, Sources
  - Manually verify accuracy
- Count how many answers are correct

**Deliverable:** 
- Output for all 10 queries
- Written analysis: "X out of 10 answers were accurate because..."

---

## Part 7: Analysis and Reflection (5 points)

Answer the following questions in markdown cells:

### Question 1: Chunking Strategy
*"What are the advantages and disadvantages of our simple 500-character chunking approach? When might it fail?"*

**Your answer:** (3-4 sentences)

### Question 2: Retrieval Quality
*"Looking at your test results, which query types (specification, feature, general) worked best? Why do you think that is?"*

**Your answer:** (3-4 sentences)

### Question 3: Improvements
*"If you could improve one part of this RAG system, what would it be and why?"*

**Your answer:** (2-3 sentences)

---

## Grading Rubric

### Correctness (60 points total)

| Component | Points | Criteria |
|-----------|--------|----------|
| Data Exploration | 15 | All files listed, text extracted, structure analyzed |
| PDF Loading | 10 | `load_pdf()` works, all 8 PDFs loaded correctly |
| Chunking | 15 | `simple_chunk()` works, all documents chunked |
| Embeddings & Storage | 20 | Embeddings created, chunks stored in ChromaDB |
| Retrieval | 20 | `retrieve_chunks()` works, relevant chunks retrieved |
| Answer Generation | 15 | `ask_toyota_question()` works, answers are accurate |
| Analysis | 5 | Thoughtful answers to reflection questions |

### Code Quality (20 points total)

| Aspect | Points | Criteria |
|--------|--------|----------|
| Functionality | 8 | All functions work without errors |
| Documentation | 6 | Docstrings and comments present |
| Code Style | 4 | Clean, readable code with proper variable names |
| Error Handling | 2 | Basic error handling implemented |

### Analysis Quality (20 points total)

| Aspect | Points | Criteria |
|--------|--------|----------|
| Depth of Reflection | 10 | Thoughtful analysis of strengths/weaknesses |
| Understanding | 6 | Demonstrates understanding of RAG concepts |
| Clarity | 4 | Clear, well-written responses |

**Total: 100 points**

---

## Submission Instructions

### What to Submit

1. **Completed Jupyter Notebook**
   - File: `02_assignment_starter.ipynb` (with your solutions)
   - All cells executed with outputs visible
   - All TODO sections completed
   - Reflection questions answered

2. **Exported HTML** (for easier grading)
   - In Jupyter: File → Save and Export Notebook As → HTML
   - File: `week01_assignment_[your_name].html`

### How to Submit

1. **Test everything works:**
   ```bash
   # Restart kernel and run all cells
   jupyter notebook 02_assignment_starter.ipynb
   # Kernel → Restart & Run All
   ```

2. **Verify outputs:**
   - All cells have output
   - No error messages
   - All test assertions pass

3. **Submit via [platform]:**
   - Upload notebook (.ipynb file)
   - Upload HTML export (.html file)

### Deadline

**Due:** [Date] at 11:59 PM

**Late Policy:**
- 0-24 hours late: -10%
- 24-48 hours late: -20%
- >48 hours late: Not accepted

---

## Tips for Success

### Start Early
- Don't wait until the last day
- Test each function before moving to the next
- Ask questions early if stuck

### Use Resources
- Review `01_lecture_demo.ipynb` for reference
- Check `lecture_notes.md` for concept explanations
- Use `../shared_resources/utils.py` helper functions
- Ask in discussion forum

### Test Incrementally
```python
# After each function, test it!
print("Testing load_pdf...")
text = load_pdf("../data/car-specs/toyota-specs/Toyota_Camry_Specifications.pdf")
assert len(text) > 0
print("✓ Works!")
```

### Common Pitfalls

❌ **Don't:**
- Copy-paste code without understanding it
- Skip the test cells
- Ignore error messages
- Rush through reflection questions

✅ **Do:**
- Read instructions carefully
- Test each part independently
- Document your code with comments
- Think critically about the system's strengths/weaknesses

---

## Getting Help

### During Development

1. **Review lecture materials:**
   - `01_lecture_demo.ipynb`
   - `lecture_notes.md`

2. **Check documentation:**
   - [LangChain Docs](https://python.langchain.com/)
   - [ChromaDB Docs](https://docs.trychroma.com/)
   - [PyPDF Docs](https://pypdf.readthedocs.io/)

3. **Ask questions:**
   - Discussion forum (preferred)
   - Office hours: [TBD]
   - Email instructor: [TBD]

### When Asking Questions

Include:
- What you're trying to do
- What you expected
- What actually happened
- Error messages (full traceback)
- Code snippet causing the issue

**Good question:**
> "I'm trying to load a PDF but getting FileNotFoundError. I'm using path '../data/toyota-specs/Toyota_Camry.pdf'. The file exists when I check with ls. Here's the error: [error message]"

**Bad question:**
> "My code doesn't work, help!"

---

## Bonus Challenges (Optional, No Extra Credit)

Want to go further? Try these:

### Challenge 1: Improve Chunking
Implement sentence-aware chunking that doesn't split mid-sentence.

### Challenge 2: Add Metadata Filtering
Filter retrieval by specific model (e.g., only search Camry docs).

### Challenge 3: Experiment with Parameters
Test different chunk sizes (200, 500, 1000) and retrieval counts (1, 3, 5, 10). Which works best?

### Challenge 4: Build a Simple UI
Create a simple command-line interface that loops and answers questions.

### Challenge 5: Add Conversation Memory
Store previous Q&A pairs and use them as context for follow-up questions.

---

**Good luck! You've got this! 🚗🚀**

If you get stuck, remember: every expert was once a beginner. Keep experimenting, keep learning!


