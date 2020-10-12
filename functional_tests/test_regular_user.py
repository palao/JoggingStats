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
import json

from django.contrib.staticfiles.testing import LiveServerTestCase
import requests


class RegularUserTestCase(LiveServerTestCase):
    username = "bob"
    password = "1Mpossibl3"

    def setUp(self):
        ## all the tests in this class will require authentication:
        self.auth_data = {"username": self.username, "password": self.password}
        post_resp = requests.post(
            self.live_server_url+"/new-account/", data=self.auth_data
        )

    def check_post(self, resp, data):
        # the response is ok
        self.assertTrue(resp.ok)
        # with the proper status code:
        self.assertEqual(resp.status_code, 201)
        # and the reason is: the run data was created
        self.assertEqual(resp.reason, "Created")
        # and to wrap it up, the text of the response has the posted data:
        expected_data = {
            k: data[k] for k in ("date", "distance", "time", "location")
        }
        self.assertEqual(resp.text, json.dumps(expected_data))

    def check_get_run(self, resp, items):
        # the response is ok
        self.assertTrue(resp.ok)
        # with the proper status code:
        self.assertEqual(resp.status_code, 200)
        # and the reason is expectedly OK
        self.assertEqual(resp.reason, "OK")
        # Now, he sees in the response the data previously posted:
        posted_runs = json.loads(resp.text)
        results = posted_runs["results"]
        count = posted_runs["count"]
        self.assertEqual(count, len(items))
        for item in items:
            self.assertIn(item, results)

    def test_can_save_data(self):
        # Now that he has an account, Bob would like to finally send
        # data for his run this morning:
        today = date.today()
        runtime = timedelta(minutes=58, seconds=24)
        todays_stats = {
            "date": str(today),
            "distance": 11.3,
            "time": runtime,
            "location": "Frankfurt am Main",
        }
        full_data = self.auth_data.copy()
        full_data.update(todays_stats)
        post_resp = requests.post(
            self.live_server_url+"/run", data=full_data
        )
        self.check_post(post_resp, full_data)
        # Wonderful!
        # He also stores yesterday's run data:
        yesterday = today - timdedelta(days=1)
        yesterdays_stats = {
            "date": str(yesterday),
            "distance": 15.9,
            "time": timedelta(hours=1, minutes=22, seconds=47),
            "location": "Frankfurt am Main",
        }
        full_data.update(yesterdays_stats)
        post_resp = requests.post(
            self.live_server_url+"/run", data=full_data
        )
        self.check_post(post_resp, full_data)
        # But he is wondering... are the data really stored? He tries to
        # retrieve them:
        get_resp = requests.get(
            self.live_server_url+"/run", data=self.auth_data
        )        
        # and indeed he can retrieve the uploaded data!
        self.check_get_run(get_resp, [todays_stats, yesterdays_stats])
        # That makes him very happy: he can use that functionality to
        # analyze his progress.

