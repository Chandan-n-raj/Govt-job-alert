import json
import tempfile
from pathlib import Path

from database import NotificationStore
from filters.job_filter import Notification, is_relevant_notification
from main import collect_new_notifications


def test_relevant_notification_is_detected() -> None:
    notification = Notification(
        organization="RBI",
        post_name="Assistant Manager Recruitment 2026",
    )
    assert is_relevant_notification(notification) is True


def test_excluded_notification_is_filtered_out() -> None:
    notification = Notification(
        organization="SBI",
        post_name="Senior Manager Recruitment",
    )
    assert is_relevant_notification(notification) is False


def test_notification_store_persists_seen_ids() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        store_path = Path(tmpdir) / "notifications.json"
        store = NotificationStore(store_path)
        store.mark_seen("rbi::assistant manager")
        reloaded = NotificationStore(store_path)
        assert reloaded.has_seen("rbi::assistant manager")
        data = json.loads(store_path.read_text(encoding="utf-8"))
        assert "rbi::assistant manager" in data


def test_collect_new_notifications_deduplicates_within_a_run() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        store_path = Path(tmpdir) / "notifications.json"
        store = NotificationStore(store_path)
        duplicate = Notification(organization="RBI", post_name="Assistant Manager Recruitment")
        notifications = [duplicate, duplicate]

        new_notifications = collect_new_notifications(notifications, store)

        assert len(new_notifications) == 1
        assert store.has_seen(duplicate.notification_id())
