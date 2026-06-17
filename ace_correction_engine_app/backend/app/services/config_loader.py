import json
from pathlib import Path

CONFIG_PATH = Path("/app/config/error_config.sample.json")

def load_error_config() -> list[dict]:
    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)
