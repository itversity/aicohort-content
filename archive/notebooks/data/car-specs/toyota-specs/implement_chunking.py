"""
Section-Based Chunking Implementation for Toyota Specifications RAG
This script demonstrates the recommended chunking strategy.
"""

import pypdf
import re
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass
import json

@dataclass
class Chunk:
    """Represents a single chunk of text with metadata"""
    content: str
    metadata: Dict[str, Any]
    chunk_id: str
    
    def to_dict(self):
        return {
            "chunk_id": self.chunk_id,
            "content": self.content,
            "metadata": self.metadata,
            "token_count": len(self.content.split())  # Approximate token count
        }

class ToyotaSpecChunker:
    """Chunks Toyota specification documents using section-based strategy"""
    
    # Section headers to identify boundaries
    SECTION_PATTERNS = [
        r"^Overview$",
        r"^Engine Options?$",
        r"^Performance",
        r"^Safety Features?$",
        r"^Technology",
        r"^Comfort",
        r"^Design$",
        r"^Dimensions?",
        r"^Capacity",
        r"^Warranty",
        r"^Competitor Comparison",
        r"^Sales Strategies?",
        r"^Key Aspects"
    ]
    
    def __init__(self, min_chunk_size: int = 150, max_chunk_size: int = 700, overlap: int = 50):
        self.min_chunk_size = min_chunk_size
        self.max_chunk_size = max_chunk_size
        self.overlap = overlap
        
    def extract_model_name(self, text: str) -> str:
        """Extract Toyota model name from text"""
        # Look for patterns like "Toyota Camry:", "Toyota RAV4:", etc.
        match = re.search(r"Toyota\s+([A-Za-z0-9]+)", text)
        if match:
            return f"Toyota {match.group(1)}"
        return "Toyota Unknown"
    
    def identify_sections(self, text: str) -> List[Dict[str, Any]]:
        """Identify section boundaries in the document"""
        sections = []
        lines = text.split('\n')
        current_section = None
        current_content = []
        current_start_line = 0
        
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            
            # Check if line matches any section pattern
            is_section_header = False
            for pattern in self.SECTION_PATTERNS:
                if re.match(pattern, line_stripped, re.IGNORECASE):
                    # Save previous section
                    if current_section and current_content:
                        sections.append({
                            "section": current_section,
                            "content": '\n'.join(current_content),
                            "start_line": current_start_line,
                            "end_line": i - 1
                        })
                    
                    # Start new section
                    current_section = line_stripped
                    current_content = [line]
                    current_start_line = i
                    is_section_header = True
                    break
            
            # If not a header, add to current section
            if not is_section_header and line_stripped:
                if current_section:
                    current_content.append(line)
                else:
                    # Content before first section (usually title/header)
                    if not sections:
                        current_section = "Overview"
                        current_content.append(line)
                        current_start_line = i
        
        # Add last section
        if current_section and current_content:
            sections.append({
                "section": current_section,
                "content": '\n'.join(current_content),
                "start_line": current_start_line,
                "end_line": len(lines) - 1
            })
        
        return sections
    
    def extract_topics_and_specs(self, content: str) -> tuple:
        """Extract topics and specifications mentioned in content"""
        topics = set()
        specs = []
        
        # Topic keywords
        topic_keywords = {
            "engine": ["engine", "motor", "powertrain", "cylinder"],
            "hybrid": ["hybrid", "electric", "ev", "plug-in"],
            "performance": ["horsepower", "hp", "torque", "acceleration"],
            "fuel_economy": ["mpg", "fuel economy", "efficiency", "miles per gallon"],
            "safety": ["safety", "collision", "airbag", "sensor", "detection"],
            "technology": ["touchscreen", "infotainment", "carplay", "android auto"],
            "capacity": ["seating", "cargo", "towing", "capacity"],
            "warranty": ["warranty", "coverage", "years", "miles"],
            "transmission": ["transmission", "cvt", "automatic"],
        }
        
        content_lower = content.lower()
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                topics.add(topic)
        
        # Extract specs (HP, MPG, prices, measurements)
        spec_patterns = [
            r'\d+\s*HP',
            r'\d+\s*hp',
            r'\d+\s*MPG',
            r'\d+\s*mpg',
            r'\$\d+,?\d*',
            r'\d+\.\d+L',
            r'\d+-speed',
        ]
        
        for pattern in spec_patterns:
            matches = re.findall(pattern, content)
            specs.extend(matches)
        
        return list(topics), specs
    
    def create_chunks(self, pdf_path: Path) -> List[Chunk]:
        """Create chunks from a Toyota specification PDF"""
        chunks = []
        
        # Extract text from PDF
        with open(pdf_path, 'rb') as f:
            reader = pypdf.PdfReader(f)
            full_text = ""
            for page in reader.pages:
                full_text += page.extract_text()
        
        # Extract model name
        model_name = self.extract_model_name(full_text)
        
        # Identify sections
        sections = self.identify_sections(full_text)
        
        if not sections:
            # Fallback: treat entire document as one chunk if no sections found
            sections = [{
                "section": "Full Document",
                "content": full_text,
                "start_line": 0,
                "end_line": len(full_text.split('\n'))
            }]
        
        # Create chunks from sections
        for idx, section_data in enumerate(sections):
            section_name = section_data["section"]
            content = section_data["content"]
            word_count = len(content.split())
            
            # Skip very small sections (less than 20 words)
            if word_count < 20:
                continue
            
            # Extract topics and specs
            topics, specs = self.extract_topics_and_specs(content)
            
            # If section is too large, split it
            if word_count > self.max_chunk_size:
                sub_chunks = self._split_large_section(content, model_name, section_name, idx)
                chunks.extend(sub_chunks)
            else:
                # Create chunk
                chunk_id = f"{model_name.lower().replace(' ', '_')}_{section_name.lower().replace(' ', '_')}_{idx:03d}"
                
                chunk = Chunk(
                    content=content,
                    metadata={
                        "model": model_name,
                        "section": section_name,
                        "topics": topics,
                        "specs_mentioned": specs[:10],  # Limit to first 10 specs
                        "doc_type": "specification",
                        "source_file": pdf_path.name,
                        "chunk_sequence": idx,
                        "word_count": word_count
                    },
                    chunk_id=chunk_id
                )
                chunks.append(chunk)
        
        return chunks
    
    def _split_large_section(self, content: str, model_name: str, section_name: str, base_idx: int) -> List[Chunk]:
        """Split a large section into smaller chunks with overlap"""
        chunks = []
        words = content.split()
        
        start = 0
        sub_chunk_idx = 0
        
        while start < len(words):
            # Get chunk of words
            end = min(start + self.max_chunk_size, len(words))
            chunk_words = words[start:end]
            chunk_content = ' '.join(chunk_words)
            
            # Extract topics and specs
            topics, specs = self.extract_topics_and_specs(chunk_content)
            
            chunk_id = f"{model_name.lower().replace(' ', '_')}_{section_name.lower().replace(' ', '_')}_{base_idx:03d}_{sub_chunk_idx:02d}"
            
            chunk = Chunk(
                content=chunk_content,
                metadata={
                    "model": model_name,
                    "section": section_name,
                    "subsection_part": sub_chunk_idx + 1,
                    "topics": topics,
                    "specs_mentioned": specs[:10],
                    "doc_type": "specification",
                    "chunk_sequence": base_idx,
                    "word_count": len(chunk_words)
                },
                chunk_id=chunk_id
            )
            chunks.append(chunk)
            
            # Move to next chunk with overlap
            start = end - self.overlap
            sub_chunk_idx += 1
            
            # Prevent infinite loop
            if start >= len(words) - self.overlap:
                break
        
        return chunks
    
    def process_all_pdfs(self, directory: Path) -> List[Chunk]:
        """Process all PDF files in a directory"""
        all_chunks = []
        
        pdf_files = sorted(directory.glob("*.pdf"))
        
        for pdf_file in pdf_files:
            print(f"Processing {pdf_file.name}...")
            try:
                chunks = self.create_chunks(pdf_file)
                all_chunks.extend(chunks)
                print(f"  Created {len(chunks)} chunks")
            except Exception as e:
                print(f"  Error: {e}")
        
        return all_chunks


def main():
    """Main execution"""
    print("=" * 80)
    print("TOYOTA SPECIFICATIONS - SECTION-BASED CHUNKING")
    print("=" * 80)
    
    # Initialize chunker
    chunker = ToyotaSpecChunker(
        min_chunk_size=150,
        max_chunk_size=700,
        overlap=50
    )
    
    # Process PDFs
    pdf_dir = Path(__file__).parent
    all_chunks = chunker.process_all_pdfs(pdf_dir)
    
    # Summary
    print(f"\n{'=' * 80}")
    print(f"CHUNKING SUMMARY")
    print(f"{'=' * 80}")
    print(f"Total chunks created: {len(all_chunks)}")
    print(f"\nChunk size distribution:")
    
    sizes = [chunk.metadata['word_count'] for chunk in all_chunks]
    print(f"  Min: {min(sizes)} words")
    print(f"  Max: {max(sizes)} words")
    print(f"  Average: {sum(sizes) / len(sizes):.1f} words")
    
    # Save chunks to JSON
    output_file = pdf_dir / "chunks_output.json"
    with open(output_file, 'w') as f:
        json.dump([chunk.to_dict() for chunk in all_chunks], f, indent=2)
    
    print(f"\n✓ Chunks saved to: {output_file}")
    
    # Display sample chunks
    print(f"\n{'=' * 80}")
    print("SAMPLE CHUNKS")
    print(f"{'=' * 80}")
    
    for i, chunk in enumerate(all_chunks[:3]):
        print(f"\n--- Chunk {i + 1}: {chunk.chunk_id} ---")
        print(f"Model: {chunk.metadata['model']}")
        print(f"Section: {chunk.metadata['section']}")
        print(f"Topics: {', '.join(chunk.metadata['topics'])}")
        print(f"Word Count: {chunk.metadata['word_count']}")
        print(f"\nContent Preview:")
        preview = chunk.content[:300] + "..." if len(chunk.content) > 300 else chunk.content
        print(preview)


if __name__ == "__main__":
    main()

