import sys
import os
import re
from pathlib import Path
from pypdf import PdfReader

# Add backend to path so we can import services
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.document_service import _extract_text
from services.chunking_service import chunk_text, CHUNK_SIZE, CHUNK_OVERLAP

def print_header(title):
    print("==========================================================")
    print(title)
    print("==========================================================")

def print_step(step_name):
    print(f"\n{step_name}\n")

def clean_text_local(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()

def inspect_ingestion(file_path_str):
    # Resolve file path
    file_path = Path(file_path_str)
    
    # If not found directly, try relative to the workspace root or backend root
    if not file_path.exists():
        # Try relative to parent if we are in backend
        alternative_path = Path("..") / file_path_str
        if alternative_path.exists():
            file_path = alternative_path
        else:
            print(f"Error: File '{file_path_str}' not found.")
            sys.exit(1)
        
    filename = file_path.name
    extension = file_path.suffix.lower()
    
    if extension not in [".pdf", ".txt"]:
        print(f"Error: Unsupported file type '{extension}'. Must be .pdf or .txt.")
        sys.exit(1)
        
    file_type = extension.lstrip(".")
    file_size = file_path.stat().st_size
    
    # Get page count if PDF
    pages = "N/A"
    if file_type == "pdf":
        try:
            reader = PdfReader(str(file_path))
            pages = len(reader.pages)
        except Exception as e:
            pages = f"Error reading pages ({e})"
            
    # Extract text using existing document extraction logic
    try:
        extracted_text = _extract_text(file_path, file_type)
    except Exception as e:
        print(f"Failed to extract text: {e}")
        sys.exit(1)
        
    total_chars = len(extracted_text)
    
    # ------------------ PRINT OUTPUT ------------------
    
    print("==============================")
    print("UNIVERSAL CONTEXT ENGINE")
    print("INGESTION INSPECTOR")
    print("==============================")
    
    # Step 1
    print_step("Step 1: Document Information")
    print(f"Filename: {filename}")
    print(f"File Type: {file_type.upper()}")
    print(f"File Size: {file_size} bytes")
    print(f"Pages (if PDF): {pages}")
    print("\n----------------------------------")
    
    # Step 2
    print_step("Step 2: Extracted Text")
    print(f"Total Extracted Characters: {total_chars}")
    print("\nFirst 1000 Characters:")
    print(extracted_text[:1000])
    print("\nLast 500 Characters:")
    print(extracted_text[-500:] if total_chars > 500 else extracted_text)
    print("\n----------------------------------")
    
    # Step 3
    print_step("Step 3: Chunking Configuration")
    print(f"Chunk Size: {CHUNK_SIZE}")
    print(f"Chunk Overlap: {CHUNK_OVERLAP}")
    print("Chunking Strategy: Fixed-Size Character Window with Overlap")
    print("\n----------------------------------")
    
    # Step 4
    print_step("Step 4: Generated Chunks")
    
    chunks = chunk_text(extracted_text)
    cleaned_text = clean_text_local(extracted_text)
    
    current_search_idx = 0
    
    for idx, chunk in enumerate(chunks, 1):
        chunk_len = len(chunk)
        
        # Locate character range in cleaned text
        # Since chunking occurs on cleaned text, we find the range in the cleaned version.
        search_start = max(0, current_search_idx - CHUNK_OVERLAP - 10)
        char_start = cleaned_text.find(chunk, search_start)
        if char_start != -1:
            char_end = char_start + chunk_len
            current_search_idx = char_end
        else:
            char_start = 0
            char_end = chunk_len
            
        preview_text = chunk[:150]
        if chunk_len > 150:
            preview_text += "..."
            
        print("================================")
        print(f"Chunk Number: {idx}")
        print(f"Chunk Length: {chunk_len}")
        print(f"Character Range: {char_start} - {char_end}")
        print("\nPreview:")
        print(preview_text)
        print("\n--------------------------------")
        print("\nFull Chunk:")
        print(chunk)
        print("================================")
        
    print("\n----------------------------------")
    
    # Step 5
    print_step("Step 5: Chunk Statistics")
    total_chunks = len(chunks)
    shortest_chunk = min(len(c) for c in chunks) if chunks else 0
    longest_chunk = max(len(c) for c in chunks) if chunks else 0
    avg_chunk = sum(len(c) for c in chunks) / total_chunks if total_chunks > 0 else 0
    
    print(f"Total Chunks: {total_chunks}")
    print(f"Shortest Chunk: {shortest_chunk}")
    print(f"Longest Chunk: {longest_chunk}")
    print(f"Average Chunk Length: {avg_chunk:.2f}")
    print("\n----------------------------------")
    
    # Step 6
    print_step("Step 6: Final Summary")
    print("Document processed successfully.")
    print("Ready for Embedding Layer.")
    print("\n==========================================================")

if __name__ == "__main__":
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
        
    if len(sys.argv) < 2:
        print("Usage: python inspect_ingestion.py <path_to_file>")
        sys.exit(1)
        
    inspect_ingestion(sys.argv[1])
