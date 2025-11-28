"""Gemini-based image generation helper."""
from __future__ import annotations

import base64
import os
from dataclasses import dataclass
from io import BytesIO
from math import gcd
from typing import Optional, Tuple

from google import genai
from google.genai import types
from PIL import Image

DEFAULT_IMAGE_SIZE = os.getenv("GEMINI_IMAGE_DEFAULT_SIZE", "512x512")
IMAGE_MODEL = os.getenv("GEMINI_IMAGE_MODEL", "gemini-2.5-flash-image")


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


def _parse_size_to_image_config(size_value: str) -> Tuple[types.ImageConfig, Optional[Tuple[int, int]]]:
    """Coerce user-provided size into an aspect ratio; keep dims for local resizing."""
    normalized = (size_value or "").strip() or DEFAULT_IMAGE_SIZE or "512x512"
    normalized = normalized.lower()

    if "x" in normalized:
        width_str, height_str = normalized.split("x", 1)
        try:
            width = max(32, min(2048, int(width_str)))
            height = max(32, min(2048, int(height_str)))
            divisor = gcd(width, height) or 1
            ratio = f"{width // divisor}:{height // divisor}"
            return types.ImageConfig(aspect_ratio=ratio), (width, height)
        except ValueError:
            return types.ImageConfig(aspect_ratio="1:1"), None

    if ":" in normalized:
        return types.ImageConfig(aspect_ratio=normalized), None

    return types.ImageConfig(aspect_ratio="1:1"), None


def _extract_image_bytes(response) -> Optional[bytes]:
    """Safely pull inline image bytes from a Gemini response."""
    if not response:
        return None

    candidate_sequences = []
    parts_attr = getattr(response, "parts", None)
    if parts_attr:
        candidate_sequences.append(parts_attr)

    candidates = getattr(response, "candidates", None)
    if candidates:
        for candidate in candidates:
            if getattr(candidate, "content", None) and getattr(candidate.content, "parts", None):
                candidate_sequences.append(candidate.content.parts)
            elif getattr(candidate, "parts", None):
                candidate_sequences.append(candidate.parts)

    for sequence in candidate_sequences:
        for part in sequence:
            inline_data = getattr(part, "inline_data", None)
            if inline_data and getattr(inline_data, "data", None):
                data = inline_data.data
                if isinstance(data, bytes):
                    return data
                if isinstance(data, str):
                    try:
                        return base64.b64decode(data)
                    except Exception:
                        return data.encode("utf-8")
    return None


def generate_image_from_prompt(prompt: str, size: Optional[str] = None) -> GeminiImageResult:
    """Generate an image using Gemini's dedicated image model."""
    prompt = (prompt or "").strip()
    if not prompt:
        return GeminiImageResult(False, "Provide a visual prompt before generating.", None)

    resolved_size = (size or DEFAULT_IMAGE_SIZE or "").strip() or "300x300"

    try:
        client = _get_client()
        image_config, resize_dims = _parse_size_to_image_config(resolved_size)
        response = client.models.generate_content(
            model=IMAGE_MODEL,
            contents=[{"role": "user", "parts": [{"text": prompt}]}],
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"],
                image_config=image_config,
            ),
        )
        image_bytes = _extract_image_bytes(response)
        if not image_bytes:
            return GeminiImageResult(False, "Gemini did not return image data.", None)

        if resize_dims:
            try:
                pil_image = Image.open(BytesIO(image_bytes))
                pil_image = pil_image.convert("RGBA")
                pil_image = pil_image.resize(resize_dims, Image.LANCZOS)
                buffer = BytesIO()
                # Default to PNG for consistency
                pil_image.save(buffer, format="PNG")
                image_bytes = buffer.getvalue()
            except Exception:
                # Fall back to original bytes if resizing fails
                pass

        return GeminiImageResult(True, "Image generated successfully.", image_bytes, resolved_size)
    except Exception as exc:  # pragma: no cover - relies on external service
        return GeminiImageResult(False, f"Gemini image generation failed: {exc}", None)
