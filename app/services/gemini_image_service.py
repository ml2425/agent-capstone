"""Gemini-based image generation helper."""
from __future__ import annotations

import base64
import os
from dataclasses import dataclass
from typing import Optional

from google import genai

DEFAULT_IMAGE_SIZE = os.getenv("GEMINI_IMAGE_DEFAULT_SIZE", "300x300")
IMAGE_MODEL = os.getenv("GEMINI_IMAGE_MODEL", "imagen-3.0-generate")


@dataclass
class GeminiImageResult:
    success: bool
    message: str
    image_bytes: Optional[bytes] = None
    size_used: Optional[str] = None


def _get_client() -> genai.Client:
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY is not set. Please update the .env file.")
    return genai.Client(api_key=api_key)


def generate_image_from_prompt(prompt: str, size: Optional[str] = None) -> GeminiImageResult:
    """Generate an image using Gemini Imagen API."""
    prompt = (prompt or "").strip()
    if not prompt:
        return GeminiImageResult(False, "Provide a visual prompt before generating.", None)

    resolved_size = (size or DEFAULT_IMAGE_SIZE or "").strip() or "300x300"

    try:
        client = _get_client()
        response = client.models.generate_images(
            model=IMAGE_MODEL,
            prompt=prompt,
            image_generation_config={"size": resolved_size},
        )
        images = getattr(response, "images", None) or getattr(response, "generated_images", None)
        if not images:
            return GeminiImageResult(False, "Gemini did not return image data.", None)

        first = images[0]
        encoded = getattr(first, "image_base64", None) or getattr(first, "bytes_base64", None)
        if not encoded:
            return GeminiImageResult(False, "Gemini returned empty image payload.", None)

        image_bytes = base64.b64decode(encoded)
        return GeminiImageResult(True, "Image generated successfully.", image_bytes, resolved_size)
    except Exception as exc:  # pragma: no cover - relies on external service
        return GeminiImageResult(False, f"Gemini image generation failed: {exc}", None)


