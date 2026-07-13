from __future__ import annotations

from typing import Any

from bs4 import BeautifulSoup

from filters.job_filter import Notification, is_relevant_notification
from .base import BaseScraper


class OfficialSiteScraper(BaseScraper):
    """A scraper that extracts officer-level recruitment links from official pages."""

    _excluded_terms = (
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
    _recruitment_signals = ("recruitment", "vacancy", "vacancies", "notification", "apply", "recruit")
    _url_signals = ("recruit", "vacancy", "career", "job", "notification")
    _entry_level_terms = (
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

    def extract_notifications(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        """Extract recruitment-like links from parsed HTML."""
        notifications: list[dict[str, Any]] = []
        for link in soup.find_all("a", href=True):
            text = " ".join(link.get_text(" ", strip=True).split())
            href = link["href"]
            if not text:
                continue
            if self._looks_like_recruitment(text, href):
                notifications.append(
                    {
                        "organization": self.organization,
                        "post_name": text,
                        "official_pdf": href if href.lower().endswith(".pdf") else None,
                        "apply_link": href,
                        "source_url": self.url,
                    }
                )
        return notifications

    def _looks_like_recruitment(self, text: str, href: str) -> bool:
        lowered_text = text.lower()
        lowered_href = href.lower()
        if any(term in lowered_text for term in self._excluded_terms):
            return False

        url_has_recruitment_signal = any(term in lowered_href for term in self._url_signals)
        text_has_recruitment_signal = any(term in lowered_text for term in self._recruitment_signals)
        text_has_entry_level_signal = any(term in lowered_text for term in self._entry_level_terms)
        return (text_has_recruitment_signal or url_has_recruitment_signal) and text_has_entry_level_signal


def build_notification_from_raw(raw: dict[str, Any]) -> Notification:
    """Create a Notification object from raw scraped data."""
    return Notification(
        organization=raw.get("organization", ""),
        post_name=raw.get("post_name", ""),
        vacancies=raw.get("vacancies"),
        official_pdf=raw.get("official_pdf"),
        apply_link=raw.get("apply_link"),
        application_start_date=raw.get("application_start_date"),
        application_end_date=raw.get("application_end_date"),
        exam_date=raw.get("exam_date"),
        educational_qualification=raw.get("educational_qualification"),
        age_limit=raw.get("age_limit"),
        selection_process=raw.get("selection_process"),
        source_url=raw.get("source_url"),
    )


def collect_relevant_notifications(raw_notifications: list[dict[str, Any]]) -> list[Notification]:
    """Filter raw notifications down to relevance-accepted entries."""
    return [
        notification
        for raw in raw_notifications
        if is_relevant_notification(notification := build_notification_from_raw(raw))
    ]
