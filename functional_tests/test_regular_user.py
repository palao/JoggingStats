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

import requests

from .utils import get_weather
from .base import FunctionalTestCase


TODAY = date.today()


class RegularUserTestCase(FunctionalTestCase):
    username = "bob"
    password = "1Mpossibl3"
    run_data = [
        {
            "date": str(TODAY),
            "distance": 11.3,
            "time": str(timedelta(minutes=58, seconds=24)),
            "location": "Frankfurt",
        },
        {
            "date": str(TODAY-timedelta(days=1)),
            "distance": 15.9,
            "time": str(timedelta(hours=1, minutes=22, seconds=47)),
            "location": "Frankfurt",
        },
        {
            "date": str(TODAY-timedelta(days=2)),
            "distance": 15.9,
            "time": str(timedelta(hours=1, minutes=20, seconds=32)),
            "location": "Frankfurt",
        },
    ]
    another_username = "mike"
    another_password = "ju=988X"
    another_run_data = [
        {
            "date": str(TODAY-timedelta(days=10)),
            "distance": 5.3,
            "time": str(timedelta(minutes=25, seconds=4)),
            "location": "Madrid",
        },
        {
            "date": str(TODAY-timedelta(days=8)),
            "distance": 5.3,
            "time": str(timedelta(minutes=25, seconds=55)),
            "location": "Madrid",
        },            
    ]
    
    def setUp(self):
        # another user has already created an account:
        auth_data = {
            "username": self.another_username, "password": self.another_password
        }
        post_resp = requests.post(
            self.live_server_url+"/new-account/", data=auth_data
        )
        # and posted some data:
        new_data = []
        for item in self.another_run_data:
            post_resp = requests.post(
                self.live_server_url+"/run/",
                data=item, auth=(auth_data["username"], auth_data["password"])
            )
            new_data.append(json.loads(post_resp.content))
        self.another_run_data = new_data
        # Bob himself made an account too:
        auth_data = {"username": self.username, "password": self.password}
        post_resp = requests.post(
            self.live_server_url+"/new-account/", data=auth_data
        )
        self.auth_data = (self.username, self.password)
        
    def test_can_save_data(self):
        # Now that he has an account, Bob would like to finally send
        # data for his run this morning:
        post_resp = requests.post(
            self.live_server_url+"/run/", data=self.run_data[0], auth=self.auth_data
        )
        self.check_post(post_resp, self.run_data[0])
        new_data = json.loads(post_resp.content)
        self.run_data[0] = new_data
        # Wonderful! He sees that the posted data has his own username included:
        self.assertEqual(new_data["user"], self.username)
        # He also stores yesterday's run data:
        post_resp = requests.post(
            self.live_server_url+"/run/",
            data=self.run_data[1], auth=self.auth_data
        )
        self.check_post(post_resp, self.run_data[1])
        self.run_data[1] = json.loads(post_resp.content)
        
        # But he is wondering... are the data really stored? He tries to
        # retrieve them:
        get_resp = requests.get(
            self.live_server_url+"/run/", auth=self.auth_data
        )        
        # and indeed he can retrieve the uploaded data!
        self.check_get_run(get_resp, self.run_data[:2])
        # That makes him very happy: he can use that functionality to
        # analyze his progress.

    def test_can_see_only_own_data(self):
        # after posting some data:
        for run_data in self.run_data:
            post_resp = requests.post(
                self.live_server_url+"/run/", data=run_data, auth=self.auth_data
            )
        # and out of curiosity, Bob wonders if he can sees his cousin's records.
        # But he checks that he can only see his own data:
        get_resp = requests.get(
            self.live_server_url+"/run/", auth=self.auth_data
        )
        retrieved_runs = json.loads(get_resp.content)
        self.assertEqual(len(retrieved_runs["results"]), len(self.run_data))
        # he knows that because he knows how many runs he uploaded.
        # BTW, he notices that there is some information in each item
        # about weather. Is this real data, or only a placeholder?
        for item in json.loads(get_resp.content)["results"]:
            self.assertNotEqual(item["weather"], "?")
        # That is nice! The weather data is real! That will be very useful
        # for him.
        
    def test_can_update_own_data(self):
        # after posting some data:
        for irun_data, run_data in enumerate(self.run_data):
            post_resp = requests.post(
                self.live_server_url+"/run/", data=run_data, auth=self.auth_data
            )
            self.run_data[irun_data] = json.loads(post_resp.content)
        # bob realized that he typed a wrong distance on the first record.
        # He tries to fix that with a PATCH:
        pk = self.run_data[0]["id"]
        patch_resp = requests.patch(
            self.live_server_url+f"/run/{pk}/",
            data={"distance": 10.3}, auth=self.auth_data
        )
        # and he sees that it is updated properly:
        pk = self.run_data[1]["id"]
        expected_item = self.run_data[0].copy()
        expected_item["distance"] = 10.3
        self.check_get_run(patch_resp, [expected_item], single=True)
        # and he also realized that another entry is completely wrong,
        # so he fixes it:
        item = {
            "date": str(TODAY-timedelta(days=2)),
            "distance": 10.7,
            "time": "01:06:22",
            "location": "Rome",
        }
        put_resp = requests.put(
            self.live_server_url+f"/run/{pk}/",
            data=item, auth=self.auth_data
        )
        item.update({
            "id": pk,
            "weather": self.run_data[1]["weather"],
            "user": self.run_data[1]["user"]
        })
        self.check_get_run(put_resp, [item], single=True)
        # Sweet!
        
    def test_cannot_update_run_records_from_other_users(self):
        # Bob wants to fix an entry in his statistics that is wrong.
        # The location must be changed:
        pk = self.another_run_data[0]["id"]
        patch_resp = requests.patch(
            self.live_server_url+f"/run/{pk}/",
            data={"location": "Sevilla"}, auth=self.auth_data
        )
        # but he got a 404:
        self.assertEqual(patch_resp.status_code, 404)
        # Out of curiosity. Bob wonders if he can change a complete record
        # not belonging to him...
        item = {
            "date": str(TODAY-timedelta(days=2)),
            "distance": 10.7,
            "time": str(timedelta(hours=1, minutes=6, seconds=22)),
            "location": "Rome",
        }
        pk = self.another_run_data[1]["id"]
        put_resp = requests.put(
            self.live_server_url+f"/run/{pk}/",
            data=item, auth=self.auth_data
        )
        # but he cannot, as expected:
        self.assertEqual(put_resp.status_code, 404)

    def test_pagination(self):
        # This test is a bit smoky for now...
        # after posting some data:
        for irun_data, run_data in enumerate(self.run_data):
            post_resp = requests.post(
                self.live_server_url+"/run/", data=run_data, auth=self.auth_data
            )
            self.run_data[irun_data] = json.loads(post_resp.content)
        # Bob sees that the results listed:
        get_resp = requests.get(
            self.live_server_url+"/run/", auth=self.auth_data
        )        
        # are paginated:
        content = json.loads(get_resp.content)
        self.assertEqual(content["count"], 3)
        self.assertIs(content["next"], None)
        self.assertIs(content["previous"], None)

        
