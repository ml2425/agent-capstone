"""PDF ingestion and text extraction service."""
from pypdf import PdfReader
from io import BytesIO
from typing import Dict
from sqlalchemy.orm import Session
from app.db.models import Source
import hashlib


def extract_pdf_text(pdf_bytes: bytes) -> str:
    """
    Extract text from PDF bytes.
    
    Args:
        pdf_bytes: PDF file content as bytes
    
    Returns:
        Extracted text string
    """
    try:
        reader = PdfReader(BytesIO(pdf_bytes))
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        raise ValueError(f"Failed to extract PDF text: {e}")


def register_pdf_source(filename: str, pdf_bytes: bytes, db: Session) -> Dict:
    """
    Register uploaded PDF as source in database.
    
    Args:
        filename: Original PDF filename
        pdf_bytes: PDF file content as bytes
        db: Database session
    
    Returns:
        Dict with source information
    """
    # Extract text
    content = extract_pdf_text(pdf_bytes)
    
    # Generate source_id from filename hash
    source_id = f"pdf_{hashlib.md5(filename.encode()).hexdigest()[:8]}"
    
    # Check if source already exists
    existing = db.query(Source).filter(Source.source_id == source_id).first()
    if existing:
        return {
            "source_id": existing.source_id,
            "title": existing.title,
            "content": existing.content,
            "type": "pdf",
            "id": existing.id
        }
    
    # Create source record
    source = Source(
        source_id=source_id,
        source_type="pdf",
        title=filename,
        content=content
    )
    db.add(source)
    db.commit()
    db.refresh(source)
    
    return {
        "source_id": source_id,
        "title": filename,
        "content": content,
        "type": "pdf",
        "id": source.id
    }


def register_pubmed_source(article_data: Dict, db: Session) -> Dict:
    """
    Register PubMed article as source in database.
    
    Args:
        article_data: Dict with pubmed_id, title, authors, year, abstract
        db: Database session
    
    Returns:
        Dict with source information
    """
    source_id = f"PMID:{article_data['pubmed_id']}"
    
    # Check if source already exists
    existing = db.query(Source).filter(Source.source_id == source_id).first()
    if existing:
        return {
            "source_id": existing.source_id,
            "title": existing.title,
            "content": existing.content,
            "type": "pubmed",
            "id": existing.id
        }
    
    # Create source record
    source = Source(
        source_id=source_id,
        source_type="pubmed",
        title=article_data.get("title", ""),
        authors=article_data.get("authors"),
        publication_year=int(article_data["year"]) if article_data.get("year", "Unknown").isdigit() else None,
        content=article_data.get("abstract", "")
    )
    db.add(source)
    db.commit()
    db.refresh(source)
    
    return {
        "source_id": source_id,
        "title": source.title,
        "content": source.content,
        "type": "pubmed",
        "id": source.id
    }

