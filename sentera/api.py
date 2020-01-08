import requests
from sentera import weather
from pandas.io.json import json_normalize
import datetime
import json
import pandas as pd
import aiohttp
import asyncio
import tqdm

counter = 0


def _run_sentera_query(query, token):
    headers = {'Authorization': token}
    request = requests.post(url='https://api.sentera.com/graphql', json=query, headers=headers)
    if request.status_code != 200:
        raise Exception("Request Failed {}. {}".format(request.status_code, query))

    return request.json()


async def _fetch(url, session, weather_variable, time_interval, weather_type):
    num_retries = 0
    while num_retries < 10:
        try:
            async with session.get(url,
                                   params=weather.create_params(weather_type, time_interval),
                                   raise_for_status=True) as response:
                return await response.read(), weather_variable
        except aiohttp.ClientError as e:
            print(e)
            # sleep a little and try again
            await asyncio.sleep(1)
            num_retries += 1

    raise aiohttp.ClientError(f"Couldn't access data from {url} from {time_interval[0]} to {time_interval[1]}")


async def _run_weather_queries_past(url_list, weather_variable_list, time_interval, weather_interval, weather_type):
    tasks = []

    async with aiohttp.ClientSession(headers=weather.WEATHER_HEADER) as session:
        for url, weather_variable in zip(url_list, weather_variable_list):
            task = asyncio.ensure_future(_fetch(url, session, weather_variable, time_interval, weather_type))
            tasks.append(task)

        data_df = pd.DataFrame(columns=[weather.TIME_COLUMNS[weather_interval], "lat", "long"])
        for f in tqdm.tqdm(asyncio.as_completed(tasks), total=len(tasks)):
            response, weather_variable = await f
            try:
                response_json = json.loads(response)
                data = json_normalize(response_json['series'])
                data = data.rename(columns={"value": str(weather_variable)}).drop(columns=["products"])
                data["lat"] = response_json['latitude']
                data["long"] = response_json['longitude']

                data_df = data_df.merge(data,
                                        on=[weather.TIME_COLUMNS[weather_interval], "lat", "long"],
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


def get_all_fields(token):
    """
    Returns a pandas dataframe with information on each field within the user's account
    (*sentera_id*, *name*, *latitude*, *longitude*)

    :param token: Sentera auth token returned from :code:`sentera.auth.get_auth_token()`.
    :return: **fields_dataframe** - pandas dataframe
    """
    query = {'query': 'query AllFields{ fields { total_count results{sentera_id name latitude longitude}}}'}
    result = _run_sentera_query(query, token)
    data = result['data']['fields']['results']
    return json_normalize(data)


async def get_weather(weather_type, weather_variables, weather_interval, time_interval=None, field_names=None,
                      field_locations=None, field_ids=None, token=None):
    """
    Returns a pandas dataframe with desired weather information

    :param weather_type: either a string (e.g. *'recent'*) or :code:`sentera.weather.WeatherType`
    :param weather_variables: list of strings (e.g. *['temperature', 'relative-humidity']*) or
                              list of :code:`sentera.weather.WeatherVariable`'s
    :param weather_interval: either a string (e.g. *'hourly'*) or :code:`sentera.weather.WeatherInterval`
    :param time_interval: [*day_start*, *day_end*] in format **YYYY/MM/DD** (eg. *['2020/01/01', '2020/01/03']*).
                          Needed for *recent* weather types, but no others.
    :param field_names: list of names of fields. **Optional**, could instead specify *field_locations* or *field_ids*
    :param field_locations: list of [*lat*, *long*] pairs. **Optional**, could instead specify *field_names* or
                            *field_ids*
    :param field_ids: list of Sentera ids of fields. **Optional**, could instead specify *field_names** or
                      **field_locations*
    :param token: Sentera auth token returned from :code:`sentera.auth.get_auth_token()`.
                  Needed if accessing fields by *field_name* or *field_id*
    :return: **weather_dataframe** - pandas dataframe
    """
    if not field_names and not field_locations and not field_ids:
        raise ValueError("Locations need to be specified by either field names, ids, or [lat, long] pairs")

    if field_names:
        if token:
            fields = get_all_fields(token)
        else:
            raise ValueError("Sentera auth token needed to access fields by name")

        field_locations = []
        for field_name in field_names:
            field_df = fields[fields["name"] == field_name]
            if field_df.empty:
                raise ValueError(f"Couldn't find field named: {field_name}")
            field_df = field_df.iloc[0]
            field_locations.append([field_df["latitude"], field_df["longitude"]])
    elif field_ids:
        if token:
            fields = get_all_fields(token)
        else:
            raise ValueError("Sentera auth token needed to access fields by name")

        field_locations = []
        for field_id in field_ids:
            field_df = fields[fields["sentera_id"] == field_id]
            if field_df.empty:
                raise ValueError(f"Couldn't find field id: {field_id}")
            field_df = field_df.iloc[0]
            field_locations.append([field_df["latitude"], field_df["longitude"]])

    weather_type = weather.WeatherType(weather_type)
    weather_interval = weather.WeatherInterval(weather_interval)

    if weather_type == weather.WeatherType.Recent:
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

    url_list = []
    weather_variables_list = []

    # time_intervals = split_time_interval(start, end, weather_type)

    for field_location in field_locations:
        for weather_variable in weather_variables:
            weather_variable = weather.WeatherVariable(weather_variable)
            weather_url = weather.build_weather_url(weather_type,
                                                    weather_variable,
                                                    weather_interval,
                                                    field_location[0],
                                                    field_location[1])
            url_list.append(weather_url)
            weather_variables_list.append(weather_variable)

    return await _run_weather_queries_past(url_list,
                                           weather_variables_list,
                                           time_interval,
                                           weather_interval,
                                           weather_type)
