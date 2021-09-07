import pytest

from ..configuration import Configuration


def test_default_configuration(monkeypatch):
    monkeypatch.delenv("SENTERA_ENV", raising=False)
    configuration = Configuration()
    assert configuration.environment == "prod"
    assert configuration.sentera_api_url("/") == "https://api.sentera.com/"
    assert configuration.weather_api_url("/") == "https://weather.sentera.com/"


def test_development_configuration(monkeypatch):
    monkeypatch.setenv("SENTERA_ENV", "dev")
    configuration = Configuration()
    assert configuration.environment == "dev"
    assert configuration.sentera_api_url("/") == "https://apidev.sentera.com/"
    assert configuration.weather_api_url("/") == "https://weatherdev.sentera.com/"


def test_env_sentera_api_url_configuration(monkeypatch):
    monkeypatch.setenv("SENTERA_API_URL", "https://example.com")
    configuration = Configuration()
    assert configuration.environment == "test"
    assert configuration.sentera_api_url("/") == "https://example.com/"
    assert configuration.weather_api_url("/") == "https://weathertest.sentera.com/"


def test_env_weather_api_url_configuration(monkeypatch):
    monkeypatch.setenv("WEATHER_API_URL", "https://weatherkazoo.sentera.com")
    configuration = Configuration()
    assert configuration.environment == "test"
    assert configuration.sentera_api_url("/") == "https://apitest.sentera.com/"
    assert configuration.weather_api_url("/") == "https://weatherkazoo.sentera.com/"


def test_argument_configuration(monkeypatch):
    assert Configuration("staging").environment == "staging"
