from enum import Enum
import posixpath

WEATHER_BASE_URL = "https://weather.sentera.com"
WEATHER_HEADER = {'X-API-Key': 'mc049Cu9FJ3lHiQYDYQTd3ZOzsOBt29d2gyi3e0r'}


class WeatherType(Enum):
    Recent = "recent"
    Historical = "historical"
    Forecast = "forecast"
    Current = "current"

    def __str__(self):
        return str(self.value)

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_


class WeatherVariable(Enum):
    Temperature = "temperature"
    Humidity = "relative-humidity"
    # DewPoint = "DewPoint"
    # WindSpeed = "WindSpeed"
    # WindDirection = "WindDirection"
    # Precipitation = "Precipitation"
    # SolarRadiation = "SolarRadiation"

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


def build_weather_url(type, variable, interval, lat, long):
    return posixpath.join(WEATHER_BASE_URL, str(type), f"{interval}-{variable}", str(lat), str(long))


def create_params(weather_variable, time_interval):
    if weather_variable == WeatherVariable.Temperature:
        return {
            'start': time_interval[0],
            'end': time_interval[1],
            'unit': 'fahrenheit'
        }

    if weather_variable == WeatherVariable.Humidity:
        return {
            'start': time_interval[0],
            'end': time_interval[1]
        }

    raise ValueError(f"Weather variable not supported: {weather_variable}")
