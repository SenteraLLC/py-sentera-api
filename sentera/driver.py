import asyncio

import requests
from pandas import json_normalize


from sentera import weather
from sentera import api
import pandas as pd
import sentera


def main():
    print("hello")
    # time_interval = ['2020/10/01', '2020/10/03']
    # print(api.get_weather('recent', [[45.000,-90.000]],'temperature', None, time_interval))
    HOURLY_WEATHER_VARIABLES = ["temperature", "relative-humidity", "precipitation", "evapotranspiration-tall-crop"]
    WEATHER_TYPE_RECENT = "recent"
    WEATHER_INTERVAL_HOURLY = "hourly"
    time_interval = ['2020/10/01', '2020/10/02']
    response = sentera.api.get_weather(
        WEATHER_TYPE_RECENT,
        [[45.000, -90.000]],
        HOURLY_WEATHER_VARIABLES,
        WEATHER_INTERVAL_HOURLY,
        time_interval,
    )
    pd.set_option('display.max_columns', None)
    print(response)

    # print("what?")

if __name__=="__main__":
    main()