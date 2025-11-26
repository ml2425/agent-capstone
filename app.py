"""
Main Gradio application for Medical MCQ Generator.
Run with: python app.py
"""
import gradio as gr
from app.ui.gradio_app import create_interface

if __name__ == "__main__":
    demo = create_interface()
    demo.launch(server_name="127.0.0.1", server_port=7860, share=False)

