import pytest


@pytest.fixture(autouse=True)
def set_test_env(monkeypatch):
    monkeypatch.setenv("SENTERA_ENV", "test")
