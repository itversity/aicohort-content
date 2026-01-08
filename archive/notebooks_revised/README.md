# 10-Week RAG Bootcamp: Toyota Car Sales Assistant
## From PDFs to Production Full-Stack Application

Welcome to the comprehensive RAG (Retrieval-Augmented Generation) bootcamp! This hands-on program will take you from RAG fundamentals to deploying a production-ready full-stack application.

## Program Overview

**Duration:** 10 weeks (2 hours live session per week + assignments)
**Project:** Build a Toyota Car Sales Assistant that answers customer questions using real Toyota specification documents
**Outcome:** Portfolio-ready full-stack RAG application deployed to Google Cloud Platform

## What You'll Learn

### Core Skills
- RAG architecture and implementation patterns
- Document processing and intelligent chunking strategies
- Vector embeddings and semantic search
- Advanced retrieval techniques (multi-query, re-ranking, hybrid search)
- LLM integration and prompt engineering
- Conversational AI with memory management
- Agentic workflows with LangGraph
- Production monitoring and evaluation
- Full-stack development (FastAPI + React)
- GCP deployment and scaling

### Tech Stack

**Backend & AI:**
- **LangChain** - RAG orchestration framework
- **LangGraph** - Agent workflow management
- **LangSmith** - Monitoring and evaluation
- **GCP Vertex AI** - Gemini Pro (LLM) and text-embedding-004 (embeddings)
- **ChromaDB** - Vector database (development)
- **Pinecone** - Vector database (production)
- **FastAPI** - Production REST API

**Frontend:**
- **React + TypeScript** - Modern UI framework
- **TailwindCSS** - Styling
- **Cursor AI** - AI-assisted development

**Deployment:**
- **GCP Cloud Run** - Serverless container platform
- **GCP Cloud Storage + CDN** - Frontend hosting
- **Docker** - Containerization

## Course Structure

### Week 1: RAG Foundations & Dataset Exploration
- Understand RAG architecture and use cases
- Analyze Toyota specification documents
- Build first Q&A system with simple chunking
- **Deliverable:** Working prototype answering Toyota spec questions

### Week 2: Smart Chunking Strategies
- Section-based chunking for structured documents
- Metadata extraction and enrichment
- Optimize for car buyer query patterns
- **Deliverable:** Production-ready chunking pipeline

### Week 3: Embeddings & Vector Search
- Compare embedding models (Vertex AI vs alternatives)
- Vector database setup and optimization
- Hybrid search implementation
- **Deliverable:** Optimized retrieval system

### Week 4: Complete RAG Pipeline
- Vertex AI Gemini Pro integration
- Prompt engineering for factual responses
- Citation and source attribution
- **Deliverable:** End-to-end RAG pipeline

### Week 5: Advanced Retrieval Techniques
- Multi-query retrieval for complex questions
- Self-query with metadata filtering
- Re-ranking with Vertex AI Ranking API
- **Deliverable:** Enhanced retrieval for comparisons

### Week 6: Evaluation & Monitoring
- RAG evaluation metrics (RAGAS framework)
- LangSmith tracing and debugging
- Creating evaluation datasets
- **Deliverable:** Evaluated and monitored RAG system

### Week 7: Conversational RAG
- Chat history and memory management
- Multi-turn conversation handling
- Context window optimization
- **Deliverable:** Conversational Toyota assistant

### Week 8: Intelligent Agents with LangGraph
- Agent architecture for RAG
- Tool-based routing (specs, comparison, recommendations)
- Self-correcting workflows
- **Deliverable:** Multi-tool agent system

### Week 9: Production Backend with FastAPI
- REST API design for RAG applications
- Async processing and streaming responses
- Authentication, logging, and caching
- **Deliverable:** Production-ready API

### Week 10: Frontend & Deployment
- React chat interface (built with Cursor AI)
- WebSocket streaming integration
- GCP deployment (Cloud Run + Cloud Storage)
- **Deliverable:** Live, publicly accessible application

### Capstone Project
- Complete production Toyota Sales Assistant
- Full evaluation report with metrics
- Deployed to GCP with monitoring
- Demo video and documentation

## Prerequisites

### Required Knowledge
- **Python** - Comfortable with functions, classes, file I/O
- **Basic ML concepts** - Understanding of embeddings, vectors
- **Command line** - Navigate directories, run scripts
- **Git basics** - Clone repos, commit changes

### Nice to Have (Not Required)
- JavaScript/React experience
- REST API development
- Cloud platform experience
- Docker/containers knowledge

### Technical Requirements
- **Python 3.10+** installed
- **GCP Account** (free tier sufficient for most of course)
- **LangSmith Account** (free tier available)
- **Git** installed
- **Code editor** - VS Code or Cursor recommended
- **16GB RAM recommended** (8GB minimum)

## Repository Structure

```
notebooks_revised/
├── README.md (this file)
├── SETUP_GUIDE.md (detailed setup instructions)
├── requirements.txt (all dependencies)
├── .env.example (environment variable template)
│
├── data/
│   └── car-specs/toyota-specs/ (8 Toyota specification PDFs)
│
├── shared_resources/
│   ├── utils.py (helper functions)
│   └── toyota_buyer_queries.json (test queries)
│
├── week01_rag_foundations/
├── week02_chunking_strategy/
├── week03_embeddings_vector_search/
├── week04_complete_rag_pipeline/
├── week05_advanced_retrieval/
├── week06_evaluation_monitoring/
├── week07_conversational_rag/
├── week08_langgraph_agents/
├── week09_fastapi_backend/
├── week10_frontend_deployment/
│
├── capstone_project/
└── reference_implementations/
```

## Getting Started

### 1. Setup Your Environment

Follow the comprehensive setup guide:
```bash
cd notebooks_revised
cat SETUP_GUIDE.md
```

This covers:
- Python virtual environment setup
- Installing dependencies
- GCP configuration
- API keys and credentials

### 2. Start with Week 1

Navigate to Week 1 and begin:
```bash
cd week01_rag_foundations
```

Read the `README.md` in each week's folder for:
- Learning objectives
- Files description
- Time commitment
- Prerequisites

### 3. Weekly Workflow

**Before Live Session:**
- Review `lecture_notes.md`
- Set up environment for that week

**During Live Session:**
- Follow along with `01_lecture_demo.ipynb`
- Ask questions in real-time

**After Live Session:**
- Complete `02_assignment_starter.ipynb`
- Take the quiz
- Submit your work

## Learning Resources

### Documentation
- [LangChain Docs](https://python.langchain.com/)
- [Vertex AI Docs](https://cloud.google.com/vertex-ai/docs)
- [LangSmith Docs](https://docs.smith.langchain.com/)
- [LangGraph Docs](https://langchain-ai.github.io/langgraph/)

### Community
- Course discussion forum: [TBD]
- Office hours: [TBD]
- Study groups: [TBD]

## Assessment & Grading

### Weekly Assignments (60%)
- 10 assignments @ 6 points each
- Graded on correctness, code quality, and analysis

### Weekly Quizzes (20%)
- 10 quizzes @ 2 points each
- Auto-graded multiple choice
- Unlimited attempts before deadline

### Capstone Project (20%)
- Complete production application
- Evaluation report
- Demo video
- Technical documentation

**Grading Scale:**
- 90-100: Excellent
- 80-89: Good
- 70-79: Satisfactory
- Below 70: Needs improvement

## Time Commitment

**Per Week:**
- Pre-work reading: 30 minutes
- Live session: 2 hours
- Assignment: 3-4 hours
- Quiz: 15 minutes
- **Total: 6-7 hours per week**

**Capstone (Weeks 11-12):**
- 15-20 hours over 2 weeks

## What You'll Build

By the end of this bootcamp, you will have built a **production-ready Toyota Car Sales Assistant** that:

✅ Answers customer questions about Toyota vehicles accurately
✅ Compares multiple models intelligently
✅ Maintains conversation context across multiple turns
✅ Provides source citations for transparency
✅ Handles 20+ simultaneous users
✅ Responds in under 3 seconds
✅ Costs less than $0.10 per query
✅ Includes beautiful, responsive web interface
✅ Deployed and accessible via public URL
✅ Monitored with LangSmith for quality

## Real-World Applications

The skills you learn building the Toyota assistant directly transfer to:
- **Customer Support** - Answer product questions using documentation
- **Legal/Compliance** - Query regulations and policies
- **Healthcare** - Clinical decision support from medical literature
- **Education** - Personalized tutoring from course materials
- **Enterprise Search** - Find information across company knowledge base
- **Research** - Query academic papers and reports

## Support

**Questions?**
- Check `troubleshooting_guide.md` in `shared_resources/`
- Post in discussion forum
- Attend office hours
- Email: [instructor email]

## License & Usage

This course content is provided for educational purposes. The Toyota specification documents are used for demonstration and learning purposes only.

---

**Ready to begin?** Head to `SETUP_GUIDE.md` to set up your environment, then start with Week 1!

🚀 Let's build something amazing!

