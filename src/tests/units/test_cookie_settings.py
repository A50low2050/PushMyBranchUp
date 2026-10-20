from datetime import timedelta

from src.config import CookieSettings, settings


def test_cookie_settings_defaults():
    cookie = CookieSettings()
    assert cookie.key == "refresh_token"
    assert cookie.name == "refresh_token"
    assert cookie.max_age == 2592000
    assert cookie.httponly is True
    assert cookie.samesite == "lax"
    assert cookie.secure is False
    assert cookie.path == "/"
    assert cookie.domain is None


def test_cookie_settings_max_age_from_timedelta():
    cookie = CookieSettings(max_age=timedelta(days=7))
    assert cookie.max_age == 604800


def test_cookie_settings_max_age_from_str():
    cookie = CookieSettings(max_age="3600")
    assert cookie.max_age == 3600


def test_settings_cookie_properties():
    assert settings.cookie.key == "refresh_token"
    assert settings.cookies.key == "refresh_token"
    assert settings.auth.cookie.key == "refresh_token"
    assert settings.auth.cookies.key == "refresh_token"
    assert settings.auth.refresh_token_cookie_name == "refresh_token"
