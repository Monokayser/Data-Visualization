from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class AISettings:
    api_key: str
    model: str
    base_url: str
    timeout_seconds: int
    site_url: str
    site_name: str

    @property
    def enabled(self) -> bool:
        return bool(self.api_key.strip())


def load_ai_settings() -> AISettings:
    load_dotenv()
    return AISettings(
        api_key=os.getenv("OPENROUTER_API_KEY", "").strip(),
        model=os.getenv("OPENROUTER_MODEL", "openrouter/free").strip() or "openrouter/free",
        base_url=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1/chat/completions").strip(),
        timeout_seconds=int(os.getenv("AI_TIMEOUT_SECONDS", "30")),
        site_url=os.getenv("APP_SITE_URL", "https://github.com/Monokayser/Data-Visualization").strip(),
        site_name=os.getenv("APP_SITE_NAME", "Data Visualization Dashboard").strip(),
    )

