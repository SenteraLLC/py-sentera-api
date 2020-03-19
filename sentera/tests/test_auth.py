import json

import httpretty
import pytest

from ..auth import get_application_token, get_auth_token


@httpretty.httprettified
def test_get_application_token_success():
    def request_callback(request, uri, response_headers):
        assert (
            request.headers["Authorization"]
            == "Basic dGVzdF9jbGllbnRfaWRfMTIzOnRlc3RfY2xpZW50X3NlY3JldF8zMjE="
        )
        assert request.body == b"grant_type=client_credentials"
        return [
            200,
            response_headers,
            json.dumps(
                {
                    "access_token": "my-test-access-token-abc123",
                    "token_type": "Bearer",
                    "expires_in": 1800,
                    "created_at": 1584561685,
                }
            ),
        ]

    httpretty.register_uri(
        httpretty.POST, "https://apitest.sentera.com/oauth/token", body=request_callback
    )
    response = get_application_token("test_client_id_123", "test_client_secret_321")
    assert response["access_token"] == "my-test-access-token-abc123"
    assert len(httpretty.latest_requests()) == 1


@httpretty.httprettified
def test_get_auth_token_success():
    def request_callback(request, uri, response_headers):
        body_json = json.loads(request.body.decode("utf-8"))
        assert body_json["session"]["email"] == "test@email.com"
        assert body_json["session"]["password"] == "pass123"
        return [
            200,
            response_headers,
            json.dumps({"auth_token": "my-test-access-token-xyz098"}),
        ]

    httpretty.register_uri(
        httpretty.POST, "https://apitest.sentera.com/v1/sessions", body=request_callback
    )
    response = get_auth_token("test@email.com", "pass123")
    assert response == "my-test-access-token-xyz098"
    assert len(httpretty.latest_requests()) == 1
