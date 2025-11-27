"""PubMed service for searching and fetching articles."""
from Bio import Entrez
from typing import List, Dict
import os

# Set email for NCBI (required)
Entrez.email = os.getenv("NCBI_EMAIL", "your-email@example.com")


def search_pubmed(keywords: str, max_results: int = 10) -> List[Dict]:
    """
    Search PubMed by keywords and return article metadata.
    
    Args:
        keywords: Search query string
        max_results: Maximum number of results to return
    
    Returns:
        List of dicts with: pubmed_id, title, authors, year, abstract
    """
    try:
        # Search for IDs
        handle = Entrez.esearch(db="pubmed", term=keywords, retmax=max_results)
        record = Entrez.read(handle)
        handle.close()
        
        if not record["IdList"]:
            return []
        
        # Fetch article details
        handle = Entrez.efetch(db="pubmed", id=",".join(record["IdList"]), retmode="xml")
        articles = Entrez.read(handle)
        handle.close()
        
        results = []
        for article in articles["PubmedArticle"]:
            medline = article["MedlineCitation"]
            
            # Extract title
            title = medline["Article"]["ArticleTitle"]
            
            # Extract authors
            author_list = medline["Article"].get("AuthorList", [])
            authors = ", ".join([
                f"{a.get('LastName', '')} {a.get('ForeName', '')}"
                for a in author_list[:3]
            ])
            if len(author_list) > 3:
                authors += " et al."
            
            # Extract year
            pub_date = medline["Article"].get("Journal", {}).get("JournalIssue", {}).get("PubDate", {})
            year = pub_date.get("Year") or pub_date.get("MedlineDate", "Unknown")
            if isinstance(year, str) and year != "Unknown":
                # Extract year from MedlineDate if needed
                year = year[:4] if year[:4].isdigit() else "Unknown"
            
            # Extract abstract
            abstract_parts = medline["Article"].get("Abstract", {}).get("AbstractText", [])
            abstract = " ".join([str(part) for part in abstract_parts])
            
            # Get PubMed ID
            pubmed_id = str(medline["PMID"])
            
            results.append({
                "pubmed_id": pubmed_id,
                "title": title,
                "authors": authors,
                "year": str(year),
                "abstract": abstract
            })
        
        return results
    except Exception as e:
        raise ValueError(f"PubMed search failed: {e}")


def fetch_pubmed_article(pubmed_id: str) -> Dict:
    """
    Fetch full article details by PubMed ID.
    
    Args:
        pubmed_id: PubMed ID (with or without "PMID:" prefix)
    
    Returns:
        Dict with article details
    """
    # Remove "PMID:" prefix if present
    pubmed_id = pubmed_id.replace("PMID:", "").strip()
    
    try:
        handle = Entrez.efetch(db="pubmed", id=pubmed_id, retmode="xml")
        articles = Entrez.read(handle)
        handle.close()
        
        if not articles["PubmedArticle"]:
            raise ValueError(f"Article {pubmed_id} not found")
        
        article = articles["PubmedArticle"][0]
        medline = article["MedlineCitation"]
        
        # Extract title
        title = medline["Article"]["ArticleTitle"]
        
        # Extract authors
        author_list = medline["Article"].get("AuthorList", [])
        authors = ", ".join([
            f"{a.get('LastName', '')} {a.get('ForeName', '')}"
            for a in author_list[:3]
        ])
        if len(author_list) > 3:
            authors += " et al."
        
        # Extract year
        pub_date = medline["Article"].get("Journal", {}).get("JournalIssue", {}).get("PubDate", {})
        year = pub_date.get("Year") or pub_date.get("MedlineDate", "Unknown")
        if isinstance(year, str) and year != "Unknown":
            year = year[:4] if year[:4].isdigit() else "Unknown"
        
        # Extract abstract
        abstract_parts = medline["Article"].get("Abstract", {}).get("AbstractText", [])
        abstract = " ".join([str(part) for part in abstract_parts])
        
        return {
            "pubmed_id": pubmed_id,
            "title": title,
            "authors": authors,
            "year": str(year),
            "abstract": abstract
        }
    except Exception as e:
        raise ValueError(f"Failed to fetch article {pubmed_id}: {e}")

