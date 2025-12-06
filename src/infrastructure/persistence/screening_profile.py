import json
from pathlib import Path

PROFILE_DIR = Path("cache/screening_profiles")

class ScreeningProfile:
    def __init__(self):
        PROFILE_DIR.mkdir(exist_ok=True)

    def list_profiles(self):
        return [p.stem for p in PROFILE_DIR.glob("*.json")]

    def save(self, name: str, data: dict):
        path = PROFILE_DIR / f"{name}.json"
        with open(path, "w") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load(self, name: str) -> dict:
        path = PROFILE_DIR / f"{name}.json"
        if not path.exists():
            return {}
        with open(path) as f:
            return json.load(f)
