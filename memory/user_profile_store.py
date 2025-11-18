import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)


@dataclass
class UserProfileStore:
    """Simple file-backed store for long-term user preferences.

    Stores one JSON file per user_id with fields like:
    {"style": {"tone": "friendly", "paragraph_length": "short"}}
    """

    root_dir: Path = field(default_factory=lambda: Path("data/users"))

    def __post_init__(self) -> None:
        self.root_dir.mkdir(parents=True, exist_ok=True)

    def _user_path(self, user_id: str) -> Path:
        return self.root_dir / f"{user_id}.json"

    def load_profile(self, user_id: str) -> Dict[str, Any]:
        path = self._user_path(user_id)
        if not path.exists():
            return {"style": {}}
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            logger.warning("Corrupt user profile, resetting", extra={"user_id": user_id})
            return {"style": {}}

    def save_profile(self, user_id: str, profile: Dict[str, Any]) -> None:
        path = self._user_path(user_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(profile, indent=2, ensure_ascii=False), encoding="utf-8")
        logger.info("Saved user profile", extra={"user_id": user_id})

    def update_style_preferences(self, user_id: str, updates: Dict[str, Any]) -> None:
        profile = self.load_profile(user_id)
        style = profile.get("style", {})
        style.update(updates)
        profile["style"] = style
        self.save_profile(user_id, profile)
