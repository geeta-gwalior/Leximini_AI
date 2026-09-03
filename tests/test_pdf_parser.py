import pytest
from services.rag_engine.pdf_parser import extract_text_from_pdf_bytes, chunk_legal_text

def test_chunk_legal_text():
    sample_text = """
    Bail Application under Section 438 of the Code of Criminal Procedure, 1973.
    The applicant respectfully submits that he has been falsely implicated in FIR No. 104/2026.
    The offences alleged are non-bailable under Bharatiya Nyaya Sanhita Section 304.
    """
    chunks = chunk_legal_text(sample_text, chunk_size=100, overlap=20)
    assert isinstance(chunks, list)
    assert len(chunks) > 0
    assert "chunk_id" in chunks[0]
    assert "content" in chunks[0]

def test_extract_text_fallback():
    raw_bytes = b"Sample Legal Text Document for Testing"
    extracted = extract_text_from_pdf_bytes(raw_bytes)
    assert "Sample Legal Text" in extracted
