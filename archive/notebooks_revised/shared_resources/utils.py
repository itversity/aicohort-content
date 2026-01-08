"""
Shared utility functions for RAG Bootcamp
These functions are used across multiple weeks for common tasks.
"""

from pathlib import Path
from typing import Dict, List, Any
import pypdf


def load_pdf(pdf_path: str | Path) -> str:
    """
    Load and extract text from a PDF file.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        str: Full text content extracted from the PDF
        
    Example:
        >>> text = load_pdf("data/car-specs/toyota-specs/Toyota_Camry_Specifications.pdf")
        >>> print(f"Loaded {len(text)} characters")
    """
    pdf_path = Path(pdf_path)
    
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")
    
    with open(pdf_path, 'rb') as f:
        reader = pypdf.PdfReader(f)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    
    return text


def get_file_info(pdf_path: str | Path) -> Dict[str, Any]:
    """
    Get detailed information about a PDF file.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        dict: Information about the PDF including:
            - filename: Name of the file
            - size_kb: File size in kilobytes
            - size_mb: File size in megabytes
            - pages: Number of pages
            - has_text: Whether text can be extracted
            
    Example:
        >>> info = get_file_info("Toyota_Camry_Specifications.pdf")
        >>> print(f"Pages: {info['pages']}, Size: {info['size_kb']:.1f} KB")
    """
    pdf_path = Path(pdf_path)
    
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")
    
    # Get file size
    size_bytes = pdf_path.stat().st_size
    size_kb = size_bytes / 1024
    size_mb = size_bytes / (1024 * 1024)
    
    # Get page count and check for text
    with open(pdf_path, 'rb') as f:
        reader = pypdf.PdfReader(f)
        page_count = len(reader.pages)
        
        # Check if first page has extractable text
        has_text = len(reader.pages[0].extract_text().strip()) > 0 if page_count > 0 else False
    
    return {
        "filename": pdf_path.name,
        "size_kb": size_kb,
        "size_mb": size_mb,
        "pages": page_count,
        "has_text": has_text
    }


def analyze_text(text: str) -> Dict[str, Any]:
    """
    Analyze text content and return statistics.
    
    Args:
        text: Text content to analyze
        
    Returns:
        dict: Statistics about the text including:
            - characters: Total character count
            - characters_no_spaces: Character count excluding spaces
            - words: Word count
            - lines: Line count
            - avg_word_length: Average word length
            
    Example:
        >>> text = load_pdf("Toyota_Camry_Specifications.pdf")
        >>> stats = analyze_text(text)
        >>> print(f"Words: {stats['words']}, Avg word length: {stats['avg_word_length']:.1f}")
    """
    # Character counts
    char_count = len(text)
    char_no_spaces = len(text.replace(" ", "").replace("\n", "").replace("\t", ""))
    
    # Word count
    words = text.split()
    word_count = len(words)
    
    # Line count
    lines = text.split("\n")
    line_count = len([line for line in lines if line.strip()])
    
    # Average word length
    avg_word_length = sum(len(word) for word in words) / word_count if word_count > 0 else 0
    
    return {
        "characters": char_count,
        "characters_no_spaces": char_no_spaces,
        "words": word_count,
        "lines": line_count,
        "avg_word_length": avg_word_length
    }


def get_all_toyota_pdfs(data_dir: str | Path = "../data/car-specs/toyota-specs") -> List[Path]:
    """
    Get all Toyota specification PDF files from the data directory.
    
    Args:
        data_dir: Path to the directory containing Toyota PDFs
        
    Returns:
        list: List of Path objects for all PDF files, sorted alphabetically
        
    Example:
        >>> pdfs = get_all_toyota_pdfs()
        >>> print(f"Found {len(pdfs)} Toyota specification documents")
        >>> for pdf in pdfs:
        ...     print(f"  - {pdf.name}")
    """
    data_dir = Path(data_dir)
    
    if not data_dir.exists():
        raise FileNotFoundError(f"Data directory not found: {data_dir}")
    
    pdfs = sorted(data_dir.glob("*.pdf"))
    
    if len(pdfs) == 0:
        raise FileNotFoundError(f"No PDF files found in: {data_dir}")
    
    return pdfs


def extract_model_name(pdf_path: str | Path) -> str:
    """
    Extract the Toyota model name from a PDF filename.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        str: Model name (e.g., "Toyota Camry", "Toyota RAV4")
        
    Example:
        >>> model = extract_model_name("Toyota_Camry_Specifications.pdf")
        >>> print(model)  # "Toyota Camry"
    """
    pdf_path = Path(pdf_path)
    filename = pdf_path.stem  # Filename without extension
    
    # Replace underscores with spaces and handle common patterns
    if filename.startswith("Toyota_"):
        # Format: Toyota_Camry_Specifications -> Toyota Camry
        parts = filename.replace("_", " ").split()
        # Take "Toyota" + model name (everything before "Specifications")
        model_parts = []
        for part in parts:
            if part.lower() in ["specifications", "spec", "specs"]:
                break
            model_parts.append(part)
        return " ".join(model_parts)
    elif filename.startswith("Introduction"):
        return "Introduction to Toyota"
    else:
        # Fallback: just replace underscores
        return filename.replace("_", " ")


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes: File size in bytes
        
    Returns:
        str: Formatted size (e.g., "74.3 KB", "1.2 MB")
        
    Example:
        >>> size = format_file_size(76234)
        >>> print(size)  # "74.4 KB"
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


def print_dataset_summary(data_dir: str | Path = "../data/car-specs/toyota-specs"):
    """
    Print a formatted summary of the Toyota dataset.
    
    Args:
        data_dir: Path to the directory containing Toyota PDFs
        
    Example:
        >>> print_dataset_summary()
        Toyota Specifications Dataset Summary
        =====================================
        Total files: 8
        ...
    """
    pdfs = get_all_toyota_pdfs(data_dir)
    
    print("Toyota Specifications Dataset Summary")
    print("=" * 60)
    print(f"Total files: {len(pdfs)}")
    print()
    
    total_size = 0
    total_pages = 0
    
    print(f"{'Filename':<45} {'Size':<10} {'Pages':<6}")
    print("-" * 60)
    
    for pdf in pdfs:
        info = get_file_info(pdf)
        total_size += info['size_kb']
        total_pages += info['pages']
        print(f"{info['filename']:<45} {info['size_kb']:>6.1f} KB {info['pages']:>5}")
    
    print("-" * 60)
    print(f"{'Total':<45} {total_size:>6.1f} KB {total_pages:>5}")
    print()
    print(f"Average file size: {total_size / len(pdfs):.1f} KB")
    print(f"Average pages per file: {total_pages / len(pdfs):.1f}")


# Example usage
if __name__ == "__main__":
    # Demonstrate the utility functions
    print("RAG Bootcamp - Shared Utilities Demo")
    print("=" * 60)
    
    # Print dataset summary
    try:
        print_dataset_summary()
    except FileNotFoundError as e:
        print(f"Note: {e}")
        print("This is expected if run outside the notebooks_revised directory")

