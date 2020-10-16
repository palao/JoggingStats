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
from datetime import timedelta

from django.contrib.staticfiles.testing import LiveServerTestCase


class FunctionalTestCase(LiveServerTestCase):
    def check_post(self, resp, data):
        # he gets the proper status code:
        self.assertEqual(resp.status_code, 201)
        # and the reason is: the run data was created
        self.assertEqual(resp.reason, "Created")
        # and to wrap it up, the text of the response has the posted data:
        resp_data = json.loads(resp.content)
        # to handle properly leading zeros:
        h, m, s = [float(_) for _ in resp_data["time"].split(":")]
        resp_data["time"] = str(timedelta(hours=h, minutes=m, seconds=s))
        del resp_data["weather"] #  don't look at weather for now!
        self.assertEqual(resp_data, data)

    def check_get_run(self, resp, items):
        # the response is ok
        self.assertTrue(resp.ok)
        # with the proper status code:
        self.assertEqual(resp.status_code, 200)
        # and the reason is expectedly OK
        self.assertEqual(resp.reason, "OK")
        # Now, he sees in the response the data previously posted:
        posted_runs = json.loads(resp.content)
        if len(items) == 1:
            # in this case, only 1 response is expected.
            posted_runs = [posted_runs]
        results = []
        for run in posted_runs:
            # to handle properly leading zeros:
            h, m, s = [float(_) for _ in run["time"].split(":")]
            run["time"] = str(timedelta(hours=h, minutes=m, seconds=s))
            del run["weather"] #  don't look at weather for now!
            results.append(run)
        for item in items:
            self.assertIn(item, results)

