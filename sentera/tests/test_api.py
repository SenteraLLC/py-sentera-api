import json

import httpretty
import pytest
import tenacity

from ..api import create_alert, get_weather, get_fields_with_bounds


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
def test_get_fields_with_bounds():
    def request_callback(request, uri, response_headers):

        query = b"query FieldsWithBounds (\\n    $sw_lat: Float!,\\n  $sw_lon: Float!,\\n $ne_lat: Float!,\\n $ne_lon: Float!) {\\n    fields ("
        variables = b'"variables": {"sw_lat": 42.73, "sw_lon": -95.70, "ne_lat": 42.756, "ne_lon": -95.80 }'
        
        # query = b"""
        #     query FieldsWithBounds($sw_lat: Float!, $sw_lon: Float!, $ne_lat: Float!, $ne_lon: Float!) {
        #         fields(
        #             bounds: {
        #                 sw_geo_coordinate: {
        #                     latitude: $sw_lat
        #                     longitude: $sw_lon
        #                 }, 
        #                 ne_geo_coordinate: {
        #                     latitude: $ne_lat
        #                     longitude: $ne_lon
        #                 }
        #             }) {
        #                 total_count
        #                 results {
        #                     sentera_id
        #                     name
        #                     latitude
        #                     longitude
        #                 }
        #             }
        #     }"""
    
        assert variables in request.body
        assert query in request.body
        return [
            200,
            response_headers,
            json.dumps(
                {
                    "data": {
                        "fields": {
                        "total_count": 1,
                        "results": [
                            {
                            "sentera_id": "sfgz3up_AS_8brhbkSentera_CV_shar_b48fa1c_210203_000857",
                            "name": "Jeff's Field",
                            "latitude": 42.734587032522,
                            "longitude": -95.625703409314
                            }
                        ]
                        }
                    }
                }
            ),
        ]
    
    httpretty.register_uri(
        httpretty.POST, "https://apitest.sentera.com/graphql", body=request_callback
    )

    response = get_fields_with_bounds(
        "ddoPA-16Oaw3Ru2WFxnlo-RhBF18y82oHrzeUPdeNgI",
        42.73,
        -95.70,
        42.756,
        -95.80
    )
