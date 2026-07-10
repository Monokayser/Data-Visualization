from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Any

import requests

from .config import AISettings
from .prompts import SYSTEM_PROMPT, build_user_prompt

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AIResult:
    ok: bool
    message: str
    error_type: str | None = None


def ask_ai(question: str, context: str, settings: AISettings, retries: int = 1) -> AIResult:
    if not question.strip():
        return AIResult(False, "Please enter a question before sending.", "empty_question")
    if not settings.enabled:
        return AIResult(
            False,
            "AI assistant is not configured yet. Add OPENROUTER_API_KEY in your local .env file or deployment secrets to enable API-based answers.",
            "missing_api_key",
        )

    payload: dict[str, Any] = {
        "model": settings.model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_user_prompt(question, context)},
        ],
        "temperature": 0.2,
        "max_tokens": 650,
    }
    headers = {
        "Authorization": f"Bearer {settings.api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": settings.site_url,
        "X-OpenRouter-Title": settings.site_name,
    }

    last_error = "Unknown AI API error."
    for attempt in range(retries + 1):
        try:
            response = requests.post(
                settings.base_url,
                headers=headers,
                json=payload,
                timeout=settings.timeout_seconds,
            )
            if response.status_code == 401:
                return AIResult(False, "AI API key is invalid or unauthorized. Please update deployment secrets.", "invalid_api_key")
            if response.status_code == 429:
                return AIResult(False, "AI service rate limit reached. Please wait and try again later.", "rate_limit")
            if response.status_code >= 500:
                last_error = "AI provider is temporarily unavailable."
                raise requests.HTTPError(last_error)
            response.raise_for_status()
            data = response.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            if not content:
                return AIResult(False, "AI service returned an empty response.", "empty_response")
            return AIResult(True, content.strip())
        except requests.Timeout:
            last_error = "AI request timed out. Please try a shorter question or retry later."
            logger.warning("AI request timeout on attempt %s", attempt + 1)
        except requests.RequestException as exc:
            last_error = "AI request failed. Please check the API configuration or try again later."
            logger.warning("AI request failed on attempt %s: %s", attempt + 1, exc)
        if attempt < retries:
            time.sleep(1.5)
    return AIResult(False, last_error, "request_failed")

