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

from datetime import timedelta
import json

from django.contrib.staticfiles.testing import LiveServerTestCase
import requests

from .utils import current_week, ONEDAY


THIS_MONDAY, THIS_SUNDAY = current_week()
PAST_WEEK_MONDAY = THIS_MONDAY-7*ONEDAY
PAST_WEEK_SUNDAY = THIS_SUNDAY-7*ONEDAY
PASTPAST_WEEK_MONDAY = THIS_MONDAY-14*ONEDAY
PASTPAST_WEEK_SUNDAY = THIS_SUNDAY-14*ONEDAY


class WeeklyReportTestCase(LiveServerTestCase):
    username = "bob"
    password = "1Mpossibl3"
    run_data = {"past_week":
        [
            {
                "date": str(PAST_WEEK_MONDAY),
                "distance": 11.3,
                "time": str(timedelta(minutes=58, seconds=24)),
                "location": "Frankfurt",
            },
            {
                "date": str(PAST_WEEK_MONDAY+ONEDAY),
                "distance": 15.9,
                "time": str(timedelta(hours=1, minutes=22, seconds=47)),
                "location": "Frankfurt",
            },
            {
                "date": str(PAST_WEEK_MONDAY+3*ONEDAY),
                "distance": 15.9,
                "time": str(timedelta(hours=1, minutes=20, seconds=32)),
                "location": "Frankfurt",
            },
            {
                "date": str(PAST_WEEK_MONDAY+5*ONEDAY),
                "distance": 15.9,
                "time": str(timedelta(hours=1, minutes=19, seconds=3)),
                "location": "Frankfurt",
            },
        ],
        "current_week":
        [
            {
                "date": str(THIS_MONDAY),
                "distance": 15.9,
                "time": str(timedelta(hours=1, minutes=23, seconds=12)),
                "location": "Frankfurt",
            },
        ],
    }
    expected_reports_data = {
        "past_week": {
            "week": "{} to {}".format(str(PAST_WEEK_MONDAY), str(PAST_WEEK_SUNDAY)),
            "total_distance_km": 59.0,
            "average_speed_kmph": 11.77,
        },
        "current_week": {
            "week": "{} to {}".format(str(THIS_MONDAY), str(THIS_SUNDAY)),
            "total_distance_km": 15.9,
            "average_speed_kmph": 11.47,
        }
    }
    another_username = "mike"
    another_password = "ju=988X"
    another_run_data = [
        {
            "date": str(PAST_WEEK_MONDAY),
            "distance": 5.3,
            "time": str(timedelta(minutes=25, seconds=4)),
            "location": "Madrid",
        },
        {
            "date": str(PAST_WEEK_SUNDAY),
            "distance": 5.3,
            "time": str(timedelta(minutes=25, seconds=55)),
            "location": "Madrid",
        },            
    ]
    
    
    def setUp(self):
        # Bob made an account:
        auth_data = {"username": self.username, "password": self.password}
        post_resp = requests.post(
            self.live_server_url+"/new-account/", data=auth_data
        )
        self.auth_data = (self.username, self.password)
        # and posted some data
        for run_data in self.run_data["past_week"]+self.run_data["current_week"]:
            post_resp = requests.post(
                self.live_server_url+"/run/", data=run_data, auth=self.auth_data
            )

    def test_can_get_list_of_weekly_reports(self):
        # Bob has been told that the site produces weekly reports
        # with some statistics of each user's runs. He wants to
        # check it out.
        # He has entered some training data of his runs. And he checks the
        # reports:
        get_resp = requests.get(
            self.live_server_url+"/weekly-reports/", auth=self.auth_data
        )
        # the response is ok
        self.assertTrue(get_resp.ok)
        # with the proper status code:
        self.assertEqual(get_resp.status_code, 200)
        # and the reason is expectedly OK
        self.assertEqual(get_resp.reason, "OK")
        # Now, he sees in the response the data previously posted:
        stats = json.loads(get_resp.content)["results"]
        self.assertEqual(len(stats), len(self.expected_reports_data))
        for week, item in self.expected_reports_data.items():
            self.assertIn(item, stats)

    def test_cannot_modify_weekly_reports(self):
        # even if Bob tries, just for the sake of testing, 
        resp = requests.post(
            self.live_server_url+"/weekly-reports/", auth=self.auth_data,
            params={
                "week": "{} to {}".format(
                    str(PASTPAST_WEEK_MONDAY), str(PASTPAST_WEEK_SUNDAY)
                ),
                "total distance [km]": 52.9,
                "average speed [km/h]": 13.39,
            }
        )
        # he cannot modify the reports:
        self.assertEqual(resp.status_code, 405)

    def test_can_see_only_own_reports(self):
        # another user has already created an account:
        auth_data = {
            "username": self.another_username, "password": self.another_password
        }
        post_resp = requests.post(
            self.live_server_url+"/new-account/", data=auth_data
        )
        # and posted some data:
        for item in self.another_run_data:
            requests.post(
                self.live_server_url+"/run/",
                data=item, auth=(auth_data["username"], auth_data["password"])
            )
        # but that data does not modifies Bob's stats:
        get_resp = requests.get(
            self.live_server_url+"/weekly-reports/", auth=self.auth_data
        )
        stats = json.loads(get_resp.content)["results"]
        self.assertEqual(len(stats), len(self.expected_reports_data))
        for week, item in self.expected_reports_data.items():
            self.assertIn(item, stats)


