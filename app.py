"""
Main Gradio application for Medical MCQ Generator.
Run with: python app.py
"""
import os
import gradio as gr
from dotenv import load_dotenv

from app.ui.gradio_app import create_interface
from app.db.database import init_db

# Load environment variables (OPENAI_API_KEY, GOOGLE_API_KEY, etc.)
load_dotenv()

# Initialize database on startup
init_db()

if __name__ == "__main__":
    demo = create_interface()
    # Support PORT environment variable for containerized deployments (e.g., Cloud Run)
    # Falls back to 7860 for local development
    port = int(os.getenv("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=port, share=False)


