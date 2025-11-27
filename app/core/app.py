"""App configuration with context compaction."""
from google.adk import App
from google.adk.config import EventsCompactionConfig
from app.agents.pipeline import mcq_pipeline
from app.core.session import session_service

app = App(
    name="MedicalMCQGenerator",
    root_agent=mcq_pipeline,
    events_compaction_config=EventsCompactionConfig(
        compaction_interval=5,  # Compact every 5 turns
        overlap_size=2  # Keep 2 previous turns
    )
)

