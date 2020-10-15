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

from django.contrib.staticfiles.testing import LiveServerTestCase
import requests

class UserRolesTestCase(LiveServerTestCase):
    def test_superusers_can_CRUD_all_runs_and_weeklyreports(self):
        self.fail()

    def test_superusers_can_CRUD_all_users_data(self):
        self.fail()

    def test_staff_members_can_CRUD_all_users_data(self):
        self.fail()

    def test_staff_members_cannot_CRUD_all_runs_and_weeklyreports(self):
        self.fail()

