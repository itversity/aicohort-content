# Toyota Specifications RAG - Chunking Strategy Analysis

## Document Characteristics

### File Inventory
| File | Pages | Size (KB) | Characters | Words | Structure |
|------|-------|-----------|------------|-------|-----------|
| Introduction_to_Toyota_Car_Sales.pdf | 2 | 48.6 | 1,871 | 246 | Overview document |
| Toyota_Camry_Specifications.pdf | 1 | 74.3 | 3,073 | 434 | Single model specs |
| Toyota_Corolla_Specifications.pdf | 1 | 73.4 | 2,685 | 379 | Single model specs |
| Toyota_Highlander_Specifications.pdf | 1 | 74.9 | 2,877 | 404 | Single model specs |
| Toyota_Prius_Specifications.pdf | 1 | 74.9 | 3,310 | 476 | Single model specs |
| Toyota_RAV4_Specifications.pdf | 1 | 75.9 | 3,174 | 456 | Single model specs |
| Toyota_Tacoma_Specifications.pdf | 1 | 73.6 | 2,668 | 379 | Single model specs |
| Toyota_bZ4X_Specifications.pdf | 4 | 83.9 | 3,090 | 411 | Single model specs (extended) |

### Content Structure Pattern
All specification documents follow a consistent structure:
1. **Overview** - Vehicle description, target audience
2. **Engine Options** - Multiple powertrain variants with specs
3. **Performance Metrics** - MPG, horsepower, transmission details
4. **Safety Features** - Toyota Safety Sense, collision prevention, etc.
5. **Technology & Comfort** - Infotainment, connectivity, interior features
6. **Dimensions & Capacity** - Seating, cargo space, towing capacity
7. **Warranty** - Coverage details
8. **Special Sections** - Competitor comparisons (bZ4X only)

## Typical Car Buyer Queries

### Query Categories
1. **Performance Questions**
   - "What's the fuel economy of the Camry hybrid?"
   - "How much horsepower does the Tacoma V6 have?"
   - "What's the 0-60 time for the RAV4 Prime?"

2. **Feature Questions**
   - "What safety features does the Highlander have?"
   - "Does the Prius Prime have wireless CarPlay?"
   - "What's included in Toyota Safety Sense?"

3. **Capacity Questions**
   - "How much can the Tacoma tow?"
   - "What's the cargo space in the RAV4?"
   - "How many people can the Highlander seat?"

4. **Comparison Questions**
   - "Compare Camry vs Corolla fuel economy"
   - "What's the difference between RAV4 and Highlander?"
   - "How does the bZ4X compare to Tesla Model Y?"

5. **Variant Questions**
   - "What engine options are available for the Camry?"
   - "Does the RAV4 come in hybrid?"
   - "What's the difference between Prius and Prius Prime?"

6. **Cost & Warranty Questions**
   - "What's the starting price of the bZ4X?"
   - "What warranty does Toyota offer?"
   - "What's covered under the powertrain warranty?"

## Recommended Chunking Strategies

### Strategy 1: **Section-Based Chunking** (RECOMMENDED)
**Approach:** Chunk by semantic sections within each vehicle specification

**Implementation:**
- **Chunk Size:** 300-500 tokens (~400-600 words)
- **Overlap:** 50-75 tokens (~10-15%)
- **Section Boundaries:** Respect natural document sections

**Chunk Structure:**
1. **Overview Chunk** (includes model name, overview, target audience)
2. **Engine Options Chunk(s)** (each engine variant could be a sub-chunk)
3. **Performance & Efficiency Chunk** (MPG, acceleration, transmission)
4. **Safety Features Chunk** (all safety systems grouped)
5. **Technology & Comfort Chunk** (infotainment, connectivity, interior)
6. **Dimensions & Capacity Chunk** (measurements, seating, cargo, towing)
7. **Warranty Chunk** (all warranty details)
8. **Special Chunks** (comparisons, sales strategies - if present)

**Metadata for Each Chunk:**
```python
{
    "model": "Toyota Camry",
    "section": "Engine Options",
    "variant": "2.5L Hybrid",  # if applicable
    "doc_type": "specification",
    "chunk_id": "camry_engine_001"
}
```

**Advantages:**
✅ Aligns with how users ask questions (by topic)
✅ Natural semantic boundaries prevent splitting related information
✅ Easy to retrieve complete context for specific questions
✅ Works well for comparison queries
✅ Maintains coherence within each chunk

**Disadvantages:**
⚠️ Some sections might be small (<200 tokens) or large (>600 tokens)
⚠️ Requires parsing to identify section boundaries

---

### Strategy 2: **Fixed-Size Chunking with Smart Overlap**
**Approach:** Fixed 512-token chunks with 128-token overlap

**Implementation:**
- **Chunk Size:** 512 tokens (~640 words)
- **Overlap:** 128 tokens (25%)
- **Boundary Handling:** Use sentence boundaries

**Advantages:**
✅ Simple to implement
✅ Consistent chunk sizes for embeddings
✅ Good overlap ensures context preservation

**Disadvantages:**
❌ May split semantic sections (e.g., splitting engine options mid-description)
❌ Less aligned with query patterns
❌ Harder to maintain coherence

---

### Strategy 3: **Hierarchical Chunking**
**Approach:** Two-level hierarchy with vehicle-level parent chunks and section-level child chunks

**Implementation:**
- **Parent Chunks:** Entire vehicle specification (2,600-3,300 chars)
- **Child Chunks:** Individual sections (200-600 tokens)
- **Retrieval:** Hybrid search (retrieve child chunks, provide parent context)

**Chunk Structure:**
```
Parent: Toyota Camry (full spec)
  ├─ Child: Overview
  ├─ Child: Engine Options
  ├─ Child: Performance
  ├─ Child: Safety Features
  ├─ Child: Technology & Comfort
  ├─ Child: Dimensions & Capacity
  └─ Child: Warranty
```

**Advantages:**
✅ Excellent for specific questions (child chunks)
✅ Provides full context when needed (parent chunks)
✅ Best for complex comparison queries
✅ Flexible retrieval strategies

**Disadvantages:**
⚠️ More complex implementation
⚠️ Requires careful indexing strategy
⚠️ May retrieve redundant information

---

### Strategy 4: **Entity-Based Chunking**
**Approach:** Chunk around specific entities (model, variant, feature)

**Implementation:**
- Each chunk focuses on a single entity (e.g., "Camry 2.5L Hybrid Engine")
- Cross-reference chunks for related entities
- Rich metadata for entity relationships

**Advantages:**
✅ Excellent for variant-specific questions
✅ Great for feature comparisons across models

**Disadvantages:**
❌ Complex to implement
❌ May create many small chunks
❌ Harder to maintain relationships

---

## Final Recommendation: **Strategy 1 (Section-Based Chunking)**

### Rationale
1. **Query Alignment:** Users ask questions by topic ("What safety features...", "What's the fuel economy...")
2. **Natural Boundaries:** Documents already have clear semantic sections
3. **Coherence:** Each chunk contains complete, related information
4. **Optimal Size:** Sections are naturally sized between 200-600 tokens
5. **Easy Comparison:** Section-based chunks make cross-model comparisons straightforward

### Implementation Details

#### Chunk Size Guidelines
- **Target:** 400 tokens (~500 words)
- **Minimum:** 150 tokens (for small sections like Warranty)
- **Maximum:** 700 tokens (for complex sections like Engine Options)
- **Overlap:** 50 tokens at section boundaries (include vehicle name + section title in overlap)

#### Metadata Schema
```python
chunk_metadata = {
    "model": "Toyota Camry",
    "section": "Engine Options",
    "subsection": "2.5L Hybrid",  # optional
    "topics": ["engine", "hybrid", "performance", "transmission"],
    "specs_mentioned": ["203 HP", "8-speed automatic", "52 MPG"],
    "doc_type": "specification",
    "source_file": "Toyota_Camry_Specifications.pdf",
    "chunk_sequence": 2  # order in document
}
```

#### Special Handling

**1. Engine Options Section**
- If multiple engine variants exist, create sub-chunks per variant
- Each sub-chunk includes: power output, transmission, key features, MPG
- Maintain parent context (model name) in each sub-chunk

**2. Introduction Document**
- Chunk by major sections (Brand Overview, Key Aspects, Customer Communication)
- These chunks provide general Toyota context for brand-related queries

**3. bZ4X Extended Document**
- Apply same section-based approach
- Competitor comparison section becomes its own chunk
- Sales strategies section becomes its own chunk

**4. Cross-References**
- Include model name in every chunk for filtering
- Add "related_models" metadata for comparison queries (e.g., Camry chunk mentions Corolla as similar segment)

#### Retrieval Strategy
1. **Embedding Model:** Use models optimized for semantic search (e.g., `text-embedding-3-large`)
2. **Top-K:** Retrieve top 3-5 chunks initially
3. **Re-ranking:** Apply relevance scoring based on:
   - Metadata match (model name, section type)
   - Semantic similarity score
   - Query type classification
4. **Context Window:** Provide 2-3 most relevant chunks to LLM (800-1500 tokens total)

#### Sample Chunking for Toyota Camry

**Chunk 1: Overview**
```
Toyota Camry: The Sophisticated Midsize Sedan

Overview:
The Toyota Camry is a premium midsize sedan renowned for its reliability, 
spacious interiors, and smooth performance. It caters to professionals, 
small families, and those seeking a balance of luxury and efficiency, 
with hybrid options available for eco-conscious buyers.

[~150 tokens]
```

**Chunk 2: Engine Options - 2.5L 4-Cylinder**
```
Toyota Camry - Engine Options

2.5L 4-Cylinder Gasoline Engine:
- Power Output: 203 HP
- Transmission: 8-speed automatic
- Key Feature: Efficient and refined performance for daily driving
- Fuel Economy: 28 city / 39 highway MPG

[~100 tokens + context]
```

**Chunk 3: Engine Options - 2.5L Hybrid**
```
Toyota Camry - Engine Options

2.5L Hybrid Engine:
- Combined Power Output: 208 HP
- Transmission: Electronic CVT
- Key Feature: Outstanding fuel efficiency with minimal emissions
- Fuel Economy: 51 city / 53 highway MPG

[~100 tokens + context]
```

**Chunk 4: Safety Features**
```
Toyota Camry - Safety Features

Toyota Safety Sense 2.5+:
- Pre-Collision System with Pedestrian Detection
- Lane Departure Alert with Steering Assist
- Adaptive Cruise Control
- Automatic High Beams
- Road Sign Assist

Additional Safety:
- 10 airbags
- Blind Spot Monitor with Rear Cross-Traffic Alert

[~150 tokens]
```

## Evaluation Metrics

To validate the chunking strategy, monitor:
1. **Retrieval Accuracy:** % of queries where relevant chunks are in top-3
2. **Answer Quality:** Human evaluation of response completeness
3. **Chunk Utilization:** Are all chunks being retrieved appropriately?
4. **Cross-Model Queries:** Success rate on comparison questions
5. **Response Time:** Latency from query to answer

## Next Steps

1. **Implement Section Parser:**
   - Use regex or NLP to identify section boundaries
   - Extract metadata (model name, section type, specs)

2. **Create Chunking Pipeline:**
   - PDF → Text Extraction → Section Identification → Chunk Creation → Metadata Addition

3. **Build Vector Store:**
   - Embed each chunk
   - Store with metadata in ChromaDB/Pinecone/Weaviate

4. **Develop Retrieval Logic:**
   - Query classification (performance/feature/comparison)
   - Metadata filtering
   - Semantic search
   - Re-ranking

5. **Test & Iterate:**
   - Create test query set (50-100 queries)
   - Measure retrieval accuracy
   - Adjust chunk sizes and overlap as needed

## Alternative Considerations

### For Very Large Document Collections
If the collection grows to 100+ models:
- Consider **hybrid search** (keyword + semantic)
- Add **model category metadata** (sedan, SUV, truck, hybrid, EV)
- Implement **two-stage retrieval** (filter by category → semantic search)

### For Complex Comparison Queries
- Consider maintaining **comparison tables** as separate chunks
- Create **synthetic comparison chunks** (e.g., "Camry vs Accord vs Sonata")

### For Evolving Content
- Version control chunks (e.g., "2024 Camry" vs "2025 Camry")
- Add update timestamps to metadata
- Implement chunk expiration/refresh logic

