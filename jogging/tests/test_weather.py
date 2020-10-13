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

import unittest
from unittest.mock import patch, MagicMock
import json
from datetime import date

from django.conf import settings

from jogging.weather import get_weather, _meta_weather_location_id, meta_weather


FICTICIOUS_METAWEATHER_DATA = [
    {
        'id': 6228000409387008,
        'weather_state_name': 'Clear',
        'weather_state_abbr': 'c',
        'wind_direction_compass': 'WNW',
        'created': '2020-10-13T12:36:55.891535Z',
        'applicable_date': '2020-10-13',
        'min_temp': 9.005,
        'max_temp': 21.095,
        'the_temp': 19.45,
        'wind_speed': 3.9686499990455744,
        'wind_direction': 291.5018201050529,
        'air_pressure': 1018.0,
        'humidity': 51,
        'visibility': 14.642922830668894,
        'predictability': 68
    },
    {
        'id': 4758843897675776,
        'weather_state_name': 'Light Cloud',
        'weather_state_abbr': 'lc',
        'wind_direction_compass': 'WNW',
        'created': '2020-10-13T09:36:56.188551Z',
        'applicable_date': '2020-10-13',
        'min_temp': 8.88,
        'max_temp': 20.855,
        'the_temp': 19.415,
        'wind_speed': 4.039265499045574,
        'wind_direction': 291.5018201050529,
        'air_pressure': 1018.0,
        'humidity': 52,
        'visibility': 13.791954982899865,
        'predictability': 68
    },
    {
        'id': 6313604271833088,
        'weather_state_name': 'Light Cloud',
        'weather_state_abbr': 'lc',
        'wind_direction_compass': 'ESE',
        'created': '2020-10-08T03:37:11.283720Z',
        'applicable_date': '2020-10-13',
        'min_temp': 6.93,
        'max_temp': 19.595,
        'the_temp': 17.21,
        'wind_speed': 2.2789376043903604,
        'wind_direction': 103.50000000000004,
        'air_pressure': 1021.0,
        'humidity': 48,
        'visibility': 9.999726596675416,
        'predictability': 70
    },
]


class UnknownError(Exception):
    ...



@patch("jogging.weather.meta_weather")
class GetWeatherTestCase(unittest.TestCase):
    def test_calls_right_provider_instance(self, pmeta_weather):
        settings.WEATHER = {"PROVIDER": "meta_weather"}
        weather = get_weather("Here", "2020/09/17")
        pmeta_weather.assert_called_once_with("Here", "2020/09/17")
        self.assertEqual(pmeta_weather.return_value, weather)
        
    def test_returns_None_unknown_provider(self, pmeta_weather):
        settings.WEATHER = {"PROVIDER": "unkwnown_weather_provider"}
        weather = get_weather("There", "2020/09/13")
        self.assertIs(weather, None)

    def test_returns_None_if_error_in_provider(self, pmeta_weather):
        settings.WEATHER = {"PROVIDER": "meta_weather"}
        pmeta_weather.side_effect = UnknownError
        weather = get_weather("Wandalucia", "2010/02/22")
        self.assertIs(weather, None)
        

@patch("jogging.weather.requests.get")
class MetaWeatherLocationIDTestCase(unittest.TestCase):
    def test_fetches_data_from_server(self, pget):
        mresponse = MagicMock()
        mresponse.json.return_value = [{"woeid": 123456}]
        pget.return_value = mresponse
        location_id = _meta_weather_location_id("Juan Francisco")
        self.assertEqual(location_id, 123456)

    def test_get_called_with_correct_url(self, pget):
        location_id = _meta_weather_location_id("Juan Francisco")
        pget.assert_called_once_with(
            "https://www.metaweather.com/api/location/search/",
            params={"query": "Juan Francisco"}
        )

    def test_returns_None_if_unexpected_data_fetched(self, pget):
        mresponse = MagicMock()
        values = ([], [{}])
        for value in values:
            with self.subTest(value=value):
                mresponse.json.return_value = value
                pget.return_value = mresponse
                location_id = _meta_weather_location_id("Juan Francisco")
                self.assertEqual(location_id, None)


@patch("jogging.weather._meta_weather_location_id")
@patch("jogging.weather.requests.get")
class MetaWeatherTestCase(unittest.TestCase):
    def test_called_with_correct_url(self, pget, pmeta_weather_location_id):
        pmeta_weather_location_id.return_value = 23
        meta_weather("Mandril", date(2020, 7, 15))
        pget.assert_called_once_with(
            "https://www.metaweather.com/api/location/23/2020/7/15/",
        )

    def test_returns_according_to_servers_fetched_data(
            self, pget, pmeta_weather_location_id):
        mresponse = MagicMock()
        mresponse.json.return_value = FICTICIOUS_METAWEATHER_DATA
        pget.return_value = mresponse
        weather = meta_weather("Madrid", date(2020, 10, 13))
        self.assertEqual(weather, "Clear")
