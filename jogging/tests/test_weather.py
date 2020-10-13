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
from unittest.mock import patch

from django.conf import settings

from jogging.weather import get_weather


@patch("jogging.weather.meta_weather")
class GetWeatherTestCase(unittest.TestCase):
    def test_calls_right_provider_instance(self, pmeta_weather):
        settings.WEATHER = {"PROVIDER": "meta_weather"}
        weather = get_weather("Here", "2020/09/17")
        pmeta_weather.assert_called_once_with("Here", "2020/09/17")
        self.assertEqual(pmeta_weather.return_value, weather)
        
    def test_unknown_provider_returns_None(self, pmeta_weather):
        settings.WEATHER = {"PROVIDER": "unkwnown_wheather_provider"}
        weather = get_weather("There", "2020/09/13")
        self.assertIs(weather, None)
