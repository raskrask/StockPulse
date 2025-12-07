import json
import os
from datetime import datetime
from infrastructure.util.io_utils import BASE_DIR

class RunStateRepository:
    FILE_PATH = f"{BASE_DIR}/state/run_state.json"

    def __init__(self):
        os.makedirs(os.path.dirname(self.FILE_PATH), exist_ok=True)
        if not os.path.exists(self.FILE_PATH):
            with open(self.FILE_PATH, "w") as f:
                json.dump({ "last_run_at": None}, f)

    def load(self):
        with open(self.FILE_PATH, "r") as f:
            data = json.load(f)

        # 文字列 → datetime 変換
        for key in data:
            if data[key]:
                data[key] = datetime.fromisoformat(data[key])

        return data

    def save(self, state: dict):
        serializable = {}
        for key, value in state.items():
            serializable[key] = value.isoformat() if value else None

        with open(self.FILE_PATH, "w") as f:
            json.dump(serializable, f, indent=2)