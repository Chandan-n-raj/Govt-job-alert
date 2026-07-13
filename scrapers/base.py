from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Any

import requests
from bs4 import BeautifulSoup

from config import DEFAULT_SETTINGS

logger = logging.getLogger(__name__)


@dataclass
class ScrapeResult:
    """Container for one website scrape attempt."""

    organization: str
    url: str
    success: bool
    notifications: list[dict[str, Any]]
    error: str | None = None


class BaseScraper:
    """Base class with retry logic for scraping official recruitment pages."""

    def __init__(self, organization: str, url: str) -> None:
        self.organization = organization
        self.url = url

    def fetch_html(self) -> str:
        headers = {"User-Agent": DEFAULT_SETTINGS.user_agent}
        last_error: Exception | None = None
        for attempt in range(1, DEFAULT_SETTINGS.max_retries + 1):
            try:
                response = requests.get(
                    self.url,
                    headers=headers,
                    timeout=DEFAULT_SETTINGS.request_timeout_seconds,
                )
                response.raise_for_status()
                return response.text
            except requests.RequestException as exc:
                logger.warning("Request failed for %s (attempt %s/%s): %s", self.organization, attempt, DEFAULT_SETTINGS.max_retries, exc)
                last_error = exc
                if attempt < DEFAULT_SETTINGS.max_retries:
                    time.sleep(DEFAULT_SETTINGS.sleep_between_retries_seconds)
                    continue
        raise RuntimeError(f"Failed to fetch {self.url}: {last_error}") from last_error

    def parse(self) -> ScrapeResult:
        try:
            html = self.fetch_html()
            soup = BeautifulSoup(html, "lxml")
            notifications = self.extract_notifications(soup)
            return ScrapeResult(self.organization, self.url, True, notifications)
        except Exception as exc:  # pragma: no cover - defensive path
            logger.exception("Scrape failed for %s", self.organization)
            return ScrapeResult(self.organization, self.url, False, [], str(exc))

    def extract_notifications(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        raise NotImplementedError
