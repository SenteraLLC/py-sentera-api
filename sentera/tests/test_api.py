import json
import pathlib
import unittest

import httpretty
import pandas as pd
import pytest
import requests_mock
import tenacity
from pandas import json_normalize
from pandas._testing import assert_frame_equal

from ..api import create_alert, get_fields_within_bounds, get_weather

TOKEN = "aaa"


@httpretty.httprettified
def test_create_alert_with_key_success():
    def request_callback(request, uri, response_headers):
        mutation = b"mutation CreateAlert (\\n    $field_sentera_id: ID!,\\n    $name: String!,\\n    $message: String!,\\n    $key: String,\\n    $url: Url) {\\n    create_alert ("
        variables = b'"variables": {"field_sentera_id": "gyq8ll6_AL_8brhbkSentera_CV_shar_e599fde_200326_182003", "name": "Southern Corn Rust Alert", "message": "Current weather conditions indicate things.", "key": "corn_rust", "url": "https://www.sentera.com"}'
        print(request.body)
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
                            "url": "https://www.sentera.com",
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
        url="https://www.sentera.com",
    )
    assert response["data"]["create_alert"]["key"] == "corn_rust"
    assert len(httpretty.latest_requests()) == 1


@httpretty.httprettified
def test_create_alert_without_key_success():
    def request_callback(request, uri, response_headers):
        mutation = b"mutation CreateAlert (\\n    $field_sentera_id: ID!,\\n    $name: String!,\\n    $message: String!,\\n    $key: String,\\n    $url: Url) {\\n    create_alert ("
        variables = b'"variables": {"field_sentera_id": "gyq8ll6_AL_8brhbkSentera_CV_shar_e599fde_200326_182003", "name": "Southern Corn Rust Alert", "message": "Current weather conditions indicate things.", "key": null, "url": null}'
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
                            "url": None,
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


def test_get_weather():
    with pytest.raises(tenacity.RetryError) as retry_error:
        get_weather(
            "recent",
            [[10, -90]],
            ["high-temperature"],
            "daily",
            ["2020/01/01", "2020/01/03"],
        )


@httpretty.httprettified
def test_get_fields_within_bounds():
    def request_callback(request, uri, response_headers):
        query = b'{"query": "\\n        query FieldsWithBounds($page: Int!, $sw_lat: Float!, $sw_lon: Float!, $ne_lat: Float!, $ne_lon: Float!) {\\n'
        variables = b'"variables": {"page": 1, "sw_lat": 42.73, "sw_lon": -95.7, "ne_lat": 42.756, "ne_lon": -95.8}}'

        assert query in request.body
        assert variables in request.body
        return [
            200,
            response_headers,
            json.dumps(
                {
                    "data": {
                        "fields": {
                            "total_count": 1,
                            "page": 1,
                            "page_size": 1000,
                            "results": [
                                {
                                    "sentera_id": "gyq8ll6_AL_8brhbkSentera_CV_shar_e599fde_200326_182003",
                                    "name": "Boundary Test",
                                    "latitude": 42.734587032522,
                                    "longitude": -95.625703409314,
                                }
                            ],
                        }
                    }
                }
            ),
        ]

    fields_df = pd.DataFrame(
        {
            "sentera_id": "gyq8ll6_AL_8brhbkSentera_CV_shar_e599fde_200326_182003",
            "name": "Boundary Test",
            "latitude": [42.734587],
            "longitude": [-95.625703],
        }
    )

    httpretty.register_uri(
        httpretty.POST, "https://apitest.sentera.com/graphql", body=request_callback
    )
    response = get_fields_within_bounds(TOKEN, 42.73, -95.70, 42.756, -95.80)
    assert_frame_equal(response, fields_df)
    assert len(httpretty.latest_requests()) == 1


class test_get_fields_within_bounds_pagination(unittest.TestCase):
    def test_pagination(self):
        with open(
            pathlib.Path(__file__).parent / "pagination_first_page.json"
        ) as first_file:
            mock_response_first_page = first_file.read()

        with open(
            pathlib.Path(__file__).parent / "pagination_second_page.json"
        ) as second_file:
            mock_response_second_page = second_file.read()

        expected_result = [
            {
                "data": {
                    "fields": {
                        "total_count": 3,
                        "page": 1,
                        "page_size": 2,
                        "results": [
                            {
                                "sentera_id": "gyq8ll6_AL_8brhbkSentera_CV_shar_e599fde_200326_182003",
                                "name": "Boundary Test",
                                "latitude": 42.734587032522,
                                "longitude": -95.625703409314,
                            },
                            {
                                "sentera_id": "gyq8ll6_AL_8brhbkSentera_CV_shar_e599fde_200326_182003",
                                "name": "Boundary Test 2",
                                "latitude": 42.734587032522,
                                "longitude": -95.625703409314,
                            },
                            {
                                "sentera_id": "gyq8ll6_AL_8brhbkSentera_CV_shar_e599fde_200326_182003",
                                "name": "Boundary Test 3",
                                "latitude": 42.734587032522,
                                "longitude": -95.625703409314,
                            },
                        ],
                    }
                }
            }
        ]

        expected_df = json_normalize(expected_result[0]["data"]["fields"]["results"])

        with requests_mock.Mocker() as m:
            m.register_uri(
                "POST",
                "https://apitest.sentera.com/graphql",
                [
                    {"text": mock_response_first_page},
                    {"text": mock_response_second_page},
                ],
            )
            response = get_fields_within_bounds(TOKEN, 42.73, -95.70, 42.756, -95.80)

        assert_frame_equal(
            response.reset_index(drop=True), expected_df.reset_index(drop=True)
        )


@httpretty.activate
def test_empty_dataframe():
    def request_callback(request, uri, response_headers):
        return [
            200,
            response_headers,
            json.dumps(
                {
                    "data": {
                        "fields": {
                            "total_count": 0,
                            "page": 1,
                            "page_size": 1000,
                            "results": [],
                        }
                    }
                }
            ),
        ]

    fields_df = pd.DataFrame({})
    httpretty.register_uri(
        httpretty.POST, "https://apitest.sentera.com/graphql", body=request_callback
    )
    response = get_fields_within_bounds(TOKEN, 0, 0, 0, 0)
    assert_frame_equal(response, fields_df)
