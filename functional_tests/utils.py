########################################################################
#
#  Copyright (c) 2020 David Palao
#
#  This file is part of JoggingStats.
#
#  JoggingStats is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  JoggingStats is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with JoggingStats. If not, see <http://www.gnu.org/licenses/>.
#
########################################################################

import json

import requests
from django.conf import settings


OWM_URL =  "http://api.openweathermap.org/data/2.5/weather"


def get_weather_openweathermap(location):
    key = settings.WEATHER["APPID"]
    resp = requests.get(OWM_URL, data={"q": location, "appid": key})
    result = json.loads(resp.content)
    try:
        weather = result["weather"]["main"]
    except KeyError:
        weather = "?"
    return weather


get_weather = get_weather_openweathermap
