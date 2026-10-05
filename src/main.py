import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import uvicorn

from src.config import settings

### точка входа в приложение
if __name__ == "__main__":
    uvicorn.run(
        "src.api.main:app",
        host=settings.uvicorn.host,
        port=settings.uvicorn.port,
        reload=settings.uvicorn.reload,
    )
