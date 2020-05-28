"""
Functions and classes enabling the construction of weather queries to be made against the Sentera Weather API.

Possible values for weather types, variables, and intervals are constrained by the Enum classes contained within this
module, as well as a nested dict that enumerates all possible allowable combinations.

Many of these functions have been defined to support asynchronous requests of weather data, and are invoked in an
asynchronous manner by the ``sentera.api`` module.
"""
import asyncio
import datetime
import json
import os
import re
from distutils.util import strtobool
from enum import Enum

import aiohttp
import pandas as pd
import tqdm
from pandas import json_normalize
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_random

from sentera.configuration import Configuration

WEATHER_BASE_URL = "https://weather.sentera.com"
WEATHER_HEADER = {"X-API-Key": "mc049Cu9FJ3lHiQYDYQTd3ZOzsOBt29d2gyi3e0r"}


class WeatherType(Enum):
    """Enumerable holding the possible weather types that can be queried against by the Sentera Weather API."""

    Recent = "recent"
    Historical = "historical"
    SevenDay = "seven-day-forecast"
    # Forecast = "forecast"
    # Current = "current"

    def __str__(self):
        """Return the value of the WeatherType Enum as a string."""
        return str(self.value)

    @classmethod
    def has_value(cls, value):
        """Class method to return chosen WeatherType value."""
        return value in cls._value2member_map_


class WeatherVariable(Enum):
    """Enumerable holding the possible weather variables that can be queried against by the Sentera Weather API."""

    Temperature = "temperature"
    Humidity = "relative-humidity"
    HighTemperature = "high-temperature"
    LowTemperature = "low-temperature"
    Precipitation = "precipitation"
    WindSpeed = "wind-speed"
    Undefined = "undefined"

    def __str__(self):
        """Return the value of the WeatherVariable Enum as a string."""
        return str(self.value)

    @classmethod
    def has_value(cls, value):
        """Class method to return chosen WeatherVariable value."""
        return value in cls._value2member_map_

    @classmethod
    def _missing_(cls, value):
        return WeatherVariable.Undefined


class WeatherInterval(Enum):
    """Enumerable holding the possible weather intervals that can be queried against by the Sentera Weather API."""

    Hourly = "hourly"
    Daily = "daily"
    Undefined = "undefined"

    def __str__(self):
        """Return the value of the WeatherInterval Enum as a string."""
        return str(self.value)

    @classmethod
    def has_value(cls, value):
        """Class method to return chosen WeatherInterval value."""
        return value in cls._value2member_map_

    @classmethod
    def _missing_(cls, value):
        return WeatherInterval.Undefined


TIME_COLUMNS = {WeatherInterval.Hourly: "validTime", WeatherInterval.Daily: "validDate"}
PARAMETER_COMBINATIONS = {
    WeatherType.Recent: {
        WeatherInterval.Hourly: [
            WeatherVariable.Temperature,
            WeatherVariable.Humidity,
            WeatherVariable.Precipitation,
            WeatherVariable.WindSpeed,
        ],
        WeatherInterval.Daily: [
            WeatherVariable.HighTemperature,
            WeatherVariable.LowTemperature,
            WeatherVariable.Precipitation,
        ],
    },
    WeatherType.Historical: {
        WeatherInterval.Daily: [
            WeatherVariable.HighTemperature,
            WeatherVariable.LowTemperature,
            WeatherVariable.Precipitation,
        ]
    },
}


def build_weather_url(weather_type, weather_variable, weather_interval, lat, long):
    """
    Construct the query URL to be passed as a request to the Weather API.

    :param weather_type: Choice of weather type, as an instance of the ``sentera.weather.WeatherType`` Enum
    :param weather_variable: Choice of weather variable, as an instance of the ``sentera.weather.WeatherVariable`` Enum
    :param weather_interval: Choice of weather interval, as an instance of the ``sentera.weather.WeatherInterval`` Enum
    :param lat: Latitude coordinate at which to query weather at.
    :param long: Longitude coordinate at which to query weather at.
    :return: Constructed query URL, as string.
    """
    if weather_type == WeatherType.SevenDay:
        return Configuration().weather_api_url(
            "/{}/{}/{}".format(str(weather_type), str(lat), str(long))
        )

    else:
        try:
            if (
                weather_variable
                not in PARAMETER_COMBINATIONS[weather_type][weather_interval]
            ):
                raise KeyError
        except KeyError:
            raise ValueError(
                f"Parameter combination not allowed: {weather_type}, {weather_variable}, {weather_interval}"
            )

        return Configuration().weather_api_url(
            "/{}/{}-{}/{}/{}".format(
                str(weather_type),
                weather_interval,
                weather_variable,
                str(lat),
                str(long),
            )
        )


def create_params(weather_type, time_interval):
    """
    Construct query parameter dict to be passed as a request to the Weather API.

    :param weather_type: Choice of weather type, as an instance of the ``sentera.weather.WeatherType`` Enum
    :param time_interval: Time interval, as a list of strings that conform to the **YYYY/MM/DD** ISO8601 format.
    :return: param_dict: Dict of query parameters.
    """
    param_dict = {"start": time_interval[0], "end": time_interval[1]}

    if weather_type == WeatherType.Historical:
        param_dict["years"] = 10

    return param_dict


WEATHER_STRINGS = {
    WeatherType.Recent: {"format": "%Y/%m/%d", "date_string": "YYYY/MM/DD"},
    WeatherType.Historical: {"format": "%m/%d", "date_string": "MM/DD"},
}


def check_time_interval(time_interval, weather_type):
    """
        Cehck the time interval.

    :param time_interval:
    :param weather_type:
    :return:
    """
    if not time_interval:
        raise ValueError("Time interval needed for recent weather types")
    try:
        start = datetime.datetime.strptime(
            time_interval[0], WEATHER_STRINGS[weather_type]["format"]
        )
        end = datetime.datetime.strptime(
            time_interval[1], WEATHER_STRINGS[weather_type]["format"]
        )
    except ValueError:
        raise ValueError(
            "Incorrect time interval format, should be",
            WEATHER_STRINGS[weather_type]["date_string"],
        )
    return start, end


def split_time_interval(time_interval, weather_type, weather_interval):
    """
    Create the list of time intervals to be passed to each request made to the Weather API.

    When the user requests data at a higher temporal resolution than that of the overall supplied time interval,
    multiple requests need to be constructed and executed. For example, if the user requests hourly temperature data
    for an entire week, a request must be constructed for every hour within the interval. This function constructs a
    list of those sub-intervals within the overall interval to be used to construct the queries.

    :param time_interval: Overall time interval of request, in **YYYY/MM/DD** ISO8601 format.
    :param weather_type: Choice of weather type, as an instance of the ``sentera.weather.WeatherType`` Enum
    :param weather_interval: Choice of weather interval, as an instance of the ``sentera.weather.WeatherInterval`` Enum
    :return: time_intervals: List of individual intervals to be constructed into individual queries
    """
    if weather_type == WeatherType.Recent:
        start, end = check_time_interval(time_interval, weather_type)
        today = datetime.datetime.today()
        if (today - start).days > 730:
            raise ValueError(
                f"Start date is over 2 years ago."
                f"Earliest allowable start date is {(today - datetime.timedelta(days=730)).date()}"
            )

        if weather_interval == WeatherInterval.Daily:
            delta = datetime.timedelta(days=90)
        else:
            delta = datetime.timedelta(days=5)

        time_intervals = []
        current_time = start
        next_time = start + delta
        while next_time < end:
            time_intervals.append(
                [current_time.strftime("%Y/%m/%d"), next_time.strftime("%Y/%m/%d")]
            )
            current_time = next_time
            next_time = current_time + delta
        time_intervals.append(
            [current_time.strftime("%Y/%m/%d"), end.strftime("%Y/%m/%d")]
        )

        return time_intervals

    elif weather_type == WeatherType.Historical:
        start, end = check_time_interval(time_interval, weather_type)
        diff = (end - start).days
        if diff >= 0:
            return [[time_interval[0], time_interval[1]]]
        else:
            return [[time_interval[0], "12-31"], ["01-01", time_interval[1]]]

    elif weather_type == WeatherType.SevenDay:
        return [["", ""]]

    return None


def _combine_seven_day(url, response_json, data_df):
    data = json_normalize(response_json)

    data["lat"] = re.findall(r"\D+/(-?[0-9]+.[0-9]+)/(-?[0-9]+.[0-9]+)", url)[0][0]
    data["long"] = re.findall(r"\D+/(-?[0-9]+.[0-9]+)/(-?[0-9]+.[0-9]+)", url)[0][1]

    return pd.concat([data_df, data], axis=0)


def _merge_to_full_df(weather_variable, weather_interval, response_json, data_df):
    data = json_normalize(response_json["series"])
    data = data.rename(columns={"value": str(weather_variable)}).drop(
        columns=["products"]
    )
    data["lat"] = response_json["latitude"]
    data["long"] = response_json["longitude"]

    data_df = data_df.merge(
        data,
        on=[TIME_COLUMNS[weather_interval], "lat", "long"],
        how="outer",
        suffixes=["", "_"],
    )
    if str(weather_variable) + "_" in data_df:
        indx = data_df[str(weather_variable) + "_"].notnull()
        data_df.loc[indx, str(weather_variable)] = data_df.loc[
            indx, str(weather_variable) + "_"
        ]
        data_df.drop(str(weather_variable) + "_", inplace=True, axis=1)

    return data_df


@retry(
    retry=retry_if_exception_type(aiohttp.ClientError),
    wait=wait_random(min=0.25, max=0.75),
    stop=stop_after_attempt(5),
)
async def _fetch(url, session, weather_variable, time_interval, weather_type):
    async with session.get(
        url, params=create_params(weather_type, time_interval), raise_for_status=True,
    ) as response:
        return await response.read(), weather_variable, url


async def run_queries(
    url_list,
    weather_variable_list,
    time_interval_list,
    weather_interval,
    weather_type,
    sentera_api_key=None,
):
    """
    Make a series of asynchronous requests to the Weather API.

    Each of these requests is composed of a URL string and a parameter dictionary, constructed based on values passed
    to the ``create_params`` and ``build_weather_url`` functions within this module. Each request is made with simple
    retry logic, so guard against the occasional server error. The results of the requests are then iteratively stored
    in a pandas DataFrame and eventually returned once all requests have completed.

    :param url_list: List of request URLS
    :param weather_variable_list: List of weather variables, as instances of the ``sentera.weather.WeatherVariable`` Enum
    :param time_interval_list: List of time intervals for each request
    :param weather_interval: List of weather intervals, as instances of the ``sentera.weather.WeatherInterval`` Enum
    :param weather_type: List of weather types, as instances of the ``sentera.weather.WeatherType`` Enum
    :param sentera_api_key: (optional) A Sentera key giving access to the data. Has a default hard coded value that works.
    :return: data_df: Pandas DataFrame of request results
    """
    tasks = []

    if sentera_api_key:
        WEATHER_HEADER["X-API-Key"] = sentera_api_key

    async with aiohttp.ClientSession(headers=WEATHER_HEADER) as session:
        for url, weather_variable, time_interval in zip(
            url_list, weather_variable_list, time_interval_list
        ):
            task = asyncio.ensure_future(
                _fetch(url, session, weather_variable, time_interval, weather_type)
            )
            tasks.append(task)

        if weather_type == WeatherType.SevenDay:
            data_df = pd.DataFrame()
        else:
            data_df = pd.DataFrame(
                columns=[TIME_COLUMNS[weather_interval], "lat", "long"]
            )

        disable_tqdm = strtobool(os.environ.get("DISABLE_TQDM") or "false")
        for f in tqdm.tqdm(
            asyncio.as_completed(tasks), total=len(tasks), disable=disable_tqdm
        ):
            response, weather_variable, url = await f
            response_json = json.loads(response)
            if weather_type == WeatherType.SevenDay:
                data_df = _combine_seven_day(url, response_json, data_df)
            else:
                data_df = _merge_to_full_df(
                    weather_variable, weather_interval, response_json, data_df
                )

    return data_df
