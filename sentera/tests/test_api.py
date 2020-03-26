import json

import httpretty
import pytest

from ..api import create_alert


@httpretty.httprettified
def test_create_alert_with_key_success():
    def request_callback(request, uri, response_headers):
        mutation = b"mutation CreateAlert ($field_sentera_id: ID!, $name: String!, $message: String!, $key: String) {\\n    create_alert ("
        variables = b'"variables": {"field_sentera_id": "gyq8ll6_AL_8brhbkSentera_CV_shar_e599fde_200326_182003", "name": "Southern Corn Rust Alert", "message": "Current weather conditions indicate things.", "key": "corn_rust"}'
        assert variables in request.body
        assert mutation in request.body
        return [
            200,
            response_headers,
            json.dumps(
                {
                    "data": {
                        "create_alert": {
                            "sentera_id": "gyq8ll6_AL_8brhbkSentera_CV_shar_e599fde_200326_182003",
                            "key": "corn_rust",
                            "name": "Southern Corn Rust Alert",
                            "message": "Current weather conditions indicate things.",
                            "created_at": "2020-03-26T18:20:03Z",
                        }
                    }
                }
            ),
        ]

    httpretty.register_uri(
        httpretty.POST, "https://apitest.sentera.com/graphql", body=request_callback
    )
    response = create_alert(
        field_sentera_id="gyq8ll6_AL_8brhbkSentera_CV_shar_e599fde_200326_182003",
        name="Southern Corn Rust Alert",
        message="Current weather conditions indicate things.",
        token="token123",
        key="corn_rust",
    )
    assert response["data"]["create_alert"]["key"] == "corn_rust"
    assert len(httpretty.latest_requests()) == 1


@httpretty.httprettified
def test_create_alert_without_key_success():
    def request_callback(request, uri, response_headers):
        mutation = b"mutation CreateAlert ($field_sentera_id: ID!, $name: String!, $message: String!, $key: String) {\\n    create_alert ("
        variables = b'"variables": {"field_sentera_id": "gyq8ll6_AL_8brhbkSentera_CV_shar_e599fde_200326_182003", "name": "Southern Corn Rust Alert", "message": "Current weather conditions indicate things.", "key": null}'
        assert variables in request.body
        assert mutation in request.body
        return [
            200,
            response_headers,
            json.dumps(
                {
                    "data": {
                        "create_alert": {
                            "sentera_id": "gyq8ll6_AL_8brhbkSentera_CV_shar_e599fde_200326_182003",
                            "key": None,
                            "name": "Southern Corn Rust Alert",
                            "message": "Current weather conditions indicate things.",
                            "created_at": "2020-03-26T18:20:03Z",
                        }
                    }
                }
            ),
        ]

    httpretty.register_uri(
        httpretty.POST, "https://apitest.sentera.com/graphql", body=request_callback
    )
    response = create_alert(
        "gyq8ll6_AL_8brhbkSentera_CV_shar_e599fde_200326_182003",
        "Southern Corn Rust Alert",
        "Current weather conditions indicate things.",
        "token123",
    )
    assert response["data"]["create_alert"]["key"] is None
    assert len(httpretty.latest_requests()) == 1
