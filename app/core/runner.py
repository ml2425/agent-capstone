"""Runner with session restore functionality."""
from google.adk import Runner
from app.core.app import app
from app.core.session import session_service
from typing import Optional
import time


runner = Runner(app=app, session_service=session_service)


async def get_last_session(user_id: str = "default") -> Optional[str]:
    """
    Get last session ID for user.
    
    Args:
        user_id: User identifier
    
    Returns:
        Session ID or None if no previous session
    """
    try:
        # Query session service for most recent session
        # Note: DatabaseSessionService may need custom query method
        # For now, we'll create a new session if none exists
        # In production, implement proper session retrieval
        return None  # Placeholder - implement based on DatabaseSessionService API
    except Exception:
        return None


async def create_new_session(user_id: str = "default") -> str:
    """
    Create a new session.
    
    Args:
        user_id: User identifier
    
    Returns:
        New session ID
    """
    session_id = f"session_{int(time.time())}"
    try:
        await session_service.create_session(
            app_name="MedicalMCQGenerator",
            user_id=user_id,
            session_id=session_id
        )
        return session_id
    except Exception as e:
        # If session creation fails, return ID anyway
        # Session will be created on first use
        return session_id


async def restore_session(user_id: str, session_id: str):
    """
    Restore session state.
    
    Args:
        user_id: User identifier
        session_id: Session ID to restore
    
    Returns:
        Session object or None
    """
    try:
        session = await session_service.get_session(
            app_name="MedicalMCQGenerator",
            user_id=user_id,
            session_id=session_id
        )
        return session
    except Exception:
        return None

