"""Shared Gemini API helpers: call with retry + clean JSON parsing."""
import json
import re
import logging
import time

from google import genai

from app.config import settings
from app.services.rate_limiter import gemini_limiter

logger = logging.getLogger(__name__)

_client: genai.Client | None = None


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(api_key=settings.gemini_api_key)
    return _client


def _clean_json(text: str) -> str:
    """Strip markdown code fences and leading/trailing whitespace."""
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


def call_gemini(prompt: str, max_retries: int = 2) -> dict:
    """Call Gemini and return parsed JSON dict. Retries on parse failure."""
    client = _get_client()

    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            gemini_limiter.wait()
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
            )
            cleaned = _clean_json(response.text)
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            last_error = e
            logger.warning(
                "Gemini returned invalid JSON (attempt %d/%d): %s",
                attempt, max_retries, str(e)[:100],
            )
            if attempt < max_retries:
                time.sleep(2)
        except Exception as e:
            last_error = e
            logger.error("Gemini API error (attempt %d/%d): %s", attempt, max_retries, e)
            if attempt < max_retries:
                time.sleep(2)

    raise RuntimeError(f"Gemini failed after {max_retries} attempts: {last_error}")
