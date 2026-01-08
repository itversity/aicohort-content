# Week 1 Quiz: RAG Foundations & Dataset Exploration

**Instructions:**
- 10 multiple-choice questions
- Select the best answer for each question
- You may attempt the quiz multiple times before the deadline
- Passing score: 16/20 (80%)

**Total Points:** 20 (2 points per question)

---

## Question 1: RAG Architecture

What does RAG stand for?

**A)** Rapid Automated Generation  
**B)** Retrieval-Augmented Generation  
**C)** Random Access Gateway  
**D)** Recursive Agent Generation  

**Correct Answer:** B

**Explanation:** RAG stands for Retrieval-Augmented Generation, a technique that combines information retrieval from a knowledge base with text generation from an LLM.

---

## Question 2: RAG Components

Which of the following is NOT a core component of a RAG system?

**A)** Vector database for storing embeddings  
**B)** Text chunking strategy  
**C)** Fine-tuning the base LLM  
**D)** Embedding model for semantic search  

**Correct Answer:** C

**Explanation:** RAG systems do not require fine-tuning the LLM. They use retrieval and augmentation to provide context, making them more flexible and cost-effective than fine-tuning approaches.

---

## Question 3: When to Use RAG

In which scenario would RAG be MOST appropriate?

**A)** You need to change the writing style of an LLM  
**B)** You have private company documents that need to be queried  
**C)** You want to make the LLM respond faster  
**D)** You need to reduce the size of the model  

**Correct Answer:** B

**Explanation:** RAG is ideal for querying private or proprietary documents that weren't in the LLM's training data. It allows you to provide up-to-date, domain-specific information without fine-tuning.

---

## Question 4: Toyota Dataset Characteristics

Based on the Toyota specification documents, which section appears in ALL vehicle spec PDFs?

**A)** Competitor Comparison  
**B)** Engine Options  
**C)** Towing Capacity  
**D)** Off-road Features  

**Correct Answer:** B

**Explanation:** All Toyota specification documents include an "Engine Options" section describing powertrain variants, horsepower, transmission, and fuel economy. Not all models have towing capacity or off-road features.

---

## Question 5: Chunking Strategy

What is the PRIMARY reason for chunking documents in a RAG system?

**A)** To reduce storage costs in the database  
**B)** To make embeddings work better on focused text segments  
**C)** To increase the speed of PDF loading  
**D)** To comply with copyright restrictions  

**Correct Answer:** B

**Explanation:** Chunking breaks documents into smaller, focused segments that embeddings can better represent semantically. This improves retrieval relevance compared to embedding entire documents.

---

## Question 6: Simple Chunking Limitation

What is a major limitation of the simple fixed-size chunking approach used in Week 1?

**A)** It's too slow for large documents  
**B)** It requires too much memory  
**C)** It may split important information mid-sentence or mid-section  
**D)** It only works with PDF files  

**Correct Answer:** C

**Explanation:** Fixed-size chunking doesn't respect semantic boundaries, so it might split a sentence about engine specifications across two chunks, reducing retrieval quality. Week 2 introduces section-based chunking to address this.

---

## Question 7: Vector Embeddings

What do vector embeddings capture about text?

**A)** The exact words and their frequency  
**B)** The semantic meaning and context  
**C)** The length and formatting  
**D)** The author and publication date  

**Correct Answer:** B

**Explanation:** Embeddings are numerical vectors that capture the semantic meaning of text. Similar meanings produce similar vectors, enabling semantic search that goes beyond keyword matching.

---

## Question 8: Retrieval Mechanism

How does a vector database find relevant chunks for a query?

**A)** Keyword matching like traditional search engines  
**B)** Calculating cosine similarity between query and chunk embeddings  
**C)** Randomly sampling from stored documents  
**D)** Alphabetically sorting by document title  

**Correct Answer:** B

**Explanation:** Vector databases use cosine similarity (or other distance metrics) to compare the query embedding with stored chunk embeddings, returning the most similar chunks.

---

## Question 9: LLM Temperature Setting

Why do we set temperature=0 for the Gemini Pro model in our RAG system?

**A)** To make responses generate faster  
**B)** To reduce API costs  
**C)** To get deterministic, factual responses  
**D)** To allow more creative answers  

**Correct Answer:** C

**Explanation:** Temperature=0 makes the LLM deterministic and focused on the most likely (factual) responses. For specifications and facts, we want consistency over creativity. Higher temperatures introduce randomness.

---

## Question 10: RAG Evaluation

Which query type would likely work BEST with our Week 1 simple RAG system?

**A)** "What is the horsepower of the Toyota Camry?" (specification lookup)  
**B)** "Compare fuel economy across all hybrid models" (multi-model comparison)  
**C)** "What car should I buy for my family?" (open-ended recommendation)  
**D)** "Tell me more about that safety feature you just mentioned" (follow-up)  

**Correct Answer:** A

**Explanation:** Simple specification lookups work best with our basic RAG system because they typically require information from a single document section. Multi-model comparisons, recommendations, and follow-up questions require more advanced capabilities (metadata filtering, conversation memory) that we'll add in later weeks.

---

## Answer Key

| Question | Correct Answer | Points |
|----------|----------------|--------|
| 1 | B | 2 |
| 2 | C | 2 |
| 3 | B | 2 |
| 4 | B | 2 |
| 5 | B | 2 |
| 6 | C | 2 |
| 7 | B | 2 |
| 8 | B | 2 |
| 9 | C | 2 |
| 10 | A | 2 |

**Total:** 20 points

---

## Scoring Guide

- **18-20 points (90-100%):** Excellent understanding
- **16-17 points (80-89%):** Good understanding (passing)
- **14-15 points (70-79%):** Adequate understanding (review key concepts)
- **Below 14 (< 70%):** Review lecture notes and try again

---

## Study Resources

If you need to review:

1. **RAG Concepts (Q1-3):** Review lecture_notes.md Part 1
2. **Dataset (Q4):** Review lecture_notes.md Part 2 and README.md
3. **Chunking (Q5-6):** Review lecture_notes.md Part 3, Step 3
4. **Embeddings (Q7-8):** Review lecture_notes.md Part 3, Steps 4-5
5. **LLM Configuration (Q9):** Review lecture_notes.md Part 3, Step 7
6. **System Evaluation (Q10):** Review assignment.md and test your system

---

**Good luck!** 🚀

