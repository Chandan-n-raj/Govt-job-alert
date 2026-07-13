from __future__ import annotations

from unittest.mock import patch

import pytest
import requests
from bs4 import BeautifulSoup

from scrapers.base import BaseScraper, ScrapeResult
from scrapers.official_sites import OfficialSiteScraper, build_notification_from_raw, collect_relevant_notifications


class DummyScraper(BaseScraper):
    def extract_notifications(self, soup: BeautifulSoup):
        return [{"organization": self.organization, "post_name": soup.title.text if soup.title else "No title"}]


def test_base_scraper_parse_returns_notifications_on_success() -> None:
    scraper = DummyScraper("RBI", "https://example.com")
    with patch("scrapers.base.requests.get") as get_mock:
        get_mock.return_value.raise_for_status.return_value = None
        get_mock.return_value.text = "<html><head><title>Test</title></head><body></body></html>"
        result = scraper.parse()

    assert result.success is True
    assert result.notifications[0]["post_name"] == "Test"


def test_base_scraper_parse_handles_request_failure() -> None:
    scraper = DummyScraper("RBI", "https://example.com")
    with patch("scrapers.base.requests.get", side_effect=requests.Timeout("boom")):
        result = scraper.parse()

    assert result.success is False
    assert result.error is not None


def test_base_scraper_fetch_html_retries_and_succeeds() -> None:
    scraper = DummyScraper("RBI", "https://example.com")
    with patch("scrapers.base.requests.get", side_effect=[requests.Timeout("bad"), type("Resp", (), {"raise_for_status": lambda self: None, "text": "<html></html>"})()]) as get_mock, patch("scrapers.base.time.sleep") as sleep_mock:
        html = scraper.fetch_html()

    assert html == "<html></html>"
    assert get_mock.call_count == 2
    sleep_mock.assert_called_once()


def test_base_scraper_fetch_html_raises_after_retries() -> None:
    scraper = DummyScraper("RBI", "https://example.com")
    with patch("scrapers.base.requests.get", side_effect=requests.Timeout("bad")) as get_mock, patch("scrapers.base.time.sleep") as sleep_mock:
        with pytest.raises(RuntimeError):
            scraper.fetch_html()

    assert get_mock.call_count == 3
    assert sleep_mock.call_count == 2


def test_official_scraper_extracts_candidate_links() -> None:
    scraper = OfficialSiteScraper("RBI", "https://example.com")
    soup = BeautifulSoup("<html><body><a href='/recruitment'>Recruitment for Officer posts</a></body></html>", "lxml")
    notifications = scraper.extract_notifications(soup)

    assert len(notifications) == 1
    assert notifications[0]["organization"] == "RBI"


def test_collect_relevant_notifications_filters_entries() -> None:
    raw_notifications = [
        {"organization": "RBI", "post_name": "Recruitment for Officer posts", "apply_link": "https://example.com/apply"},
        {"organization": "SBI", "post_name": "Consultant Recruitment", "apply_link": "https://example.com/consultant"},
    ]

    notifications = collect_relevant_notifications(raw_notifications)
    assert len(notifications) == 1
    assert notifications[0].post_name == "Recruitment for Officer posts"


def test_build_notification_from_raw_sets_all_fields() -> None:
    notification = build_notification_from_raw({"organization": "RBI", "post_name": "Officer", "vacancies": "10", "official_pdf": "a.pdf", "apply_link": "b", "source_url": "c"})
    assert notification.organization == "RBI"
    assert notification.vacancies == "10"
    assert notification.official_pdf == "a.pdf"
