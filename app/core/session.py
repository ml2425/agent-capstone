"""Session management with DatabaseSessionService."""
from google.adk.session import DatabaseSessionService
import os

SESSION_DB_URL = os.getenv("SESSION_DB_URL", "sqlite:///./agent_sessions.db")

session_service = DatabaseSessionService(db_url=SESSION_DB_URL)

