from slowapi import Limiter
from slowapi.util import get_remote_address

from src.config import settings

limiter = Limiter(
    key_func=get_remote_address,
    enabled=settings.rate_limit.enabled,
    headers_enabled=False,
)
