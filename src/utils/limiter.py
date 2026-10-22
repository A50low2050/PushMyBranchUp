import re
from slowapi import Limiter
from slowapi.util import get_remote_address

from src.config import settings

limiter = Limiter(
    key_func=get_remote_address,
    enabled=settings.rate_limit.enabled,
    headers_enabled=False,
)


def format_rate_limit_detail(detail: str | None) -> str:
    """Переводит описание лимита slowapi/limits на русский язык.

    Примеры входных значений: '30 per minute' и '30 per 1 minute'.
    """
    if not detail:
        return "Превышен лимит запросов. Попробуйте позже."

    # Разбираем форматы вида "30 per minute", "30 per 1 minute", "10 per 5 seconds"
    match = re.search(r"(\d+)\s+per\s+(?:(\d+)\s+)?([a-zA-Z]+)", detail, re.IGNORECASE)
    if not match:
        return f"Превышен лимит запросов: {detail}"

    amount = match.group(1)
    multiples = int(match.group(2)) if match.group(2) else 1
    unit = match.group(3).lower()

    # Склонения единиц времени: (1, 2-4, 5+)
    units_map = {
        "second": ("секунду", "секунды", "секунд"),
        "seconds": ("секунду", "секунды", "секунд"),
        "minute": ("минуту", "минуты", "минут"),
        "minutes": ("минуту", "минуты", "минут"),
        "hour": ("час", "часа", "часов"),
        "hours": ("час", "часа", "часов"),
        "day": ("день", "дня", "дней"),
        "days": ("день", "дня", "дней"),
        "month": ("месяц", "месяца", "месяцев"),
        "months": ("месяц", "месяца", "месяцев"),
        "year": ("год", "года", "лет"),
        "years": ("год", "года", "лет"),
    }

    if unit not in units_map:
        return f"Превышен лимит запросов: {detail}"

    one, few, many = units_map[unit]

    if multiples == 1:
        return f"Превышен лимит запросов: {amount} в {one}"

    if 11 <= (multiples % 100) <= 14:
        unit_form = many
    elif multiples % 10 == 1:
        unit_form = one
    elif 2 <= (multiples % 10) <= 4:
        unit_form = few
    else:
        unit_form = many

    return f"Превышен лимит запросов: {amount} за {multiples} {unit_form}"
