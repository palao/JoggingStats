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

import io
from datetime import date, timedelta

from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.parsers import JSONParser

from jogging.serializers import NewAccountSerializer, RunSerializer
from jogging.models import Run


class NewAccountSerializerTestCase(TestCase):
    def setUp(self):
        json_data = b'{"username": "pedro", "password": "whatever"}'
        stream = io.BytesIO(json_data)
        self.data = JSONParser().parse(stream)
        self.expected_validated_data = {
            "username": "pedro", "password": "whatever"
        }
        
    def test_can_deserialize_user(self):
        serializer = NewAccountSerializer(data=self.data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(
            dict(serializer.validated_data),
            self.expected_validated_data
        )

    def test_create_makes_new_user(self):
        serializer = NewAccountSerializer(data=self.data)
        serializer.is_valid()
        new_user = serializer.create(serializer.validated_data)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(new_user.username, "pedro")
        self.assertTrue(new_user.password.startswith("pbkdf2_sha256$"))
        with self.assertRaises(KeyError):
            serializer.validated_data["password"]


class RunSerializerTestCase(TestCase):
    def test_can_serialize_run(self):
        run = Run(
            date=date.today(),
            distance=9.2,
            time=timedelta(hours=1, seconds=2),
            location="Las Vegas",
        )
        run.save()
        serializer = RunSerializer(run)
        self.assertEqual(
            serializer.data,
            {
                "date": str(date.today()),
                "distance": 9.2,
                "time": "01:00:02",
                "location": "Las Vegas",
            }
        )