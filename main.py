from __future__ import annotations

import logging
import sys

from config import DEFAULT_SETTINGS
from database import NotificationStore
from email_sender import send_notifications
from filters.job_filter import Notification
from scrapers.official_sites import OfficialSiteScraper, collect_relevant_notifications
from scrapers.registry import ORGANIZATION_SITES

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def collect_new_notifications(
    notifications: list[Notification],
    store: NotificationStore,
) -> list[Notification]:
    """Return notifications that are new for this run and persist them as seen."""
    seen_in_run: set[str] = set()
    new_notifications: list[Notification] = []

    for notification in notifications:
        notification_id = notification.notification_id()
        if notification_id in seen_in_run or store.has_seen(notification_id):
            continue

        seen_in_run.add(notification_id)
        store.mark_seen(notification_id)
        new_notifications.append(notification)

    return new_notifications


def run_monitor() -> list[Notification]:
    """Run the monitor across all configured organizations and send new alerts."""
    store = NotificationStore(DEFAULT_SETTINGS.notifications_file)
    notifications_to_send: list[Notification] = []

    for organization, url in ORGANIZATION_SITES.items():
        scraper = OfficialSiteScraper(organization, url)
        scrape_result = scraper.parse()
        if not scrape_result.success:
            logger.warning("Skipping %s due to error: %s", organization, scrape_result.error)
            continue

        new_notifications = collect_new_notifications(
            collect_relevant_notifications(scrape_result.notifications),
            store,
        )
        notifications_to_send.extend(new_notifications)

    if notifications_to_send:
        delivered_count = sum(1 for notification in notifications_to_send if send_notifications([notification]) > 0)
        logger.info("Delivered %s notification email(s)", delivered_count)
    else:
        logger.info("No new notifications found")

    return notifications_to_send


if __name__ == "__main__":
    run_monitor()
    sys.exit(0)
