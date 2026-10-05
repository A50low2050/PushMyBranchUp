# flake8: noqa: E402

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import uvicorn

from src.config import settings
from src.utils.logserv import LogService

# точка входа в приложение
if __name__ == "__main__":
    log_config = LogService.configurate()

    uvicorn.run(
        "src.api.main:app",
        host=settings.uvicorn.host,
        port=settings.uvicorn.port,
        reload=settings.uvicorn.reload,
        log_config=log_config,
    )
