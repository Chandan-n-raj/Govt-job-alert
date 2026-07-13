from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Notification:
    """Represents a recruitment notification extracted from a website."""

    organization: str
    post_name: str
    vacancies: str | None = None
    official_pdf: str | None = None
    apply_link: str | None = None
    application_start_date: str | None = None
    application_end_date: str | None = None
    exam_date: str | None = None
    educational_qualification: str | None = None
    age_limit: str | None = None
    selection_process: str | None = None
    source_url: str | None = None

    def notification_id(self) -> str:
        """Return a stable identifier for the notification."""
        return f"{self.organization.lower()}::{self.post_name.lower()}"


RELEVANT_TITLES = (
    "grade a",
    "grade b",
    "assistant manager",
    "management trainee",
    "executive trainee",
    "officer",
    "administrative officer",
    "assistant administrative officer",
    "it officer",
    "finance officer",
    "hr officer",
    "law officer",
    "engineer officer",
    "technical officer",
    "scientific officer",
    "scientist engineer",
)

EXCLUDED_TERMS = (
    "consultant",
    "contract",
    "apprentice",
    "internship",
    "temporary",
    "experienced",
    "lateral",
    "senior manager",
    "deputy general manager",
    "general manager",
)
RECRUITMENT_TERMS = ("recruitment", "vacancy", "vacancies", "notification", "apply", "recruit", "career")


def is_relevant_notification(notification: Notification) -> bool:
    """Return True when the parsed notification looks like an entry-level officer role."""
    haystack = f"{notification.post_name} {notification.organization}".lower()
    if not haystack.strip():
        return False
    if any(term in haystack for term in EXCLUDED_TERMS):
        return False
    if not any(term in haystack for term in RECRUITMENT_TERMS):
        return False

    return any(title in haystack for title in RELEVANT_TITLES)


def normalize_text(value: str | None) -> str | None:
    """Collapse whitespace and trim a string value."""
    if value is None:
        return None
    cleaned = re.sub(r"\s+", " ", value).strip()
    return cleaned or None
