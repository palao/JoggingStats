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
from django.contrib.auth.models import User

from .base import FunctionalTestCase


class FilteringTestCase(FunctionalTestCase):
    username = "bob"
    password = "1Mpossibl3"
    another_username = "mike"
    another_password = "ju=988X"
    super_username = "root"
    super_password = "12x45"
    run_data = [
        {
            "date": "2020-10-19",
            "distance": 11.3,
            "time": "58:24",
            "location": "Frankfurt",
        },
        {
            "date": "2020-10-16",
            "distance": 15.9,
            "time": "1:22:47",
            "location": "Frankfurt",
        },
        {
            "date": "2020-10-14",
            "distance": 15.9,
            "time": "1:22:02",
            "location": "Frankfurt",
        },
        {
            "date": "2020-10-12",
            "distance": 15.9,
            "time": "1:23:21",
            "location": "Frankfurt",
        },
        {
            "date": "2020-10-11",
            "distance": 11.3,
            "time": "59:23",
            "location": "Frankfurt",
        },
        {
            "date": "2020-10-9",
            "distance": 14.2,
            "time": "1:15:12",
            "location": "Toledo",
        },
        {
            "date": "2020-10-7",
            "distance": 14.2,
            "time": "1:16:52",
            "location": "Toledo",
        },
        {
            "date": "2020-10-3",
            "distance": 21.2,
            "time": "2:42:15",
            "location": "Madrid",
        },
        {
            "date": "2020-9-30",
            "distance": 15.9,
            "time": "1:20:37",
            "location": "Madrid",
        },
        {
            "date": "2020-9-28",
            "distance": 15.9,
            "time": "1:25:11",
            "location": "Frankfurt",
        },
    ]

    def setUp(self):
        # given a superuser:
        self.super_user = User.objects.create_superuser(
            self.super_username, password=self.super_password)
        self.super_auth = (self.super_username, self.super_password)
        # and a regular user:
        post_resp = requests.post(
            self.live_server_url+"/new-account/",
            data={"username": self.username, "password": self.password}
        )
        self.auth = (self.username, self.password)
        # that uploaded some data:
        runs = []
        for item in self.run_data:
            post_resp = requests.post(
                self.live_server_url+"/run/",
                data=item, auth=self.auth
            )
            runs.append(json.loads(post_resp.content))
        self.complete_run_data = runs
        # and another user:
        post_resp = requests.post(
            self.live_server_url+"/new-account/",
            data={
                "username": self.another_username,
                "password": self.another_password
            }
        )     

    def check_list(self, resp, expected_amount, **params_to_check):
        items = json.loads(resp.content)["results"]
        self.assertEqual(len(items), expected_amount)
        for item in items:
            for key, value in params_to_check.items():
                self.assertEqual(item[key], value)

    def test_basic_filtering_runs(self):
        # Bob has been told also that he can filter his run records. Since
        # he has already a few, that is very useful.
        # He wants to see the records he did in Toledo:
        params = {"location": "Toledo"}
        get_resp = requests.get(
            self.live_server_url+"/run/", auth=self.auth, params=params,
        )
        self.check_list(get_resp, 2, **params)
        # Wonderful! What about his long runs in Frankfurt?
        params = {"location": "Frankfurt", "distance": 15.9}
        get_resp = requests.get(
            self.live_server_url+"/run/", auth=self.auth, params=params,
        )
        self.check_list(get_resp, 4, **params)
        # Excellent!
        
    def test_basic_filtering_reports(self):
        # Although it is less useful in his opinion, Bob will try to
        # filter weekly reports too.
        # He wants to filter by total distance. He knows that the current
        # week he only ran once and it was 11.3 km:
        params = {"total_distance_km": 11.3}
        get_resp = requests.get(
            self.live_server_url+"/weekly-reports/",
            auth=self.auth, params=params,
        )
        self.check_list(get_resp, 1, **params)
        # Great. 
        ## need more test cases here?
        
    def test_basic_filtering_users(self):
        # The admin of the site wants to get information about the users:
        get_resp = requests.get(
            self.live_server_url+"/user/", auth=self.super_auth
        )
        self.check_list(get_resp, 3)
        # but this list is too long. He wants to focus in one user:
        params = {"username": self.username}
        get_resp = requests.get(
            self.live_server_url+"/user/", auth=self.super_auth, params=params
        )
        self.check_list(get_resp, 1, **params)

    def test_advanced_filtering_runs(self):
        # Bob knows that there is a way to perform more advanced searches.
        # The "search" param must be used for that. He tries it:
        params = {"search": "distance lt 12"}
        get_resp = requests.get(
            self.live_server_url+"/run/", auth=self.auth, params=params,
        )
        self.check_list(get_resp, 2, distance=11.3)
        # But he wants to perform a more advanced search:
        params = {"search": '(distance gt 15) AND (location ne "Frankfurt")'}
        get_resp = requests.get(
            self.live_server_url+"/run/", auth=self.auth, params=params,
        )
        self.check_list(get_resp, 2, location="Madrid")
        # And last:
        params = {
            "search": '((distance gt 15) AND (location ne "Frankfurt")) OR (distance lt 12)'
        }
        get_resp = requests.get(
            self.live_server_url+"/run/", auth=self.auth, params=params,
        )
        self.check_list(get_resp, 4)
        # Nice!

