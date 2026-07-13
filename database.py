from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class NotificationStore:
    """Persist known notification identifiers in a JSON file."""

    def __init__(self, file_path: str | Path) -> None:
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self._known_ids: set[str] = set()
        self._load()

    def _load(self) -> None:
        if not self.file_path.exists():
            self._known_ids = set()
            return

        try:
            data = json.loads(self.file_path.read_text(encoding="utf-8"))
            if isinstance(data, list):
                self._known_ids = {str(item) for item in data}
            else:
                self._known_ids = set()
        except (json.JSONDecodeError, OSError):
            self._known_ids = set()

    def has_seen(self, notification_id: str) -> bool:
        return notification_id in self._known_ids

    def mark_seen(self, notification_id: str) -> None:
        self._known_ids.add(notification_id)
        self._persist()

    def _persist(self) -> None:
        self.file_path.write_text(json.dumps(sorted(self._known_ids), indent=2), encoding="utf-8")

    def list_seen(self) -> list[str]:
        return sorted(self._known_ids)

    def add_many(self, notification_ids: list[str]) -> None:
        self._known_ids.update(notification_ids)
        self._persist()

    @property
    def known_ids(self) -> set[str]:
        return set(self._known_ids)
