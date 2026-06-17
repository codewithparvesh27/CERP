import json
import os
from pathlib import Path


def load_error_config() -> listcandidates = [
        os.getenv("ERROR_CONFIG_PATH"),
        "/app/config/error_config.sample.json",
        "config/error_config.sample.json",
        "../config/error_config.sample.json",
        "app/config/error_config.sample.json",
    ]

    for candidate in candidates:
        if not candidate:
            continue

        path = Path(candidate)
        if path.exists():
            with path.open("r", encoding="utf-8") as f:
                return json.load(f)

    raise FileNotFoundError(
        "Could not find error configuration file. "
        "Set ERROR_CONFIG_PATH environment variable."
    )