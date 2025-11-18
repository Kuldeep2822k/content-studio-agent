import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


@dataclass
class SessionMemory:
    """Very simple JSON-file-backed session memory.

    In a more advanced setup you might swap this out for a database or a
    vector store. For the capstone, this keeps things transparent.
    """

    root_dir: Path = field(default_factory=lambda: Path("data/sessions"))

    def __post_init__(self) -> None:
        self.root_dir.mkdir(parents=True, exist_ok=True)

    def _session_path(self, session_id: str) -> Path:
        return self.root_dir / f"{session_id}.json"

    def load_session(self, session_id: str) -> Dict[str, Any]:
        path = self._session_path(session_id)
        if not path.exists():
            return {"events": []}
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            logger.warning("Corrupt session file, resetting", extra={"session_id": session_id})
            return {"events": []}

    def append_event(self, session_id: str, event: Dict[str, Any]) -> None:
        data = self.load_session(session_id)
        events: List[Dict[str, Any]] = data.get("events", [])
        events.append(event)
        data["events"] = events

        path = self._session_path(session_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

        logger.info("Appended session event", extra={"session_id": session_id, "event_type": event.get("type")})
