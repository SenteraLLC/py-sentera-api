import pytest

from ..configuration import Configuration


def test_default_configuration(monkeypatch):
    monkeypatch.delenv("SENTERA_ENV", raising=False)
    configuration = Configuration()
    assert configuration.environment == "prod"
    assert configuration.sentera_api_url("/") == "https://api.sentera.com/"


def test_development_configuration(monkeypatch):
    monkeypatch.setenv("SENTERA_ENV", "dev")
    configuration = Configuration()
    assert configuration.environment == "dev"
    assert configuration.sentera_api_url("/") == "https://apidev.sentera.com/"


def test_argument_configuration(monkeypatch):
    assert Configuration("staging").environment == "staging"
