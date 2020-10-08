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

from django.contrib.staticfiles.testing import LiveServerTestCase
import requests


class NewUserTestCase(LiveServerTestCase):
    username = "bob"
    password = "1Mpossibl3"
    
    def test_can_create_one_account_through_the_api(self):
        # Bob is an amateur runner. He loves running. He tries to run
        # every day before or after working. His friend Haile told 
        # him about a new site that he can use to store and retrieve
        # statistics of his runs. As he respects very much Haile's
        # opinions about the matter, he tries it out. He wants to
        # start by recording the stats of his last run today morning:
        today = date.today()
        runtime = timedelta(minutes=58, seconds=24)
        todays_stats = {
            "date": str(today),
            "distance": 11.3,
            "time": runtime,
            "location": "Frankfurt am Main",
        }
        post_resp = requests.post(
            "http://127.0.0.1:8000/run", data=todays_stats
        )
        # Okay, he needs an account; so he creates an account:
        
        
