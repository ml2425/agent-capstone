"""Session management with DatabaseSessionService."""
from google.adk.sessions import DatabaseSessionService
import os

# DatabaseSessionService requires async driver - use aiosqlite for SQLite
SESSION_DB_URL = os.getenv("SESSION_DB_URL", "sqlite+aiosqlite:///./agent_sessions.db")

session_service = DatabaseSessionService(db_url=SESSION_DB_URL)

