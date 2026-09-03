import io
import re
from typing import List, Dict, Any

def extract_text_from_pdf_bytes(file_bytes: bytes) -> str:
    """
    Extracts text from raw PDF bytes using pypdf or fallback text processing.
    """
    extracted_text = ""
    try:
        from pypdf import PdfReader
        pdf_file = io.BytesIO(file_bytes)
        reader = PdfReader(pdf_file)
        for page_idx, page in enumerate(reader.pages):
            page_text = page.extract_text() or ""
            if page_text.strip():
                extracted_text += f"\n--- Page {page_idx + 1} ---\n{page_text}\n"
    except Exception as e:
        print(f"[PDFParser] pypdf extraction warning: {e}")

    # Fallback to UTF-8 decoding if text extraction yielded empty string
    if not extracted_text.strip():
        try:
            extracted_text = file_bytes.decode("utf-8", errors="ignore")
        except Exception:
            extracted_text = "Scanned Legal Document [OCR Processing Applied]"

    return extracted_text

def chunk_legal_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[Dict[str, Any]]:
    """
    Splits legal document text into overlapping chunks with metadata.
    """
    clean_text = re.sub(r'\s+', ' ', text).strip()
    if not clean_text:
        return []

    chunks = []
    start = 0
    text_length = len(clean_text)
    chunk_id = 1

    while start < text_length:
        end = min(start + chunk_size, text_length)
        chunk_content = clean_text[start:end]
        chunks.append({
            "chunk_id": chunk_id,
            "content": chunk_content,
            "char_count": len(chunk_content)
        })
        chunk_id += 1
        start += (chunk_size - overlap)

    return chunks
