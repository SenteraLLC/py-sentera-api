import requests
from sentera import weather
from pandas.io.json import json_normalize
import datetime
import json
import pandas as pd


def _run_sentera_query(query, token):
    headers = {'Authorization': token}
    request = requests.post(url='https://api.sentera.com/graphql', json=query, headers=headers)
    if request.status_code != 200:
        raise Exception("Request Failed {}. {}".format(request.status_code, query))

    return request.json()


def _run_weather_query(url, params):
    request = requests.get(url=url,
                           params=params,
                           headers=weather.WEATHER_HEADER)
    if request.status_code != 200:
        raise Exception(f"Request Failed {request.status_code}. {url} - {params}")

    return json.loads(request.content)


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


def get_weather(weather_type, weather_variables, weather_interval, time_interval, field_name=None, field_location=None, field_id=None, token=None):
    """
    Returns a pandas dataframe with desired weather information

    :param weather_type: either a string (e.g. *'recent'*) or :code:`sentera.weather.WeatherType`
    :param weather_variables: list of strings (e.g. *['temperature', 'relative-humidity']*) or
                              list of :code:`sentera.weather.WeatherVariable`'s
    :param weather_interval: either a string (e.g. *'hourly'*) or :code:`sentera.weather.WeatherInterval`
    :param time_interval: [*day_start*, *day_end*] in format **YYYY/MM/DD** (eg. *['2020/01/01', '2020/01/03']*)
    :param field_name: name of field. **Optional**, could instead specify *field_location* or *field_id*
    :param field_location: [*lat*, *long*]. **Optional**, could instead specify *field_name* or *field_id*
    :param field_id: Sentera id of field. **Optional**, could instead specify *field_name** or **field_location*
    :param token: Sentera auth token returned from :code:`sentera.auth.get_auth_token()`.
                  Needed if accessing fields by *field_name* or *field_id*
    :return: **weather_dataframe** - pandas dataframe
    """

    if not field_name and not field_location and not field_id:
        raise ValueError("A location needs to be specified by either field name, id, or [lat, long] pair")

    if field_name:
        if token:
            fields = get_all_fields(token)
        else:
            raise ValueError("Sentera auth token needed to access fields by name")
        field_df = fields[fields["name"] == field_name]
        if field_df.empty:
            raise ValueError(f"Couldn't find field named: {field_name}")
        field_df = field_df.iloc[0]
        field_location = [field_df["latitude"], field_df["longitude"]]
    elif field_id:
        if token:
            fields = get_all_fields(token)
        else:
            raise ValueError("Sentera auth token needed to access fields by name")
        field_df = fields[fields["sentera_id"] == field_id].iloc[0]
        field_location = [field_df["latitude"], field_df["longitude"]]

    weather_type = weather.WeatherType(weather_type)
    weather_interval = weather.WeatherInterval(weather_interval)

    try:
        datetime.datetime.strptime(time_interval[0], '%Y/%m/%d')
    except ValueError:
        raise ValueError("Incorrect time interval format, should be YYYY/MM/DD")

    try:
        datetime.datetime.strptime(time_interval[1], '%Y/%m/%d')
    except ValueError:
        raise ValueError("Incorrect time interval format, should be YYYY/MM/DD")

    data_df = pd.DataFrame(columns=["validTime"])
    for weather_variable in weather_variables:
        weather_variable = weather.WeatherVariable(weather_variable)
        weather_url = weather.build_weather_url(weather_type,
                                                weather_variable,
                                                weather_interval,
                                                field_location[0],
                                                field_location[1])
        data = json_normalize(_run_weather_query(weather_url, weather.create_params(weather_variable, time_interval))['series'])
        data = data.rename(columns={"value": str(weather_variable)}).drop(columns=["products"])
        data_df = pd.merge(data, data_df, on="validTime", how="outer")
    return data_df
