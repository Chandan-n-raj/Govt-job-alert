from unittest.mock import patch

from config import DEFAULT_SETTINGS
from database import NotificationStore
from filters.job_filter import Notification
from main import collect_new_notifications, run_monitor


def test_collect_new_notifications_deduplicates_in_run_and_across_runs(tmp_path) -> None:
    store = NotificationStore(tmp_path / "notifications.json")
    notification = Notification(organization="RBI", post_name="Officer Recruitment")

    first_batch = collect_new_notifications([notification, notification], store)
    second_batch = collect_new_notifications([notification], store)

    assert len(first_batch) == 1
    assert len(second_batch) == 0


def test_run_monitor_skips_failed_scrapes_and_logs(tmp_path) -> None:
    store_path = tmp_path / "notifications.json"
    with patch("main.DEFAULT_SETTINGS", DEFAULT_SETTINGS.__class__(notifications_file=str(store_path))), patch("main.OfficialSiteScraper.parse") as parse_mock, patch("main.send_notifications") as send_mock:
        parse_mock.return_value.success = False
        parse_mock.return_value.error = "boom"
        result = run_monitor()

    assert result == []
    send_mock.assert_not_called()
