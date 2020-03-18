import pytest

from ..configuration import Configuration


def test_default_configuration():
    configuration = Configuration()
    assert configuration.environment == "production"
    assert configuration.sentera_api_url("/") == "https://api.sentera.com/"


def test_development_configuration(monkeypatch):
    monkeypatch.setenv("SENTERA_ENV", "development")
    configuration = Configuration()
    assert configuration.environment == "development"
    assert configuration.sentera_api_url("/") == "https://apidev.sentera.com/"


def test_argument_configuration(monkeypatch):
    assert Configuration("staging").environment == "staging"
