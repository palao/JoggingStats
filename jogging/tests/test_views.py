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

#import unittest
import json

from django.urls import reverse
from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from jogging.views import NewAccount, RunViewSet


class NewAccountTestCase(TestCase):
    def test_can_create_account(self):
        factory = APIRequestFactory()
        view = NewAccount.as_view()
        request = factory.post(
            view,
            {"username": "mike", "password": "1259f"},
            format="json",
        )
        response = view(request)
        self.assertEqual(User.objects.count(), 1)
        user = User.objects.first()
        self.assertEqual(user.username, "mike")
        with self.assertRaises(KeyError):
            response.data["password"]


class RunViewSetTestCase(TestCase):
    def test_post_allowed_if_authenticated(self):
        user = User(username="paul")
        user.set_password("aDc3")
        user.save()
        factory = APIRequestFactory()
        view = RunViewSet.as_view({'post': 'create'})
        request = factory.post(
            view,
            {
                "date": "2020-10-12", "distance": "2.6",
                "time": "01:23:30", "location": "Rome"
            },
            format="json",
        )
        force_authenticate(request, user=user)
        response = view(request)
        self.assertEqual(response.status_code, 201)
        
    def test_forbidden_if_not_logged_in(self):
        factory = APIRequestFactory()
        view = RunViewSet.as_view({'post': 'create'})
        request = factory.post(
            view,
            {
                "date": "2020-10-12", "distance": "2.6",
                "time": "01:23:30", "location": "Rome"
            },
            format="json",
        )
        response = view(request)
        self.assertEqual(response.status_code, 403)

