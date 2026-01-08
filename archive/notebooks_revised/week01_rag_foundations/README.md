# Week 1: RAG Foundations & Dataset Exploration

Welcome to Week 1 of the RAG Bootcamp! This week you'll learn the fundamentals of Retrieval-Augmented Generation (RAG) and build your first Q&A system using Toyota specification documents.

## Learning Objectives

By the end of this week, you will be able to:

1. **Understand RAG Architecture**
   - Explain what RAG is and why it's needed
   - Identify the three core components: Retrieval, Augmentation, Generation
   - Compare RAG with fine-tuning and prompt engineering

2. **Analyze the Toyota Dataset**
   - Inspect PDF file sizes, structure, and content
   - Identify common sections across specification documents
   - Understand typical car buyer query patterns

3. **Build a Working RAG System**
   - Load and extract text from PDF documents
   - Implement simple chunking strategy
   - Create embeddings with Vertex AI
   - Store chunks in ChromaDB vector database
   - Retrieve relevant context for queries
   - Generate answers using Gemini Pro

4. **Test and Validate**
   - Query your RAG system with car buyer questions
   - Evaluate response quality and accuracy
   - Identify limitations of simple chunking

## What You'll Build

A basic Toyota Specification Q&A system that can answer questions like:
- "What is the Toyota Camry's horsepower?"
- "What safety features does the RAV4 have?"
- "Tell me about Toyota's reliability"

## Files in This Week

### Notebooks
- **`01_lecture_demo.ipynb`** - Complete working example from live session
- **`02_assignment_starter.ipynb`** - Your assignment template with TODOs
- **`03_assignment_solution.ipynb`** - Reference solution (available after deadline)

### Documentation
- **`README.md`** (this file) - Week overview
- **`lecture_notes.md`** - Detailed notes from live session
- **`assignment.md`** - Assignment instructions and requirements
- **`quiz.md`** - 10 questions to test your understanding
- **`test_queries.json`** - Test queries for validation

## Prerequisites

### Knowledge
- None! This is Week 1, we start from the basics.
- Helpful: Basic Python (functions, loops, file I/O)
- Helpful: Understanding of what an LLM is

### Technical Setup
- Python 3.10+ with `.venv` activated
- All dependencies installed (`pip install -r requirements.txt`)
- GCP account with Vertex AI enabled
- LangSmith account for monitoring
- Environment variables configured (`.env` file)

**Haven't set up yet?** Follow `../SETUP_GUIDE.md`

## Time Commitment

| Activity | Time |
|----------|------|
| Pre-work: Read lecture notes | 30 min |
| Live session | 2 hours |
| Assignment | 3-4 hours |
| Quiz | 15 min |
| **Total** | **6-7 hours** |

## Getting Started

### 1. Pre-Work (Before Live Session)

Read the lecture notes to familiarize yourself with concepts:
```bash
cat lecture_notes.md
```

Key topics to understand:
- What is RAG and when to use it
- Vector embeddings and semantic search
- The Toyota dataset structure

### 2. Live Session (2 hours)

**Format:** Instructor-led live coding session

**Schedule:**
- **0:00-0:30** - RAG Introduction & Concepts
- **0:30-1:15** - Toyota Dataset Analysis & Exploration
- **1:15-2:00** - Build First RAG System Live

**What to do:**
- Follow along with `01_lecture_demo.ipynb`
- Ask questions in real-time
- Take notes on key concepts
- Run cells in your own notebook

### 3. Assignment (3-4 hours)

**Goal:** Build your own Toyota Q&A system from scratch

**Steps:**
1. Open `02_assignment_starter.ipynb`
2. Read through all instructions
3. Complete all TODO sections
4. Test with the provided queries
5. Answer reflection questions
6. Submit completed notebook

**Tips:**
- Start early - don't wait until deadline
- Use `01_lecture_demo.ipynb` as reference
- Test each function before moving to next
- Use `../shared_resources/utils.py` for helper functions

### 4. Quiz (15 minutes)

**Format:** 10 multiple-choice questions (auto-graded)

**Topics Covered:**
- RAG architecture and components
- When to use RAG vs alternatives
- Vector embeddings and similarity
- Toyota dataset characteristics

**Tips:**
- Review `lecture_notes.md` before taking quiz
- Unlimited attempts before deadline
- Focus on understanding, not memorization

## Dataset: Toyota Specifications

This week we're working with **8 Toyota specification PDFs**:

| File | Size | Description |
|------|------|-------------|
| `Introduction_to_Toyota_Car_Sales.pdf` | 49 KB | Toyota brand overview |
| `Toyota_Camry_Specifications.pdf` | 74 KB | Midsize sedan |
| `Toyota_Corolla_Specifications.pdf` | 73 KB | Compact sedan |
| `Toyota_Highlander_Specifications.pdf` | 75 KB | Midsize SUV |
| `Toyota_Prius_Specifications.pdf` | 75 KB | Hybrid sedan |
| `Toyota_RAV4_Specifications.pdf` | 76 KB | Compact SUV |
| `Toyota_Tacoma_Specifications.pdf` | 74 KB | Midsize truck |
| `Toyota_bZ4X_Specifications.pdf` | 84 KB | Electric SUV |

**Location:** `../data/car-specs/toyota-specs/`

### Common Document Structure

All specification documents follow this pattern:
1. **Overview** - Vehicle description and target audience
2. **Engine Options** - Powertrain specifications (HP, MPG, transmission)
3. **Design** - Exterior and interior design features
4. **Comfort & Technology** - Infotainment, connectivity, features
5. **Competitor Comparison** - How it stacks against rivals
6. **Sales Strategies** - Key selling points

## Key Concepts

### What is RAG?

**RAG (Retrieval-Augmented Generation)** combines information retrieval with LLM generation:

1. **Retrieval:** Find relevant documents/chunks from a knowledge base
2. **Augmentation:** Add retrieved content to the prompt context
3. **Generation:** LLM generates answer grounded in the retrieved information

**Why RAG?**
- ✅ Access to up-to-date information (not in training data)
- ✅ Factually grounded responses with citations
- ✅ Works with private/proprietary data
- ✅ More cost-effective than fine-tuning
- ✅ Transparent - can see what documents were used

### Simple Chunking (Week 1 Approach)

This week we use **fixed-size chunking**: split documents into chunks of N characters.

```python
def simple_chunk(text, chunk_size=500):
    chunks = []
    for i in range(0, len(text), chunk_size):
        chunks.append(text[i:i+chunk_size])
    return chunks
```

**Pros:**
- Simple to implement
- Consistent chunk sizes
- Works as baseline

**Cons:**
- May split sentences mid-way
- Ignores semantic boundaries
- Not optimized for our structured documents

**Coming in Week 2:** Section-based chunking that respects document structure!

### Vector Embeddings

Embeddings convert text to numerical vectors that capture semantic meaning:

```
"What is the Camry's horsepower?" → [0.23, -0.45, 0.67, ..., 0.12] (1536 dims)
"203 HP 2.5L engine" → [0.25, -0.42, 0.69, ..., 0.15] (1536 dims)
                                    ↑ Similar vectors = similar meaning
```

**This week we use:** Vertex AI `text-embedding-004` (768 dimensions)

## Deliverables

### Assignment Submission
- [ ] Completed `02_assignment_starter.ipynb` with all cells executed
- [ ] All TODO sections implemented
- [ ] Test queries answered correctly
- [ ] Reflection questions answered
- [ ] Notebook exported as HTML (for grading)

### Quiz Completion
- [ ] Take quiz online
- [ ] Score 80% or higher (unlimited attempts)

## Grading

### Assignment (60 points)
- **Correctness (36 pts):** All functions work correctly
  - PDF loading (6 pts)
  - Chunking implementation (6 pts)
  - Embedding and storage (12 pts)
  - Query and retrieval (6 pts)
  - Answer generation (6 pts)
- **Code Quality (12 pts):** Clean, documented code with docstrings
- **Analysis (12 pts):** Thoughtful answers to reflection questions

### Quiz (20 points)
- 10 questions × 2 points each
- Must score 16/20 or higher to pass

**Total:** 80 points (60 + 20)

## Common Issues & Tips

### Issue: "ModuleNotFoundError"
**Solution:** Activate `.venv` and install requirements:
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### Issue: "GCP Authentication Error"
**Solution:** Run:
```bash
gcloud auth application-default login
```

### Issue: "PDF not found"
**Solution:** Check relative path. From week01 notebooks, use:
```python
"../data/car-specs/toyota-specs/Toyota_Camry_Specifications.pdf"
```

### Tip: Use Shared Utilities
Don't rewrite common functions! Use what's provided:
```python
from sys import path
path.append('../shared_resources')
from utils import load_pdf, get_file_info, analyze_text
```

### Tip: Test Incrementally
Don't write all code at once. Test each function:
```python
# Test PDF loading
text = load_pdf("../data/car-specs/toyota-specs/Toyota_Camry_Specifications.pdf")
print(f"Loaded {len(text)} characters")  # Should be > 2000

# Test chunking
chunks = simple_chunk(text, 500)
print(f"Created {len(chunks)} chunks")  # Should be > 5
```

## Additional Resources

### Documentation
- [LangChain Docs](https://python.langchain.com/)
- [Vertex AI Embeddings](https://cloud.google.com/vertex-ai/docs/generative-ai/embeddings/get-text-embeddings)
- [ChromaDB Docs](https://docs.trychroma.com/)
- [PyPDF Documentation](https://pypdf.readthedocs.io/)

### Readings
- [RAG Paper (Lewis et al.)](https://arxiv.org/abs/2005.11401) - Original RAG research
- [LangChain RAG Tutorial](https://python.langchain.com/docs/use_cases/question_answering/)

### Videos
- [What is RAG?](https://www.youtube.com/watch?v=T-D1OfcDW1M) - 10 min overview
- [Vector Databases Explained](https://www.youtube.com/watch?v=klTvEwg3oJ4) - 15 min

## Getting Help

**During the Week:**
- Post questions in discussion forum
- Attend office hours: [TBD]
- Review `../shared_resources/troubleshooting_guide.md`

**Stuck on Assignment:**
- Re-watch live session recording
- Review `01_lecture_demo.ipynb` for reference
- Check `lecture_notes.md` for concept explanations
- Ask specific questions in forum (include error messages!)

## Next Week Preview

**Week 2: Smart Chunking Strategies**

In Week 2, we'll improve our RAG system with intelligent chunking:
- Section-based chunking (respects document structure)
- Metadata extraction (model, section, topics)
- Optimized for car buyer queries
- Better retrieval accuracy

This week's simple chunking works, but you'll see limitations. Week 2 solves them!

---

**Ready to start?** Open `01_lecture_demo.ipynb` after the live session, then begin your assignment with `02_assignment_starter.ipynb`.

Good luck! 🚀

