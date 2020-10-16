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

from django.contrib.auth.models import User
import requests

from .base import FunctionalTestCase

TODAY = date.today()


class UsersMixIn:
    super_username = "root"
    super_password = "12x45"
    staff_username = "epi"
    staff_password = "bL8s"
    username = "bob"
    password = "1Mpossibl3"
    run_data = {
        "date": str(TODAY),
        "distance": 11.3,
        "time": str(timedelta(minutes=58, seconds=24)),
        "location": "Frankfurt",
    }
    another_username = "mike"
    another_password = "ju=988X"
    another_run_data = {
        "date": str(TODAY-timedelta(days=10)),
        "distance": 5.3,
        "time": str(timedelta(minutes=25, seconds=4)),
        "location": "Madrid",
    }
    
    def setUp(self):
        # given a superuser:
        self.super_user = User.objects.create_superuser(
            self.super_username, password=self.super_password)
        # and a staff user:
        self.staff_user = User.objects.create_user(
            self.staff_username, password=self.staff_password, is_staff=True)
        # and given that another user has already created an account:
        auth_data = {
            "username": self.another_username, "password": self.another_password
        }
        post_resp = requests.post(
            self.live_server_url+"/new-account/", data=auth_data
        )
        # and posted some data:
        response = requests.post(
            self.live_server_url+"/run/",
            data=self.another_run_data,
            auth=(auth_data["username"], auth_data["password"])
        )
        self.another_run_data = json.loads(response.content)
        # ...
        # Bob himself made an account too:
        auth_data = {"username": self.username, "password": self.password}
        post_resp = requests.post(
            self.live_server_url+"/new-account/", data=auth_data
        )
        self.auth_data = (self.username, self.password)
        # he himself posts also some data:
        response = requests.post(
            self.live_server_url+"/run/",
            data=self.run_data,
            auth=self.auth_data
        )
        self.run_data = json.loads(response.content)
        self.all_runs = [self.run_data, self.another_run_data]

    def test_can_CRUD_users(self):
        """This test must pass for superusers and staff, that's why it 
        is in the MixIn."""
        # the $BOSS can see the list of users:
        get_resp = requests.get(
            self.live_server_url+"/user-list/", auth=self.auth
        )        
        self.check_get_run(get_resp, self.all_runs)
        # he can add a new one:
        put_resp = requests.put(
            self.live_server_url+"/user/",
            data={"username": "aitor", "password": "7illA"}, auth=self.auth
        )
        # and it is indeed created:
        self.assertEqual(put_resp.status_code, 201)
        self.assertEqual(put_resp.reason, "Created")
        resp_data = json.loads(put_resp.content)
        self.assertEqual(resp_data, {"username": "aitor"})
        # which is confirmed because there are 5 users now:
        get_resp = requests.get(
            self.live_server_url+"/user-list/", auth=self.auth
        )        
        self.assertEqual(
            len(json.loads(get_resp.content)), 5
        )
        # He can also delete an entry that he has been told to be wrong:
        del_resp = requests.delete(
            self.live_server_url+"/user/5/", auth=self.auth
        )
        # and, yes, it is gone!
        get_resp = requests.get(
            self.live_server_url+"/user-list/", auth=self.auth
        )        
        self.assertEqual(
            len(json.loads(get_resp.content)), 4
        )
        

class SuperUsersTestCase(UsersMixIn, FunctionalTestCase):
    def setUp(self):
        super().setUp()
        self.auth = (self.super_username, self.super_password)
    
    def test_can_CRUD_run_records(self):
        # the admin has access to all the data in the site:
        get_resp = requests.get(
            self.live_server_url+"/run/", auth=self.auth
        )        
        self.check_get_run(get_resp, self.all_runs)
        pk = self.run_data["id"]
        # if needed, he can change some data:
        patch_resp = requests.patch(
            self.live_server_url+f"/run/{pk}/",
            data={"location": "Tokyo"}, auth=self.auth
        )
        # and he sees that it is updated properly:
        expected_item = self.run_data.copy()
        expected_item["location"] = "Tokyo"
        self.check_get_run(patch_resp, [expected_item], single=True)
        # ...but he will restore it back:
        data2put = self.run_data.copy()
        del data2put["user"]
        del data2put["id"]
        put_resp = requests.put(
            self.live_server_url+f"/run/{pk}/",
            data=data2put, auth=self.auth
        )
        # and it is indeed restored:
        get_resp = requests.get(
            self.live_server_url+"/run/", auth=self.auth
        )        
        self.check_get_run(get_resp, self.all_runs)
        # He can also delete an entry that he has been told to be wrong:
        pk = self.another_run_data["id"]
        del_resp = requests.delete(
            self.live_server_url+f"/run/{pk}/", auth=self.auth
        )
        # and, yes, it is gone!
        get_resp = requests.get(
            self.live_server_url+"/run/", auth=self.auth
        )        
        self.check_get_run(get_resp, [self.run_data])
        

class StaffUsersTestCase(UsersMixIn, FunctionalTestCase):
    def setUp(self):
        super().setUp()
        self.auth = (self.staff_username, self.staff_password)
    
    def test_cannot_CRUD_run_records(self):
        # the staff has no access to run records in the site:
        get_resp = requests.get(
            self.live_server_url+"/run/", auth=self.auth
        )
        self.check_get_run(get_resp, [])
        # he cannot change the data of other users:
        patch_resp = requests.patch(
            self.live_server_url+"/run/1/",
            data={"location": "Tokyo"}, auth=self.auth
        )
        # since he gets an error:
        self.assertEqual(patch_resp.status_code, 404)
        # And of course, he cannot delete any entry that doesn't belong to him:
        del_resp = requests.delete(
            self.live_server_url+"/run/1/", auth=self.auth
        )
        self.assertEqual(del_resp.status_code, 404)
        
