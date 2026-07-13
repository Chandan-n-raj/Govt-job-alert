from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Final


@dataclass(frozen=True)
class Settings:
    """Runtime configuration for the job monitor."""

    repo_root: str = os.path.abspath(os.path.dirname(__file__))
    notifications_file: str = os.path.join(os.path.abspath(os.path.dirname(__file__)), "notifications.json")
    request_timeout_seconds: int = 20
    max_retries: int = 3
    sleep_between_retries_seconds: float = 1.5
    user_agent: str = "govt-job-monitor/1.0 (+https://example.com)"
    email_from: str = os.getenv("EMAIL_FROM", "")
    email_to: str = os.getenv("EMAIL_TO", "")
    smtp_host: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    smtp_username: str = os.getenv("SMTP_USERNAME", "")
    smtp_password: str = os.getenv("SMTP_PASSWORD", "")
    smtp_use_tls: bool = os.getenv("SMTP_USE_TLS", "true").lower() == "true"


DEFAULT_SETTINGS: Final[Settings] = Settings()
