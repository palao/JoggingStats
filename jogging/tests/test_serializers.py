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

from django.test import TestCase
from rest_framework.parsers import JSONParser

from jogging.serializers import NewAccountSerializer


class NewAccountSerializerTestCase(TestCase):
    def test_can_deserialize_user(self):
        json_data = b'{"username": "pedro", "password": "whatever"}'
        stream = io.BytesIO(json_data)
        data = JSONParser().parse(stream)
        serializer = NewAccountSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(
            dict(serializer.validated_data),
            {"username": "pedro", "password": "whatever"}
        )
