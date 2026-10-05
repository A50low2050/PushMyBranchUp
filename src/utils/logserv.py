import json
import logging
import logging.config
import os
from typing import Any

from src.config import BASE_DIR


class LogService:
    @staticmethod
    def configurate() -> dict[str, Any]:
        config_file = BASE_DIR / "logconfig.json"
        os.makedirs(BASE_DIR / "logs", exist_ok=True)

        with open(config_file, "r", encoding="utf-8") as f:
            logging_cfg = json.load(f)

        logs_path = BASE_DIR / "logs" / "main.log"
        logging_cfg["handlers"]["file"]["filename"] = logs_path
        logging.config.dictConfig(logging_cfg)
        return logging_cfg

    @staticmethod
    def get_logger(name: str | None = None) -> logging.Logger:
        return logging.getLogger(name or __name__)
