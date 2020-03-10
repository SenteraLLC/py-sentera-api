"""Functions exposed to the user that make requests to the Sentera Weather API."""
import asyncio

import requests
from pandas.io.json import json_normalize

from sentera import weather


def _run_sentera_query(query, token):
    headers = {"Authorization": "Bearer {}".format(token)}
    request = requests.post(
        url="http://localhost:3001/graphql", json=query, headers=headers
        # url="https://api.sentera.com/graphql", json=query, headers=headers
    )
    if request.status_code != 200:
        raise Exception("Request Failed {}. {}".format(request.status_code, query))

    return request.json()

def create_alert(field_sentera_id, name, message, token):
    query = """mutation CreateAlert ($field_sentera_id: ID!, $name: String!, $message: String!) {
    create_alert (
    field_sentera_id: $field_sentera_id
    name: $name
    message: $message
    )
    {
    sentera_id
    name
    message
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
        "message": message
    }
    result = _run_sentera_query({"query": query, "variables": variables}, token)
    return result

def get_all_fields(token):
    """
    Return a pandas dataframe with information on each field within the user's account.

    Returned DataFrame has columns as follows: (*sentera_id*, *name*, *latitude*, *longitude*)

    :param token: Sentera auth token returned from :code:`sentera.auth.get_auth_token()`.
    :return: **fields_dataframe** - pandas dataframe
    """
    query = {
        "query": "query AllFields{ fields { total_count results{sentera_id name latitude longitude}}}"
    }
    result = _run_sentera_query(query, token)
    data = result["data"]["fields"]["results"]
    return json_normalize(data)


def get_weather(
    weather_type,
    weather_variables,
    weather_interval,
    location_list,
    time_interval=None,
    dtn_key=None,
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
    :param dtn_key: (optional) A DTN key giving access to the data. Has a default hard coded value that works.
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
            dtn_key,
        )
    )
    return weather_df
