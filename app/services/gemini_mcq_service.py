"""Gemini-based MCQ generation helpers used by the Gradio UI."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from google import genai


_GEMINI_MODEL = os.getenv("GEMINI_MODEL", "models/gemini-2.0-flash")


@dataclass
class GeminiResult:
    success: bool
    message: str
    payload: Dict[str, Any] | None = None


def _get_client() -> genai.Client:
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY is not set. Please update the .env file.")
    return genai.Client(api_key=api_key)


def _coerce_json_from_response(response: genai.types.GenerateContentResponse) -> Dict[str, Any]:
    """Extract JSON text from Gemini response and parse it."""
    raw_text = response.text if hasattr(response, "text") else response.output_text
    raw_text = raw_text.strip()
    # Strip code fences if Gemini wrapped the JSON
    if raw_text.startswith("```"):
        raw_text = raw_text.strip("`")
        # remove optional language hint
        if raw_text.startswith("json"):
            raw_text = raw_text[4:].strip()
    return json.loads(raw_text)


def _build_mcq_prompt(article_title: str, article_text: str) -> str:
    return f"""
You are a medical MCQ author. Using the article below, produce:
1. A single multiple-choice question (5 options, exactly one correct).
2. At least one SNOMED-style relation triplet describing the knowledge assessed.
3. An optimized visual prompt describing an illustration that matches the scenario.

Return STRICT JSON with this schema:
{{
  "mcq": {{
    "stem": "...",
    "question": "...",
    "options": ["A", "B", "C", "D", "E"],
    "correct_option": 0   // index 0-4
  }},
  "triplets": [
    {{
      "subject": "...",
      "action": "...",
      "object": "...",
      "relation": "SNOMED-like verb"
    }}
  ],
  "visual_prompt": "text describing the desired medical illustration"
}}

Rules:
- Options must be medically plausible.
- Triplets must reflect TRUE statements from the article (at least one triplet).
- visual_prompt should be concise (<= 80 words).
- DO NOT add commentary outside the JSON.

Article title: {article_title}

Article content:
\"\"\"{article_text[:8000]}\"\"\"  // truncated if extremely long
""".strip()


def generate_mcq_with_triplets(article: Dict[str, Any]) -> GeminiResult:
    """Generate MCQ + triplets + visual prompt for the provided article."""
    try:
        client = _get_client()
        prompt = _build_mcq_prompt(article.get("title") or article.get("source_id", "Article"), article.get("content", ""))
        response = client.models.generate_content(
            model=_GEMINI_MODEL,
            contents=[
                {
                    "role": "user",
                    "parts": [{"text": prompt}],
                }
            ],
        )
        payload = _coerce_json_from_response(response)
        return GeminiResult(True, "MCQ generated", payload)
    except Exception as exc:  # pragma: no cover - logging handled upstream
        return GeminiResult(False, f"Gemini MCQ generation failed: {exc}", None)


def regenerate_mcq_with_feedback(article: Dict[str, Any], previous_payload: Dict[str, Any], feedback: str) -> GeminiResult:
    """Regenerate MCQ using reviewer feedback."""
    try:
        client = _get_client()
        prompt = f"""
The reviewer provided feedback for an MCQ. Return updated JSON with the same schema as before.

Feedback:
{feedback}

Previous response JSON:
{json.dumps(previous_payload, ensure_ascii=False)}

Article title: {article.get("title")}
Article snippet:
\"\"\"{article.get("content", "")[:6000]}\"\"\"
"""
        response = client.models.generate_content(
            model=_GEMINI_MODEL,
            contents=[{"role": "user", "parts": [{"text": prompt}]}],
        )
        payload = _coerce_json_from_response(response)
        return GeminiResult(True, "MCQ regenerated", payload)
    except Exception as exc:  # pragma: no cover
        return GeminiResult(False, f"Gemini MCQ regeneration failed: {exc}", None)

