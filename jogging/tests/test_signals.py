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

import datetime
from unittest.mock import MagicMock, patch

from django.test import TestCase
from django.contrib.auth.models import User

from jogging.signals import run_save_handler, run_stats_for_report
from jogging.models import WeeklyReport, Run


class FakeRun:
    def __init__(self, date, owner):
        self.date = date
        self.owner = owner


class StatsForReportTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="mn")
        another_user = User.objects.create(username="yt")
        with patch("jogging.models.get_weather") as pget_weather:
            pget_weather.return_value = "Sunny"
            self.runs = [
                Run.objects.create(
                    date=datetime.date(2020, 10, 5),
                    distance=2.5,
                    time=datetime.timedelta(minutes=3, seconds=9),
                    location="Buenos Aires",
                    owner=self.user,
                ),
                Run.objects.create(
                    date=datetime.date(2020, 10, 6),
                    distance=5.4,
                    time=datetime.timedelta(minutes=21, seconds=20),
                    location="Buenos Aires",
                    owner=self.user,
                ),
                Run.objects.create(
                    date=datetime.date(2020, 9, 28),
                    distance=8.4,
                    time=datetime.timedelta(minutes=38, seconds=52),
                    location="Buenos Aires",
                    owner=self.user,
                ),
                Run.objects.create(
                    date=datetime.date(2020, 10, 6),
                    distance=6.2,
                    time=datetime.timedelta(minutes=22, seconds=45),
                    location="Buenos Aires",
                    owner=another_user,
                )
            ]
        
    def test_stats_for_report_with_one_run_in_a_week(self):
        stats = run_stats_for_report(
            Run,
            self.user,
            datetime.date(2020, 9, 28),
            datetime.date(2020, 9, 30)
        )
        self.assertEqual(stats["distance__sum"], 8.4)
        self.assertEqual(stats["time__sum"].seconds, 2332)
        
    def test_stats_for_report_with_one_run_in_a_week(self):
        stats = run_stats_for_report(
            Run,
            self.user,
            datetime.date(2020, 10, 5),
            datetime.date(2020, 10, 7)
        )
        self.assertEqual(stats["distance__sum"], 7.9)
        self.assertEqual(stats["time__sum"].seconds, 1469)
        
@patch("jogging.signals.run_stats_for_report")
class RunSaveHandler(TestCase):
    def test_calls_run_stats_for_report(self, prun_stats_for_report):
        user = User.objects.create(username="yt")
        # I don't call "create" to avoid calling the handler implicitly:
        run = Run(
            owner=user,
            date=datetime.date(2020, 8, 11),
            distance=3,
            time=datetime.timedelta(minutes=10),
            location="Besq"
        )
        delta = MagicMock()
        delta.seconds = 13171
        stats = {"distance__sum": 45, "time__sum": delta}
        prun_stats_for_report.return_value = stats
        run_save_handler(Run, run)
        prun_stats_for_report.assert_called_once_with(
            Run,
            run.owner,
            datetime.date(2020, 8, 10),
            datetime.date(2020, 8, 16),
        )
        
    def test_creates_WeekleReport_with_data_from_aux_func(
            self, prun_stats_for_report):
        mRun = MagicMock()
        user = User.objects.create(username="mariano")
        run = FakeRun(
            date=datetime.date(2020, 10, 6),
            owner=user
        )
        delta = MagicMock()
        delta.seconds = 13171
        stats = {"distance__sum": 45, "time__sum": delta}
        prun_stats_for_report.return_value = stats
        run_save_handler(mRun, run)
        self.assertEqual(WeeklyReport.objects.count(), 1)
        rep = WeeklyReport.objects.first()
        self.assertEqual(rep.week_start, datetime.date(2020, 10, 5))
        self.assertEqual(rep.total_distance_km, 45)
        self.assertAlmostEqual(rep.average_speed_kmph, 45/13171*3600)
