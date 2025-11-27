"""Provenance verification tools."""
from google.adk.tools import FunctionTool
from typing import List, Dict


def verify_context_sentences(
    context_sentences: List[str],
    source_text: str
) -> Dict:
    """
    Verify that context sentences appear in source text.
    Returns verification status for each sentence.
    
    Args:
        context_sentences: List of context sentences to verify
        source_text: Source text to search in
    
    Returns:
        Dict with 'all_verified' (bool) and 'results' (list of verification results)
    """
    results = []
    source_text_lower = source_text.lower()
    
    for sentence in context_sentences:
        # Simple substring check (can enhance with fuzzy matching)
        sentence_lower = sentence.lower().strip()
        found = sentence_lower in source_text_lower
        
        # Also check if sentence appears with minor variations (whitespace, punctuation)
        if not found:
            # Try removing punctuation and extra whitespace
            sentence_clean = " ".join(sentence_lower.split())
            source_clean = " ".join(source_text_lower.split())
            found = sentence_clean in source_clean
        
        results.append({
            "sentence": sentence,
            "verified": found
        })
    
    all_verified = all(r["verified"] for r in results)
    return {
        "all_verified": all_verified,
        "results": results,
        "verified_count": sum(1 for r in results if r["verified"]),
        "total_count": len(results)
    }


provenance_verifier_tool = FunctionTool(verify_context_sentences)

