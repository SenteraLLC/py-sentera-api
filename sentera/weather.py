from enum import Enum
import posixpath
import datetime
import json
import pandas as pd
from pandas.io.json import json_normalize
import aiohttp
import asyncio
import tqdm

WEATHER_BASE_URL = "https://weather.sentera.com"
WEATHER_HEADER = {'X-API-Key': 'mc049Cu9FJ3lHiQYDYQTd3ZOzsOBt29d2gyi3e0r'}


class WeatherType(Enum):
    Recent = "recent"
    Historical = "historical"
    # Forecast = "forecast"
    # Current = "current"

    def __str__(self):
        return str(self.value)

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_


class WeatherVariable(Enum):
    Temperature = "temperature"
    Humidity = "relative-humidity"
    HighTemperature = "high-temperature"
    LowTemperature = "low-temperature"
    Precipitation = "precipitation"

    def __str__(self):
        return str(self.value)

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_


class WeatherInterval(Enum):
    Hourly = "hourly"
    Daily = "daily"

    def __str__(self):
        return str(self.value)

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_


TIME_COLUMNS = {WeatherInterval.Hourly: "validTime", WeatherInterval.Daily: "validDate"}
PARAMETER_COMBINATIONS = {
                            WeatherType.Recent:
                            {
                                WeatherInterval.Hourly:
                                    [WeatherVariable.Temperature,
                                     WeatherVariable.Humidity],
                                WeatherInterval.Daily:
                                    [WeatherVariable.HighTemperature,
                                     WeatherVariable.LowTemperature,
                                     WeatherVariable.Precipitation]
                            },
                            WeatherType.Historical:
                            {
                                WeatherInterval.Daily:
                                    [WeatherVariable.HighTemperature,
                                     WeatherVariable.LowTemperature,
                                     WeatherVariable.Precipitation]
                            }
                         }


def build_weather_url(weather_type, weather_variable, weather_interval, lat, long):
    try:
        if weather_variable not in PARAMETER_COMBINATIONS[weather_type][weather_interval]:
            raise KeyError
    except KeyError:
        raise ValueError(f"Parameter combination not allowed: {weather_type}, {weather_variable}, {weather_interval}")

    return posixpath.join(WEATHER_BASE_URL,
                          str(weather_type),
                          f"{weather_interval}-{weather_variable}",
                          str(lat),
                          str(long))


def create_params(weather_type, time_interval):
    param_dict = {'start': time_interval[0], 'end': time_interval[1]}

    if weather_type == WeatherType.Historical:
        param_dict['years'] = 10

    return param_dict


def split_time_interval(time_interval, weather_type, weather_interval):
    if weather_type == WeatherType.Recent:
        if not time_interval:
            raise ValueError("Time interval needed for recent weather types")
        try:
            start = datetime.datetime.strptime(time_interval[0], '%Y/%m/%d')
        except ValueError:
            raise ValueError("Incorrect time interval format, should be YYYY/MM/DD")

        try:
            end = datetime.datetime.strptime(time_interval[1], '%Y/%m/%d')
        except ValueError:
            raise ValueError("Incorrect time interval format, should be YYYY/MM/DD")

        today = datetime.datetime.today()
        if (today - start).days > 730:
            raise ValueError(f"Start date is over 2 years ago."
                             f"Earliest allowable start date is {(today - datetime.timedelta(days=730)).date()}")

        if weather_interval == WeatherInterval.Daily:
            delta = datetime.timedelta(days=90)
        else:
            delta = datetime.timedelta(days=5)

        time_intervals = []
        current_time = start
        next_time = start + delta
        while next_time < end:
            time_intervals.append([current_time.strftime("%Y/%m/%d"), next_time.strftime("%Y/%m/%d")])
            current_time = next_time
            next_time = current_time + delta
        time_intervals.append([current_time.strftime("%Y/%m/%d"), end.strftime("%Y/%m/%d")])

        return time_intervals

    elif weather_type == WeatherType.Historical:
        return [["01-01", "07-01"], ["07-01", "12-31"]]

    return None


async def _fetch(url, session, weather_variable, time_interval, weather_type):
    num_retries = 0
    while num_retries < 5:
        try:
            async with session.get(url,
                                   params=create_params(weather_type, time_interval),
                                   raise_for_status=True) as response:
                return await response.read(), weather_variable
        except aiohttp.ClientError as e:
            await asyncio.sleep(1)
            num_retries += 1

    raise aiohttp.ClientError(f"Couldn't access data from {url} from {time_interval[0]} to {time_interval[1]}")


async def run_queries(url_list, weather_variable_list, time_interval_list, weather_interval, weather_type):
    tasks = []

    async with aiohttp.ClientSession(headers=WEATHER_HEADER) as session:
        for url, weather_variable, time_interval in zip(url_list, weather_variable_list, time_interval_list):
            task = asyncio.ensure_future(_fetch(url, session, weather_variable, time_interval, weather_type))
            tasks.append(task)

        data_df = pd.DataFrame(columns=[TIME_COLUMNS[weather_interval], "lat", "long"])
        for f in tqdm.tqdm(asyncio.as_completed(tasks), total=len(tasks)):
            response, weather_variable = await f
            try:
                response_json = json.loads(response)
                data = json_normalize(response_json['series'])
                data = data.rename(columns={"value": str(weather_variable)}).drop(columns=["products"])
                data["lat"] = response_json['latitude']
                data["long"] = response_json['longitude']

                data_df = data_df.merge(data,
                                        on=[TIME_COLUMNS[weather_interval], "lat", "long"],
                                        how="outer",
                                        suffixes=["", "_"])
                if str(weather_variable) + "_" in data_df:
                    indx = data_df[str(weather_variable) + "_"].notnull()
                    data_df.loc[indx, str(weather_variable)] = data_df.loc[indx, str(weather_variable) + "_"]
                    data_df.drop(str(weather_variable) + "_", inplace=True, axis=1)
            except Exception as e:
                print(response)
                raise e

    return data_df
