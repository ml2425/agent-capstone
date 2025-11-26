"""
Gradio UI for Medical MCQ Generator.
Implements all UI components from plan/UI/ui_plan.md
"""
import gradio as gr
from typing import Optional, Tuple
import json


# Mock data for skeleton UI
MOCK_ARTICLES = [
    {
        "title": "Metformin in Type 2 Diabetes: A Comprehensive Review",
        "authors": "Smith J, et al.",
        "year": "2023",
        "abstract": "This study examines the efficacy of metformin as first-line treatment for type 2 diabetes mellitus...",
        "pubmed_id": "12345678"
    },
    {
        "title": "Diabetes Management: Current Guidelines and Best Practices",
        "authors": "Johnson A, et al.",
        "year": "2023",
        "abstract": "Recent guidelines emphasize the importance of early intervention...",
        "pubmed_id": "12345679"
    }
]

MOCK_TRIPLETS = [
    {
        "id": "triplet_001",
        "subject": "Metformin",
        "action": "treats",
        "object": "Type 2 Diabetes",
        "relation": "TREATS",
        "schema_valid": True,
        "context_sentences": [
            "Metformin is the first-line treatment for type 2 diabetes mellitus.",
            "It works by reducing hepatic glucose production and improving insulin sensitivity.",
            "Clinical trials have shown significant HbA1c reduction with metformin therapy."
        ],
        "source_title": "Metformin in Type 2 Diabetes: A Comprehensive Review",
        "source_authors": "Smith J, et al.",
        "source_id": "PMID:12345678"
    }
]

MOCK_MCQ = {
    "id": "mcq_001",
    "stem": "A 45-year-old patient with Type 2 Diabetes presents with elevated HbA1c levels (8.5%) and reports polyuria and polydipsia.",
    "question": "What is the first-line treatment for this patient?",
    "options": [
        "Metformin",
        "Insulin",
        "Sulfonylurea",
        "GLP-1 Agonist",
        "DPP-4 Inhibitor"
    ],
    "correct_option": 0,
    "source_title": "Metformin in Type 2 Diabetes: A Comprehensive Review",
    "source_authors": "Smith J, et al.",
    "source_id": "PMID:12345678",
    "triplet": "Metformin → treats → Type 2 Diabetes",
    "visual_prompt": "High-resolution medical illustration of metformin molecule structure, showing mechanism of action on hepatic glucose production. Medical textbook style, axial view.",
    "visual_triplet": "Metformin → demonstrates → Mechanism"
}


def search_pubmed(keywords: str) -> str:
    """Handle PubMed search (placeholder with mock results)."""
    if not keywords.strip():
        return "Please enter search keywords."
    
    # Mock search results
    results_html = f"🔍 **Found {len(MOCK_ARTICLES)} articles for '{keywords}':**\n\n"
    
    for i, article in enumerate(MOCK_ARTICLES, 1):
        results_html += f"""
**{i}. {article['title']}**
- Authors: {article['authors']}
- Year: {article['year']}
- Abstract: {article['abstract'][:150]}...
- PubMed ID: {article['pubmed_id']} *(internal use only)*

"""
    
    return results_html


def handle_pdf_upload(file) -> str:
    """Handle PDF upload (placeholder)."""
    if file is None:
        return "No file uploaded."
    return f"📁 PDF uploaded: {file.name}\n*Extraction feature coming soon*"


def display_triplets() -> str:
    """Display triplets for review (placeholder)."""
    if not MOCK_TRIPLETS:
        return "No triplets available for review."
    
    triplet = MOCK_TRIPLETS[0]
    html = f"""
## 🔍 Triplet Review

### Triplet Information:
- **Subject:** {triplet['subject']}
- **Action:** {triplet['action']}
- **Object:** {triplet['object']}
- **Relation:** {triplet['relation']}
- **Schema Status:** {'✅ Valid' if triplet['schema_valid'] else '⚠️ Needs Review'}

### Provenance Evidence (Context Sentences):
"""
    for sentence in triplet['context_sentences']:
        html += f"> {sentence}\n\n"
    
    html += f"""
### 📌 Provenance:
- **Title:** {triplet['source_title']}
- **Authors:** {triplet['source_authors']}
- **PubMed ID:** {triplet['source_id'].replace('PMID:', '')}

---
*Accept/Reject/Edit buttons coming soon*
"""
    return html


def display_original_mcq() -> Tuple[str, str, str]:
    """Display original MCQ (placeholder). Returns (mcq_html, visual_prompt, visual_triplet)."""
    mcq = MOCK_MCQ
    html = f"""
## 📝 Original MCQ
**Status:** Pending

### Clinical Stem:
{mcq['stem']}

### Question:
{mcq['question']}

### Options:
"""
    for i, option in enumerate(mcq['options'], start=1):
        marker = "✅" if i - 1 == mcq['correct_option'] else "  "
        html += f"{marker} {chr(64+i)}) {option}\n"
    
    html += f"""
### 📌 Provenance:
- **Title:** {mcq['source_title']}
- **Authors:** {mcq['source_authors']}
- **PubMed ID:** {mcq['source_id'].replace('PMID:', '')}
- **Triplet:** {mcq['triplet']}

---
*Edit/Regenerate/Approve/Reject buttons coming soon*
"""
    return html, mcq['visual_prompt'], mcq['visual_triplet']


def handle_generate_image(visual_prompt: str, llm_model: str):
    """Handle image generation (placeholder)."""
    # Return placeholder - in real implementation, this would call image generation API
    return (
        gr.update(visible=True, value=None, label="Generated Image (placeholder)"),
        gr.update(visible=True),
        gr.update(visible=True),
        "🖼️ Image generation requested (feature coming soon)"
    )


def display_updated_mcq() -> str:
    """Display updated MCQ (second display - placeholder)."""
    mcq = MOCK_MCQ.copy()
    mcq['stem'] = "A 45-year-old obese patient with Type 2 Diabetes, HbA1c 8.5%, presents with elevated glucose levels, polyuria, polydipsia, and recent weight gain. Physical examination reveals acanthosis nigricans."
    
    html = f"""
## 📝 Updated MCQ (LLM Generated)
**Status:** Pending Review

### Clinical Stem:
{mcq['stem']}

### Question:
{mcq['question']}

### Options:
"""
    for i, option in enumerate(mcq['options'], start=1):
        marker = "✅" if i - 1 == mcq['correct_option'] else "  "
        html += f"{marker} {chr(64+i)}) {option}\n"
    
    html += f"""
### 📌 Provenance:
- **Title:** {mcq['source_title']}
- **Authors:** {mcq['source_authors']}
- **PubMed ID:** {mcq['source_id'].replace('PMID:', '')}
- **Triplet:** {mcq['triplet']}

### 🎨 Optimized Visual Prompt:
{mcq['visual_prompt']}

**Visual Triplet:** {mcq['visual_triplet']}

---
*Accept Update/Reject Update/Request Another Update/Revert to Original buttons coming soon*
"""
    return html


def update_llm_model(model: str) -> str:
    """Update LLM model selection."""
    return f"✅ LLM model set to: {model}"


def create_interface():
    """Create the main Gradio interface."""
    
    with gr.Blocks(title="Medical MCQ Generator") as demo:
        # Header with LLM Selector
        with gr.Row():
            gr.Markdown("# 🏥 Medical MCQ Generator")
            llm_selector = gr.Dropdown(
                choices=["ChatGPT 4o", "Gemini 2.5"],
                value="ChatGPT 4o",
                label="LLM Model",
                scale=1
            )
            llm_status = gr.Textbox(label="Status", value="✅ ChatGPT 4o selected", interactive=False, scale=2)
        
        llm_selector.change(fn=update_llm_model, inputs=llm_selector, outputs=llm_status)
        
        # Main Tabs
        with gr.Tabs():
            # Tab 1: Source Search/Upload
            with gr.Tab("📚 Source Search/Upload"):
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Markdown("### Search PubMed Articles")
                        pubmed_search = gr.Textbox(
                            label="Enter keywords",
                            placeholder="e.g., diabetes treatment, metformin",
                            lines=1
                        )
                        search_btn = gr.Button("🔍 Search", variant="primary")
                        search_results = gr.Markdown(value="*Enter keywords and click Search*")
                        
                        gr.Markdown("---")
                        gr.Markdown("### Upload PDF Document")
                        pdf_upload = gr.File(
                            label="Upload PDF",
                            file_types=[".pdf"]
                        )
                        upload_status = gr.Textbox(label="Upload Status", interactive=False)
                
                    with gr.Column(scale=1):
                        gr.Markdown("### 📋 Ingested Sources")
                        ingested_sources = gr.Markdown(value="*No sources ingested yet*")
                
                # Connect handlers
                search_btn.click(fn=search_pubmed, inputs=pubmed_search, outputs=search_results)
                pdf_upload.change(fn=handle_pdf_upload, inputs=pdf_upload, outputs=upload_status)
            
            # Tab 2: Triplet Review
            with gr.Tab("🔍 Triplet Review"):
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("### Review Extracted Triplets")
                        refresh_triplets = gr.Button("🔄 Refresh Triplets", variant="primary")
                        triplet_display = gr.Markdown(value="*Click Refresh to load triplets*")
                        
                        with gr.Row():
                            accept_btn = gr.Button("✅ Accept", variant="primary")
                            reject_btn = gr.Button("❌ Reject")
                            edit_btn = gr.Button("✏️ Edit")
                        
                        triplet_action_status = gr.Textbox(label="Action Status", interactive=False)
                
                refresh_triplets.click(fn=display_triplets, outputs=triplet_display)
                accept_btn.click(fn=lambda: "✅ Triplet accepted (feature coming soon)", outputs=triplet_action_status)
                reject_btn.click(fn=lambda: "❌ Triplet rejected (feature coming soon)", outputs=triplet_action_status)
                edit_btn.click(fn=lambda: "✏️ Edit triplet (feature coming soon)", outputs=triplet_action_status)
            
            # Tab 3: MCQ Review
            with gr.Tab("📝 MCQ Review"):
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("### Original MCQ")
                        generate_mcq_btn = gr.Button("🔄 Generate MCQ", variant="primary")
                        original_mcq_display = gr.Markdown(value="*Click Generate MCQ to create a new question*")
                        
                        with gr.Row():
                            edit_mcq_btn = gr.Button("✏️ Edit MCQ")
                            regenerate_mcq_btn = gr.Button("🔄 Regenerate MCQ")
                            approve_mcq_btn = gr.Button("✅ Approve", variant="primary")
                            reject_mcq_btn = gr.Button("❌ Reject")
                        
                        mcq_action_status = gr.Textbox(label="Action Status", interactive=False)
                        
                        gr.Markdown("---")
                        gr.Markdown("### 🎨 Optimized Visual Prompt")
                        visual_prompt_display = gr.Textbox(
                            label="Visual Prompt",
                            value="*Generate MCQ to see visual prompt*",
                            lines=4,
                            interactive=True
                        )
                        visual_triplet_display = gr.Textbox(
                            label="Visual Triplet",
                            value="",
                            interactive=False
                        )
                        generate_image_btn = gr.Button("🖼️ Generate Image", variant="primary")
                        
                        gr.Markdown("---")
                        gr.Markdown("### 🖼️ Generated Image")
                        image_display = gr.Image(label="Generated Image", visible=False)
                        image_llm_selector = gr.Radio(
                            choices=["ChatGPT 4o", "Gemini 2.5"],
                            value="ChatGPT 4o",
                            label="Generate with",
                            visible=False
                        )
                        with gr.Row(visible=False) as image_actions:
                            use_image_btn = gr.Button("✅ Use This Image", variant="primary")
                            regenerate_image_btn = gr.Button("🔄 Regenerate")
                            remove_image_btn = gr.Button("❌ Remove")
                        image_action_status = gr.Textbox(label="Image Action Status", interactive=False, visible=False)
                        
                        gr.Markdown("---")
                        gr.Markdown("### Request MCQ Update")
                        update_request = gr.Textbox(
                            label="Describe the update you want",
                            placeholder="e.g., Add more clinical context to stem",
                            lines=2
                        )
                        request_update_btn = gr.Button("🔄 Request Update", variant="primary")
                        
                        gr.Markdown("### Updated MCQ (LLM Generated)")
                        updated_mcq_display = gr.Markdown(value="*Request an update to see the LLM-generated version*")
                        
                        with gr.Row():
                            accept_update_btn = gr.Button("✅ Accept Update", variant="primary")
                            reject_update_btn = gr.Button("❌ Reject Update")
                            another_update_btn = gr.Button("🔄 Request Another Update")
                            revert_btn = gr.Button("↩️ Revert to Original")
                        
                        update_action_status = gr.Textbox(label="Update Action Status", interactive=False)
                
                # Connect handlers
                generate_mcq_btn.click(
                    fn=display_original_mcq, 
                    outputs=[original_mcq_display, visual_prompt_display, visual_triplet_display]
                )
                generate_image_btn.click(
                    fn=handle_generate_image,
                    inputs=[visual_prompt_display, image_llm_selector],
                    outputs=[image_display, image_llm_selector, image_actions, image_action_status]
                )
                use_image_btn.click(fn=lambda: "✅ Image accepted (feature coming soon)", outputs=image_action_status)
                regenerate_image_btn.click(fn=lambda: "🔄 Regenerating image (feature coming soon)", outputs=image_action_status)
                remove_image_btn.click(fn=lambda: (gr.update(visible=False), gr.update(visible=False), gr.update(visible=False), "❌ Image removed"), 
                                      outputs=[image_display, image_llm_selector, image_actions, image_action_status])
                request_update_btn.click(fn=display_updated_mcq, outputs=updated_mcq_display)
                
                edit_mcq_btn.click(fn=lambda: "✏️ Edit MCQ (feature coming soon)", outputs=mcq_action_status)
                regenerate_mcq_btn.click(fn=lambda: "🔄 Regenerate MCQ (feature coming soon)", outputs=mcq_action_status)
                approve_mcq_btn.click(fn=lambda: "✅ MCQ approved (feature coming soon)", outputs=mcq_action_status)
                reject_mcq_btn.click(fn=lambda: "❌ MCQ rejected (feature coming soon)", outputs=mcq_action_status)
                
                accept_update_btn.click(fn=lambda: "✅ Update accepted (feature coming soon)", outputs=update_action_status)
                reject_update_btn.click(fn=lambda: "❌ Update rejected (feature coming soon)", outputs=update_action_status)
                another_update_btn.click(fn=lambda: "🔄 Another update requested (feature coming soon)", outputs=update_action_status)
                revert_btn.click(fn=lambda: "↩️ Reverted to original (feature coming soon)", outputs=update_action_status)
            
            # Tab 4: Knowledge Base (Optional)
            with gr.Tab("📚 Knowledge Base"):
                gr.Markdown("### Browse Approved Triplets and MCQs")
                gr.Markdown("*This feature will be implemented in a future phase*")
    
    return demo

