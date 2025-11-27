"""Runner with session restore functionality."""
from google.adk.runners import Runner
from google.genai import types
from app.core.app import app
from app.core.session import session_service
from typing import Optional, Any
import time


runner = Runner(app=app, session_service=session_service)


async def run_agent(new_message: str, user_id: str = "default", session_id: Optional[str] = None) -> Any:
    """
    Helper function to run agent and collect final result from async generator.
    
    This function manages a complete conversation session, handling session creation/retrieval,
    query processing, and response streaming.
    
    Args:
        new_message: Message text to send to agent
        user_id: User identifier
        session_id: Session ID (if None, will create new session)
    
    Returns:
        Final result from agent pipeline (text content from final response)
    """
    if session_id is None:
        session_id = await create_new_session(user_id)
    
    # Create proper message object using google.genai.types
    # Runner expects a Content object with role and parts, not a plain string
    query_content = types.Content(role="user", parts=[types.Part(text=new_message)])
    
    # runner.run_async returns an async generator - collect all events
    result = None
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=query_content
    ):
        # Extract final response content
        if event.is_final_response() and event.content and event.content.parts:
            text = event.content.parts[0].text
            if text and text != "None":
                result = text
        else:
            # Keep the last event as fallback
            result = event
    
    return result


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

