from typing import Annotated

from fastapi import Depends, Request

from src.utils.notiserv import NotificationService


def get_notifications(request: Request) -> NotificationService:
    return request.app.state.notifications


NotificationsDep = Annotated[NotificationService, Depends(get_notifications)]
