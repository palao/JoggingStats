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


from datetime import date, timedelta
from unittest.mock import patch

from django.test import TestCase
from django.contrib.auth.models import User

from jogging.models import Run, WeeklyReport


@patch("jogging.models.get_weather")
class RunTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="x")
        self.run = Run(
            date=date.today(),
            distance=2.5,
            time=timedelta(minutes=3, seconds=9),
            location="Lima",
            owner=self.user,
        )
        
    def test_can_be_saved(self, pget_weather):
        pget_weather.return_value = "Cloudy"
        self.run.save()
        self.assertEqual(Run.objects.count(), 1)
        saved = Run.objects.first()
        self.assertEqual(saved.date, date.today())
        self.assertEqual(saved.distance, 2.5)
        self.assertEqual(saved.time, timedelta(minutes=3, seconds=9))
        self.assertEqual(saved.location, "Lima")
        self.assertEqual(saved.owner, self.user)

    def test_has_weather_field_set_from_get_weather(self, pget_weather):
        pget_weather.return_value = "Some weather"
        self.run.save()
        self.assertEqual(self.run.weather, "Some weather")
        
    def test_leaves_default_value_if_get_weather_is_None(self, pget_weather):
        pget_weather.return_value = None
        self.run.save()
        self.assertEqual(self.run.weather, "?")
        

class WeeklySummaryTestCase(TestCase):
    def test_can_be_saved(self):
        user = User.objects.create(username="sam")
        r = WeeklyReport(
            week_start=date(2020,10,5),
            total_distance_km=23.5,
            average_speed_kmph=12,
            owner=user
        )
        r.save()
        saved = WeeklyReport.objects.first()
        self.assertEqual(saved.week_start, date(2020,10,5))
        self.assertEqual(saved.total_distance_km, 23.5)
        self.assertEqual(saved.average_speed_kmph, 12)
        self.assertEqual(saved.owner, user)
        
