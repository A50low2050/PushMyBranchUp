from typing import Annotated

from fastapi import Depends
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)

security = HTTPBearer()
BearerCredentials = Annotated[HTTPAuthorizationCredentials, Depends(security)]


def get_token(creds: BearerCredentials) -> str:
    return creds.credentials


GetTokenDep = Annotated[str, Depends(get_token)]
