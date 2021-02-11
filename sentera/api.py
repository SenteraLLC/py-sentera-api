"""Functions exposed to the user that make requests to the Sentera Weather API."""
import asyncio
import math

import requests
from pandas import json_normalize

from sentera import weather
from sentera.configuration import Configuration


def _run_sentera_query(query, token):
    url = Configuration().sentera_api_url("/graphql")
    headers = {"Authorization": token}
    response = requests.post(url=url, json=query, headers=headers)
    if response.status_code != 200:
        raise Exception(
            "Request Failed {}. {}".format(response.status_code, response.text)
        )

    return response.json()


def get_all_fields(token):
    """
    Return a pandas dataframe result with information on each field within the user's account.

    Returned dataframe has the following values: (*sentera_id*, *name*, *latitude*, *longitude*)

    :param token: Sentera auth token returned from :code:`sentera.auth.get_auth_token()`.
    :return: **fields_dataframe** - pandas dataframe
    """
    query = {
        "query": "query AllFields{ fields { total_count results{sentera_id name latitude longitude}}}"
    }
    result = _run_sentera_query(query, token)
    data = result["data"]["fields"]["results"]
    return json_normalize(data)


def get_fields_within_bounds(token, sw_lat, sw_lon, ne_lat, ne_lon):
    """
    Return a pandas dataframe result of fields within a given boundry.

    The function takes the southwest and northeast coordinates of a paticular area of interest,
    returning all fields inside those coordinates.

    :param token: Sentera auth token returned from :code:`sentera.auth.get_auth_token()`.
    :param page:
    :return: **fields_df** - pandas dataframe
    """
    query = """
        FieldsWithBounds($page: Int!, $sw_lat: Float!, $sw_lon: Float!, $ne_lat: Float!, $ne_lon: Float!) {
            fields(
                pagination: {
                    page: $page
                    page_size: 1000
                }
                bounds: {
                    sw_geo_coordinate: {
                        latitude: $sw_lat
                        longitude: $sw_lon
                    },
                    ne_geo_coordinate: {
                        latitude: $ne_lat
                        longitude: $ne_lon
                    }
                }) {
                    total_count
                    page
                    page_size
                    results {
                        sentera_id
                        name
                        latitude
                        longitude
                    }
                }
        }"""

    variables = {
        "page": 1,
        "sw_lat": sw_lat,
        "sw_lon": sw_lon,
        "ne_lat": ne_lat,
        "ne_lon": ne_lon,
    }

    data = {"query": query, "variables": variables}
    response = _run_sentera_query(data, token)

    fields = response["data"]["fields"]["results"]
    fields_df = json_normalize(fields)
    total_pages = math.ceil(
        response["data"]["fields"]["total_count"]
        / response["data"]["fields"]["page_size"]
    )

    for page in range(2, total_pages + 1):
        variables["page"] = page
        data = {"query": query, "variables": variables}
        response = _run_sentera_query(data, token)

        additional_fields = response["data"]["fields"]["results"]
        fields_df = fields_df.append(json_normalize(additional_fields))

    return fields_df


def get_weather(
    weather_type,
    location_list,
    weather_variables=None,
    weather_interval=None,
    time_interval=None,
    sentera_api_key=None,
):
    """
    Return a pandas DataFrame with desired weather information.

    :param weather_type: either a string (e.g. *'recent'*) or :code:`sentera.weather.WeatherType`
    :param weather_variables: list of strings (e.g. *['temperature', 'relative-humidity']*) or
                              list of :code:`sentera.weather.WeatherVariable`'s
    :param weather_interval: either a string (e.g. *'hourly'*) or :code:`sentera.weather.WeatherInterval`
    :param time_interval: [*day_start*, *day_end*] in format **YYYY/MM/DD** (eg. *['2020/01/01', '2020/01/03']*).
                          Needed for *recent* weather types, but no others.
    :param location_list: list of locations defined by (*lat*, *long*) to get weather for
    :param sentera_api_key: (optional) A Sentera API key giving access to the data. Has a default hard coded value that works.
    :return: **weather_dataframe** - pandas dataframe
    """
    weather_type = weather.WeatherType(weather_type)
    weather_interval = weather.WeatherInterval(weather_interval)

    url_list = []
    weather_variables_list = []
    time_interval_list = []

    time_intervals = weather.split_time_interval(
        time_interval, weather_type, weather_interval
    )

    if not weather_variables:
        weather_variables = [None]

    for time_interval in time_intervals:
        for field_location in location_list:
            for weather_variable in weather_variables:
                weather_variable = weather.WeatherVariable(weather_variable)
                weather_url = weather.build_weather_url(
                    weather_type,
                    weather_variable,
                    weather_interval,
                    field_location[0],
                    field_location[1],
                )
                url_list.append(weather_url)
                weather_variables_list.append(weather_variable)
                time_interval_list.append(time_interval)

    loop = asyncio.get_event_loop()
    weather_df = loop.run_until_complete(
        weather.run_queries(
            url_list,
            weather_variables_list,
            time_interval_list,
            weather_interval,
            weather_type,
            sentera_api_key,
        )
    )
    return weather_df


def create_alert(field_sentera_id, name, message, token, key=None, url=None):
    """
    Create alert content and post alert mutation to https://api.sentera.com/graphql.

    :param field_sentera_id: A field id (string)
    :param name: name of the alert (string)
    :param message: brief description of the alert being made (string)
    :param token: an authorization token needed to post the alert to the specified field (string)
    :param key: (optional) A client-defined key to help identify the alert.
    :param url: (optional) url link to more information about the alert (url)
    :return: result of the request.post
    """
    query = """mutation CreateAlert (
    $field_sentera_id: ID!,
    $name: String!,
    $message: String!,
    $key: String,
    $url: Url) {
    create_alert (
    field_sentera_id: $field_sentera_id
    name: $name
    message: $message
    key: $key
    url: $url
    )
    {
    sentera_id
    name
    message
    key
    url
    created_by {
        sentera_id
        first_name
        last_name
        email
        }
        created_at
    }
}"""
    variables = {
        "field_sentera_id": field_sentera_id,
        "name": name,
        "message": message,
        "key": key,
        "url": url,
    }
    data = {"query": query, "variables": variables}
    result = _run_sentera_query(data, token)

    return result
