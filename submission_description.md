# Medical MCQ Writer Agent: Generating Verifiable Questions from Medical Literature

**Generate verifiable questions from medical literature (PUBMED search) with provenance tracking**

---

## Problem Statement

Medical education requires high-quality multiple-choice questions (MCQs) that accurately assess clinical knowledge, but creating these questions presents many challenges.

The primary problem is **provenance verification**. Traditional MCQ writing is a time-consuming manual process, typically taking 30 minutes or more per question when including research, fact-checking, image sourcing, and review. This inefficiency creates a critical bottleneck: fewer medical professionals can participate as question writers, leading to limited diversity in both the writers themselves and the questions they produce. When fewer specialists contribute, question coverage becomes skewed, potentially missing important subtopics or failing to represent diverse clinical perspectives.

Modern Large Language Models (LLMs) offer the potential to dramatically improve efficiency, but they introduce a dangerous risk: **hallucination**. Without proper source verification, LLM-generated medical content can contain plausible-sounding but factually incorrect information. In medical education, this can mislead future physicians and ultimately compromise patient safety.

The medical knowledge landscape is vast and constantly expanding. Thousands of new research papers are published daily in PubMed, the world's largest medical literature database with over 35 million citations. Keeping MCQ content current with the latest evidence while maintaining accuracy and provenance is nearly impossible at scale using traditional manual methods.

Our solution addresses these challenges by solving the **provenance problem first**. By ensuring every MCQ is directly linked to its source article with verifiable reasoning paths, we can leverage LLM efficiency gains—reducing question generation time from 30 minutes to minutes—while maintaining the accuracy and trustworthiness essential for medical education. 

This approach not only improves efficiency but also enables a more diverse pool of medical specialists to contribute as question writers, expanding question coverage and reducing knowledge gaps.

---

## Why Agents?

Medical MCQ development involves a complex, multi-step workflow that is inherently repetitive: search literature, extract facts, validate against medical ontologies, generate questions, refine quality, and curate images or diagrams. While medical professionals are competent with modern chatbot interfaces, manually orchestrating these repetitive steps through direct LLM interactions remains time-consuming and error-prone.

**SequentialAgent orchestration** addresses the repetitive nature of MCQ development by automating the deterministic pipeline. The workflow—from source ingestion through fact extraction, knowledge base management, MCQ generation, and visual refinement—follows a predictable sequence where each step builds on the previous. Agents excel at this: they maintain context across steps, handle data handoff via structured `output_key` parameters, and ensure provenance is preserved throughout the pipeline. What would take a human 30 minutes of repetitive clicking, copying, and pasting between different tools becomes an automated flow where agents coordinate the entire process.

**Custom Loop refinement** solves a different challenge: quality coordination between different LLM instances. Our system uses Gemini as a specialized critic to review MCQ quality, then coordinates with the user's chosen LLM (Gemini or ChatGPT) to refine the question based on critique. This multi-LLM coordination—where different models play different roles—is precisely what agents handle well. The loop pattern allows iterative improvement (limited to 2 iterations for simplicity) with explicit error handling, something that would be cumbersome to manage manually through direct API calls.

The **Google ADK framework** simplifies agent development significantly. Without a framework, we'd need to build session management, context compaction, tool integration, and error handling from scratch. ADK provides DatabaseSessionService for persistent state, EventsCompactionConfig for efficient token usage, and built-in tools like Google Search. More importantly, agents help **store reasoning triplets and cite sources automatically**—tasks that are easy for humans conceptually but time-consuming in practice. Medical MCQ writers are health professionals, not software engineers; they need tools that handle the technical complexity while they focus on medical accuracy.

Agents transform MCQ development from a series of manual, repetitive steps into an orchestrated workflow where the framework handles coordination, state management, and provenance tracking, allowing medical professionals to focus on what they do best: ensuring clinical accuracy and educational value.

---

## What You Created

We built a production-ready system that generates verifiable medical MCQs with complete provenance tracking, using a hybrid architecture that combines Google ADK agent orchestration with direct API calls for optimal performance and flexibility.

### Architecture Overview

The system consists of three main components accessible through a Gradio web interface:

**Tab 1: Source Intake** - Users search PubMed by keywords or upload PDF documents. PubMed articles are displayed with titles, authors, and publication years. PDF uploads are automatically parsed and chunked by section (Abstract, Methods, Results, Discussion, Conclusion), with each section treated as a separate source for focused MCQ generation. Selected sources are added to a pending queue without triggering any LLM calls—giving users full control over when processing begins.

**Tab 2: MCQ Builder** - The core generation interface where users select a pending source and choose their preferred LLM (Gemini 2.5 Flash Lite or ChatGPT 4o mini). With a single click, the system generates a complete MCQ package: a 5-option multiple-choice question with stem, supporting SNOMED-CT style knowledge triplets (Subject-Action-Object-Relation), and an optimized visual prompt. Users can provide natural-language feedback to refine questions through our custom loop refinement process, which uses Gemini as a critic and their chosen LLM as a refiner. Once satisfied, users accept the MCQ, which persists to the knowledge base along with all provenance metadata.

**Tab 3: Knowledge Base** - A searchable repository of all approved MCQs with pagination, detailed views showing complete provenance trails, and export functionality. Every MCQ displays its source article (PubMed ID or PDF filename), associated triplets with context sentences, visual prompts, and generated images.

### Key Technical Components

The system implements **6 Google ADK framework features**:

1. **SequentialAgent Orchestration** - A pipeline of 6 specialized agents (SourceIngestionAgent → FactExtractionAgent → KBManagementAgent → MCQGenerationAgent → VisualRefinerAgent → ZeroTripletFallbackAgent) that process sources through automated workflows. See "Project pipeline" diagram in media gallery.

2. **Custom Loop for MCQ Refinement** - An iterative critique-refine pattern inspired by ADK LoopAgent, where Gemini critiques MCQ quality and the user's chosen LLM refines based on feedback. See "Loop Critique Agent" diagram in media gallery.

3. **DatabaseSessionService** - Persistent session management ensuring work survives app restarts.

4. **Context Compaction** - Automatic conversation history management for efficient token usage.

5. **Custom Tools** - Five specialized tools for schema validation, knowledge base operations, provenance verification, PubMed integration, and web search.

6. **Built-in Tools** - Google Search integration for finding medically plausible distractors.

The architecture diagram (available in media gallery) shows the layered structure: Gradio UI → Agent Pipeline → Tools → Services → Database, demonstrating how agents orchestrate the entire workflow while maintaining provenance at every step.

---

## Demo

The system demonstrates a complete workflow from literature search to verified MCQ generation. Users begin by searching PubMed—for example, entering "rivaroxaban coronary artery disease" returns relevant articles. Selecting an article adds it to the pending queue, where it awaits processing.

In the MCQ Builder tab, selecting the pending article and clicking "Generate MCQ Draft" triggers the generation process. Within seconds, the system returns a complete MCQ with five options, a correct answer index, supporting knowledge triplets showing the reasoning path (e.g., "Rivaroxaban → inhibits → Factor Xa"), and an optimized visual prompt. The triplets include verbatim context sentences from the source article, providing immediate provenance verification.

Users can then provide feedback like "make the question more clinical" or "simplify the stem," which triggers our Loop Critique Agent. Gemini analyzes the current MCQ and user feedback, providing specific critique. The user's chosen LLM then refines the MCQ based on this critique, iterating up to two times for optimal quality.

The visual prompt can be edited before acceptance, and users can generate accompanying images using either Gemini Imagen or DALL-E. Once satisfied, accepting the MCQ saves it to the knowledge base with complete provenance: source article metadata, triplets with context sentences, visual prompt, and image path.

The Knowledge Base tab provides search functionality across all approved MCQs, allowing educators to find questions by PMID, title, authors, or question text. Each MCQ displays its complete provenance trail, enabling reviewers to verify that questions are grounded in published literature—a critical requirement for medical education.

The project file structure (available in media gallery) shows the organized codebase, while the architecture diagram illustrates how agents coordinate the workflow. The system successfully balances automation with human oversight, ensuring efficiency gains without sacrificing accuracy or verifiability.

---

## The Build

We developed this system to address a specific product requirement: **provenance verification for medical MCQ generation**. This requirement emerged from the critical need to safely leverage modern LLMs in medical education while maintaining the trust and accuracy essential for training future physicians.

### Why PubMed?

PubMed, maintained by the National Center for Biotechnology Information (NCBI), is the world's largest and most authoritative database of medical literature, containing over 35 million peer-reviewed citations. By integrating directly with PubMed's API, we ensure that every MCQ can be traced back to peer-reviewed, published research, providing the credibility and verifiability that medical education demands.

### Addressing Diversity Through Automation

A key insight driving our development was recognizing that **automating critique, image generation, and MCQ creation helps recruit more medical specialists as question writers**. The traditional 30-minute-per-question barrier means a smaller pool of dedicated educators can contribute. By reducing this to minutes and handling the technical complexity (provenance tracking, triplet extraction, image generation), we lower the barrier to entry. More specialists can contribute, leading to greater **diversity of writers** and, by extension, **diversity of questions** covering a broader range of medical topics, clinical scenarios, and educational perspectives.

### Technology Stack

We built the system using **Python** as the core programming language, **Google Agent Development Kit (ADK)** as the orchestration framework, **Gradio** for the interactive web interface, and **Google Gemini** as the primary LLM for both text generation and image creation (via Gemini Imagen). The ADK framework provides SequentialAgent for pipeline orchestration, DatabaseSessionService for persistence, and context compaction for efficiency. Gemini's capabilities in medical reasoning and structured output generation make it ideal for extracting knowledge triplets and generating clinically accurate MCQs. Gradio enables rapid development of the human-in-the-loop interface, allowing medical professionals to interact with the system through an intuitive web-based UI.

The framework and models work together to enable efficient question generation: agents handle the orchestration and state management, while Gemini processes the medical literature and generates questions. The hybrid architecture—using SequentialAgent for automated workflows and direct API calls for on-demand generation—provides both automation and flexibility.

### Human-in-the-Loop Design

Throughout development, we maintained **human-in-the-loop** as a core principle. No MCQ is saved to the knowledge base without explicit human approval. Users review triplets, edit visual prompts, provide feedback for refinement, and make the final acceptance decision. This design ensures that medical professionals remain in control, using agents as powerful assistants rather than autonomous generators. The system augments human expertise rather than replacing it.

### Implementation Challenges

Key technical challenges included multi-LLM routing (supporting both Gemini and ChatGPT), PDF section parsing for medical papers, error handling with graceful fallbacks, and session persistence across app restarts. The ADK framework simplified many of these challenges, particularly session management and context compaction, allowing us to focus on the core innovation: provenance-first MCQ generation.

---

## If I Had More Time, This Is What I'd Do

Given more time, I would focus on three critical enhancements that would significantly improve the system's capabilities and impact.

### Enhanced UI and State Management

The current Gradio interface, while functional, could better handle complex state management for multi-step workflows. A redesigned UI would provide real-time progress indicators for the SequentialAgent pipeline, better visualization of the refinement loop iterations, and improved handling of concurrent MCQ generation tasks. 

### Deep Triplet Reasoning for Higher Quality MCQs

The most impactful enhancement would be leveraging triplet reasoning for **deep semantic search** across the knowledge base. Currently, triplets are used for provenance verification, but they represent a rich knowledge graph that could power advanced features. By analyzing relationships between triplets (e.g., "Drug A treats Condition B" connected to "Condition B causes Symptom C"), the system could generate more sophisticated MCQs that test higher-order clinical reasoning. This would enable questions that require students to connect multiple concepts, mirroring real-world clinical decision-making.

### Clinical Scenario Generation for OSCE-Style Assessment

A transformative addition would be generating **clinical scenarios with verbal answer requirements** for clinical management questions. This would replicate **OSCE (Objective Structured Clinical Examination)** testing formats, where medical candidates demonstrate clinical skills through structured scenarios. The system could use triplets to generate realistic patient presentations, and LLMs could create follow-up questions requiring students to explain their clinical reasoning verbally. This addresses a critical gap: while multiple-choice questions test knowledge recall, OSCE-style scenarios assess application and clinical judgment.

The National Board of Medical Examiners (NBME) has recognized the importance of innovative assessment methods, as evidenced by their research on assessment for learning in medical education ([NBME Assessment for Learning Webinar](https://www.nbme.org/events/webinars/assessment-for-learning)). Our system's provenance-first approach and triplet-based reasoning could contribute to this evolving field by generating verifiable, evidence-based clinical scenarios.

### Additional Future Aspirations

Beyond these priorities, I would explore **collaborative question authoring** features where multiple medical specialists could contribute to a single MCQ, each bringing their expertise to different aspects (clinical scenario, distractors, visual prompt). This would further enhance diversity while maintaining provenance. 

The foundation we've built—with provenance tracking, agent orchestration, and human-in-the-loop design—provides a solid platform for these enhancements, each building on the core innovation of verifiable, evidence-based MCQ generation.

---

*Word count: ~1,480 words*

