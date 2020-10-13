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


from django.conf import settings
import requests


META_WEATHER_BASE_URL = "https://www.metaweather.com/api/"
META_WEATHER_LOCATION_SEARCH_URL = META_WEATHER_BASE_URL + "location/search/"


meta_weather = None


def _meta_weather_location_id(location):
    response = requests.get(
        META_WEATHER_LOCATION_SEARCH_URL,
        params={"query": location}
    )
    data = response.json()
    return data[0]["woeid"]


def get_weather(location, date):
    try:
        provider = globals()[settings.WEATHER["PROVIDER"]]
    except KeyError:
        pass
    try:
        return provider(location, date)
    except:
        pass

