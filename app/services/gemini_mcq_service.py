"""MCQ generation helpers supporting both Gemini and OpenAI (ChatGPT)."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from google import genai
from openai import OpenAI


_GEMINI_MODEL = os.getenv("GEMINI_MODEL", "models/gemini-2.0-flash")


@dataclass
class GeminiResult:
    success: bool
    message: str
    payload: Dict[str, Any] | None = None


def _get_gemini_client() -> genai.Client:
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY is not set. Please update the .env file.")
    return genai.Client(api_key=api_key)


def _get_openai_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set. Please update the .env file.")
    return OpenAI(api_key=api_key)


def _extract_json_from_response(response: Any, provider: str) -> Dict[str, Any]:
    """Universal JSON extractor for both Gemini and OpenAI responses."""
    if provider == "gemini":
        # Gemini format: response.text or response.output_text
        raw_text = response.text if hasattr(response, "text") else response.output_text
    else:  # openai
        # OpenAI format: response.choices[0].message.content
        raw_text = response.choices[0].message.content or ""
    
    raw_text = raw_text.strip()
    # Strip code fences if wrapped
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


def generate_mcq_with_triplets(article: Dict[str, Any], model_id: Optional[str] = None) -> GeminiResult:
    """Generate MCQ + triplets + visual prompt for the provided article.
    
    Args:
        article: Article data with title and content
        model_id: Optional model identifier. If contains "chatgpt" or "openai", uses OpenAI API.
                  Otherwise uses Gemini (default).
    """
    try:
        prompt = _build_mcq_prompt(article.get("title") or article.get("source_id", "Article"), article.get("content", ""))
        
        # Route to OpenAI if ChatGPT selected, otherwise use Gemini
        if model_id and ("chatgpt" in model_id.lower() or "openai" in model_id.lower()):
            # OpenAI API with JSON mode
            client = _get_openai_client()
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a medical MCQ author. Return only valid JSON, no commentary."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.7,
            )
            payload = _extract_json_from_response(response, "openai")
            return GeminiResult(True, "MCQ generated (ChatGPT)", payload)
        else:
            # Gemini API (default)
            client = _get_gemini_client()
            response = client.models.generate_content(
                model=_GEMINI_MODEL,
                contents=[
                    {
                        "role": "user",
                        "parts": [{"text": prompt}],
                    }
                ],
            )
            payload = _extract_json_from_response(response, "gemini")
            return GeminiResult(True, "MCQ generated (Gemini)", payload)
    except Exception as exc:  # pragma: no cover - logging handled upstream
        provider = "ChatGPT" if (model_id and ("chatgpt" in model_id.lower() or "openai" in model_id.lower())) else "Gemini"
        return GeminiResult(False, f"{provider} MCQ generation failed: {exc}", None)


def regenerate_mcq_with_feedback(article: Dict[str, Any], previous_payload: Dict[str, Any], feedback: str, model_id: Optional[str] = None) -> GeminiResult:
    """Regenerate MCQ using reviewer feedback.
    
    Args:
        article: Article data with title and content
        previous_payload: Previous MCQ JSON payload
        feedback: Reviewer feedback text
        model_id: Optional model identifier. If contains "chatgpt" or "openai", uses OpenAI API.
                  Otherwise uses Gemini (default).
    """
    try:
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
        
        # Route to OpenAI if ChatGPT selected, otherwise use Gemini
        if model_id and ("chatgpt" in model_id.lower() or "openai" in model_id.lower()):
            # OpenAI API with JSON mode
            client = _get_openai_client()
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a medical MCQ author. Return only valid JSON, no commentary."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.7,
            )
            payload = _extract_json_from_response(response, "openai")
            return GeminiResult(True, "MCQ regenerated (ChatGPT)", payload)
        else:
            # Gemini API (default)
            client = _get_gemini_client()
            response = client.models.generate_content(
                model=_GEMINI_MODEL,
                contents=[{"role": "user", "parts": [{"text": prompt}]}],
            )
            payload = _extract_json_from_response(response, "gemini")
            return GeminiResult(True, "MCQ regenerated (Gemini)", payload)
    except Exception as exc:  # pragma: no cover
        provider = "ChatGPT" if (model_id and ("chatgpt" in model_id.lower() or "openai" in model_id.lower())) else "Gemini"
        return GeminiResult(False, f"{provider} MCQ regeneration failed: {exc}", None)

