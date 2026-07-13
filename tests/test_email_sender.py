from unittest.mock import patch

from email_sender import send_notification_email, send_notifications
from filters.job_filter import Notification


def test_send_notification_email_skips_without_credentials() -> None:
    notification = Notification(organization="RBI", post_name="Officer Recruitment")
    with patch("email_sender.DEFAULT_SETTINGS") as settings:
        settings.email_to = ""
        settings.email_from = ""
        assert send_notification_email(notification) is False


def test_send_notification_email_success() -> None:
    notification = Notification(organization="RBI", post_name="Officer Recruitment")
    with patch("email_sender.DEFAULT_SETTINGS") as settings, patch("email_sender.smtplib.SMTP") as smtp_cls:
        settings.email_to = "user@example.com"
        settings.email_from = "sender@example.com"
        settings.smtp_host = "smtp.example.com"
        settings.smtp_port = 587
        settings.smtp_use_tls = False
        settings.smtp_username = ""
        settings.smtp_password = ""
        smtp_instance = smtp_cls.return_value.__enter__.return_value
        assert send_notification_email(notification) is True
        smtp_instance.send_message.assert_called_once()


def test_send_notifications_returns_count() -> None:
    notifications = [Notification(organization="RBI", post_name="Officer Recruitment")]
    with patch("email_sender.send_notification_email", return_value=True) as send_mock:
        assert send_notifications(notifications) == 1
        send_mock.assert_called_once_with(notifications[0])
