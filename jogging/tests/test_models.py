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

from django.test import TestCase

from jogging.models import Run


class RunTestCase(TestCase):
    def test_can_be_saved(self):
        run = Run(
            date=date.today(),
            distance=2.5,
            time=timedelta(minutes=3, seconds=9),
            location="Lima"
        )
        run.save()
        self.assertEqual(Run.objects.count(), 1)
        saved = Run.objects.first()
        self.assertEqual(saved.date, date.today())
        self.assertEqual(saved.distance, 2.5)
        self.assertEqual(saved.time, timedelta(minutes=3, seconds=9))
        self.assertEqual(saved.location, "Lima")
