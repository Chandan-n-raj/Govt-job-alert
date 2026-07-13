import json
import tempfile
from pathlib import Path

from database import NotificationStore


def test_store_persists_and_loads_ids() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        store_path = Path(tmpdir) / "notifications.json"
        store = NotificationStore(store_path)
        store.mark_seen("rbi::assistant manager")
        store.mark_seen("sbi::officer")

        reloaded = NotificationStore(store_path)
        assert reloaded.has_seen("rbi::assistant manager")
        assert reloaded.has_seen("sbi::officer")
        assert reloaded.list_seen() == ["rbi::assistant manager", "sbi::officer"]

        payload = json.loads(store_path.read_text(encoding="utf-8"))
        assert payload == ["rbi::assistant manager", "sbi::officer"]
