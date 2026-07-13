from __future__ import annotations

import logging
import smtplib
from email.message import EmailMessage
from typing import Iterable

from config import DEFAULT_SETTINGS
from filters.job_filter import Notification

logger = logging.getLogger(__name__)


def _build_message(notification: Notification) -> EmailMessage:
    """Create an email message for a notification."""
    message = EmailMessage()
    message["Subject"] = f"New Recruitment Alert: {notification.organization} - {notification.post_name}"
    message["From"] = DEFAULT_SETTINGS.email_from
    message["To"] = DEFAULT_SETTINGS.email_to

    body = "\n".join(
        [
            f"Organization: {notification.organization}",
            f"Post Name: {notification.post_name}",
            f"Vacancies: {notification.vacancies or 'Not provided'}",
            f"Apply Link: {notification.apply_link or 'Not provided'}",
            f"Official PDF: {notification.official_pdf or 'Not provided'}",
        ]
    )
    message.set_content(body)
    return message


def send_notification_email(notification: Notification) -> bool:
    """Send a brief email for a new recruitment notification."""
    if not DEFAULT_SETTINGS.email_to or not DEFAULT_SETTINGS.email_from:
        logger.info("Email credentials missing; skipping email delivery for %s", notification.post_name)
        return False

    message = _build_message(notification)

    try:
        with smtplib.SMTP(DEFAULT_SETTINGS.smtp_host, DEFAULT_SETTINGS.smtp_port) as smtp:
            if DEFAULT_SETTINGS.smtp_use_tls:
                smtp.starttls()
            if DEFAULT_SETTINGS.smtp_username and DEFAULT_SETTINGS.smtp_password:
                smtp.login(DEFAULT_SETTINGS.smtp_username, DEFAULT_SETTINGS.smtp_password)
            smtp.send_message(message)
    except Exception as exc:  # pragma: no cover - defensive path
        logger.exception("Email delivery failed for %s: %s", notification.post_name, exc)
        return False

    return True


def send_notifications(notifications: Iterable[Notification]) -> int:
    """Send emails for a collection of notifications and return the success count."""
    return sum(1 for notification in notifications if send_notification_email(notification))
