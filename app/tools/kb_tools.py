"""Knowledge Base tools for agents."""
from google.adk.tools import FunctionTool
from app.services.kb_service import (
    query_triplets_for_distractors,
    get_approved_triplets
)
from app.db.database import SessionLocal
from typing import Dict, List, Optional


def query_kb_for_distractors(
    subject: Optional[str] = None,
    action: Optional[str] = None,
    object: Optional[str] = None
) -> Dict:
    """
    Query KB for plausible swap triplets for distractor generation.
    Returns list of triplets matching query criteria.
    
    Args:
        subject: Optional subject to filter by (KB Query 1: same subject, different action/object)
        action: Optional action to filter by (KB Query 2: same action/object, different subject)
        object: Optional object to filter by (KB Query 2: same action/object, different subject)
    
    Returns:
        Dict with 'triplets' list
    """
    db = SessionLocal()
    try:
        triplets = query_triplets_for_distractors(db, subject, action, object)
        return {
            "triplets": [
                {
                    "subject": t.subject,
                    "action": t.action,
                    "object": t.object,
                    "relation": t.relation
                }
                for t in triplets
            ],
            "count": len(triplets)
        }
    finally:
        db.close()


def get_approved_triplets_for_mcq(source_id: Optional[int] = None) -> Dict:
    """
    Get approved triplets for MCQ generation.
    
    Args:
        source_id: Optional source ID to filter by
    
    Returns:
        Dict with 'triplets' list
    """
    db = SessionLocal()
    try:
        triplets = get_approved_triplets(db, source_id)
        return {
            "triplets": [
                {
                    "id": t.id,
                    "subject": t.subject,
                    "action": t.action,
                    "object": t.object,
                    "relation": t.relation,
                    "source_id": t.source_id
                }
                for t in triplets
            ],
            "count": len(triplets)
        }
    finally:
        db.close()


kb_query_tool = FunctionTool(query_kb_for_distractors)
kb_get_approved_tool = FunctionTool(get_approved_triplets_for_mcq)

