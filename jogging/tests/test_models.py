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
from django.db.utils import IntegrityError
from django.db import transaction

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
    def setUp(self):
        self.user1 = User.objects.create(username="sam")
        self.user2 = User.objects.create(username="cp")
        self.r1 = WeeklyReport(
            week_start=date(2020,10,5),
            total_distance_km=23.5,
            average_speed_kmph=12,
            owner=self.user1
        )
        
    def test_can_be_saved(self):
        self.r1.save()
        saved = WeeklyReport.objects.first()
        self.assertEqual(saved.week_start, date(2020,10,5))
        self.assertEqual(saved.total_distance_km, 23.5)
        self.assertEqual(saved.average_speed_kmph, 12)
        self.assertEqual(saved.owner, self.user1)

    def test_save_fixes_date(self):
        r = WeeklyReport.objects.create(
            week_start=date(2020,10,14),
            owner=self.user1
        )
        self.assertEqual(r.week_start, date(2020,10,12))
        
    def test_has_default_values(self):
        r = WeeklyReport(
            week_start=date(2020,9,28),
            owner=self.user1
        )
        r.save()
        saved = WeeklyReport.objects.first()
        self.assertEqual(saved.week_start, date(2020,9,28))
        self.assertEqual(saved.total_distance_km, 0)
        self.assertEqual(saved.average_speed_kmph, 0)
        self.assertEqual(saved.owner, self.user1)
        
    def test_one_owner_can_only_have_one_entry_per_date(self):
        self.r1.save()
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                r2 = WeeklyReport.objects.create(
                    week_start=date(2020,10,5),
                    total_distance_km=25.2,
                    average_speed_kmph=12.9,
                    owner=self.user1
                )
        self.assertEqual(WeeklyReport.objects.count(), 1)

    def test_two_owners_can_have_entries_on_same_date(self):
        self.r1.save()
        r2 = WeeklyReport.objects.create(
            week_start=date(2020,10,5),
            total_distance_km=25.2,
            average_speed_kmph=12.9,
            owner=self.user2
        )
        self.assertEqual(WeeklyReport.objects.count(), 2)
        
    def test_has_week_property(self):
        self.r1.save()
        self.assertEqual(self.r1.week, "2020-10-05 to 2020-10-11")
        
