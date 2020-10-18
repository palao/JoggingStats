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

from datetime import timedelta, date
from unittest.mock import patch
import json

from django.urls import reverse
from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework.renderers import JSONRenderer

from jogging.views import (
    NewAccount, RunViewSet, WeeklyReportViewSet, UserViewSet,
)
from jogging.models import Run, WeeklyReport
from jogging.serializers import RunSerializer, WeeklyReportSerializer


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
    def setUp(self):
        self.user1 = User.objects.create(username="sam")
        self.user2 = User.objects.create(username="dave")
        self.superuser = User.objects.create_superuser(username="boss")
        with patch("jogging.models.get_weather") as pget_weather:
            pget_weather.return_value = "Cloudy"
            self.run1 = Run.objects.create(
                date=date(2020, 10, 13),
                distance="5.6",
                time=timedelta(minutes=53, seconds=22),
                location="Porto",
                owner=self.user1,
            )
            self.run2 = Run.objects.create(
                date=date(2020, 9,23),
                distance="4.9",
                time=timedelta(minutes=30, seconds=8),
                location="Casablanca",
                owner=self.user2,
            )
        
    def test_create_allowed_if_authenticated(self):
        user = User.objects.create(username="paul")
        factory = APIRequestFactory()
        with patch("jogging.models.get_weather") as pget_weather:
            pget_weather.return_value = "Cloudy"
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
        
    def test_create_forbidden_if_not_logged_in(self):
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

    def test_list_fetches_data_from_logged_in_user(self):
        serializer = RunSerializer([self.run1], many=True)
        expected = JSONRenderer().render(serializer.data)
        factory = APIRequestFactory()
        view = RunViewSet.as_view({'get': 'list'})
        request = factory.get("/run/")
        force_authenticate(request, user=self.user1)
        response = view(request)
        response.render()
        self.assertEqual(response.content, expected)

    def test_list_fetches_all_data_if_superuser(self):
        serializer = RunSerializer([self.run1, self.run2], many=True)
        expected = JSONRenderer().render(serializer.data)
        factory = APIRequestFactory()
        view = RunViewSet.as_view({'get': 'list'})
        request = factory.get("/run/")
        force_authenticate(request, user=self.superuser)
        response = view(request)
        response.render()
        self.assertEqual(response.content, expected)

    def test_partial_update_patches_data(self):
        for user in (self.user1, self.superuser):
            with self.subTest(user=user):
                factory = APIRequestFactory()
                view = RunViewSet.as_view({'patch': 'partial_update'})
                request = factory.patch("/run/", {"location": "Winnipeg"})
                force_authenticate(request, user=user)
                response = view(request, pk=1)
                response.render()
                data = json.loads(response.content)
                self.assertEqual(data["location"], "Winnipeg")
                # restore:
                self.run1.location = "Porto"
                self.run1.save()

    def test_destroy_deletes_data(self):
        for iuser, user in enumerate((self.user1, self.superuser)):
            ik = iuser*2+1 # because I'll destroy the 1st and add the 3rd
            with self.subTest(user=user):
                factory = APIRequestFactory()
                view = RunViewSet.as_view({'delete': 'destroy'})
                request = factory.delete("/run/")
                force_authenticate(request, user=user)
                response = view(request, pk=ik)
                response.render()
                self.assertEqual(Run.objects.count(), 1)
                # add one more:
                Run.objects.create(
                    date=date(2020, 10, 13),
                    distance="5.6",
                    time=timedelta(minutes=53, seconds=22),
                    location="Porto",
                    owner=self.user1,
                )

    # POST as superuser in the name of another user?


class WeeklyReportViewSetTestCase(TestCase):
    def test_list_forbidden_if_not_logged_in(self):
        factory = APIRequestFactory()
        view = WeeklyReportViewSet.as_view({'get': 'list'})
        request = factory.get("/weekly-reports/")
        response = view(request)
        self.assertEqual(response.status_code, 403)
        
    def test_list_fetches_data_from_user_logged_in(self):
        factory = APIRequestFactory()
        user1 = User.objects.create(username="mandri")
        user2 = User.objects.create(username="winn")
        test_dates = [
            (date(2020, 10, 12), date(2020, 10, 18)),
            (date(2020, 10, 5), date(2020, 10, 11)),
        ]
        test_distances = [13.5, 50.4]
        test_speeds = [20.0, 12.4]
        reports = [
            WeeklyReport.objects.create(
                week_start=rdate[0],
                total_distance_km=rdist,
                average_speed_kmph=rspeed,
                owner=user1,
            ) for (rdate, rdist, rspeed) in zip(
                test_dates, test_distances, test_speeds)
        ] + [
            WeeklyReport.objects.create(
                week_start=test_dates[0][0],
                total_distance_km=sum(test_distances)/2,
                average_speed_kmph=sum(test_speeds)/2,
                owner=user2,
            )
        ]
        serializer = WeeklyReportSerializer(reports[:2], many=True)
        expected = JSONRenderer().render(serializer.data)
        view = WeeklyReportViewSet.as_view({'get': 'list'})
        request = factory.get("/weekly-reports/")
        force_authenticate(request, user=user1)
        response = view(request)
        response.render()
        self.assertEqual(response.content, expected)
        
    def test_cannot_create(self):
        factory = APIRequestFactory()
        user = User.objects.create(username="mandri")
        view = WeeklyReportViewSet.as_view({'post': 'create'})
        request = factory.post(
            view,
            {
                "week": "2020-10-12 to 2020-10-18",
                "total_distance_km": "2.6",
                "average_speed_kmph": "12.3",
            },
            format="json",
        )
        force_authenticate(request, user=user)
        with self.assertRaises(AttributeError):
            response = view(request)

    def test_cannot_update(self):
        user = User.objects.create(username="mandri")
        WeeklyReport.objects.create(
            week_start=date(2020,10,5),
            total_distance_km=20,
            average_speed_kmph=10,
            owner=user,
        )
        factory = APIRequestFactory()
        view = WeeklyReportViewSet.as_view({'put': 'update'})
        request = factory.put(
            "/weekly-reports/1/",
            {
                "total_distance_km": "26",
            },
            format="json",
        )
        force_authenticate(request, user=user)
        with self.assertRaises(AttributeError):
            response = view(request)


class UserViewSetTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create(username="sam")
        self.user2 = User.objects.create(username="dave")
        self.superuser = User.objects.create_superuser(username="boss")
        self.staff_user = User.objects.create(username="manue", is_staff=True)
        
    def test_staff_and_superuser_can_create(self):
        new_username = "paul"
        factory = APIRequestFactory()
        view = UserViewSet.as_view({'post': 'create'})
        for user in (self.superuser, self.staff_user):
            request = factory.post(view, {"username": new_username})
            force_authenticate(request, user=user)
            response = view(request)
            self.assertEqual(response.status_code, 201)
            self.assertEqual(User.objects.count(), 5)
            User.objects.filter(username="paul").first().delete()

    def test_create_forbidden_if_not_logged_in(self):
        factory = APIRequestFactory()
        view = UserViewSet.as_view({'post': 'create'})
        request = factory.post(view, {"username": "paul"})
        response = view(request)
        self.assertEqual(response.status_code, 403)

    def test_create_forbidden_if_not_staff_nor_superuser(self):
        factory = APIRequestFactory()
        view = UserViewSet.as_view({'post': 'create'})
        request = factory.post(view, {"username": "paul"})
        force_authenticate(request, user=self.user1)
        response = view(request)
        self.assertEqual(response.status_code, 403)

    # def test_list_fetches_data_from_logged_in_user(self):
    #     serializer = UserSerializer([self.run1], many=True)
    #     expected = JSONRenderer().render(serializer.data)
    #     factory = APIRequestFactory()
    #     view = UserViewSet.as_view({'get': 'list'})
    #     request = factory.get("/run/")
    #     force_authenticate(request, user=self.user1)
    #     response = view(request)
    #     response.render()
    #     self.assertEqual(response.content, expected)

    # def test_list_fetches_all_data_if_superuser(self):
    #     serializer = UserSerializer([self.run1, self.run2], many=True)
    #     expected = JSONRenderer().render(serializer.data)
    #     factory = APIRequestFactory()
    #     view = UserViewSet.as_view({'get': 'list'})
    #     request = factory.get("/run/")
    #     force_authenticate(request, user=self.superuser)
    #     response = view(request)
    #     response.render()
    #     self.assertEqual(response.content, expected)

    # def test_partial_update_patches_data(self):
    #     for user in (self.user1, self.superuser):
    #         with self.subTest(user=user):
    #             factory = APIRequestFactory()
    #             view = UserViewSet.as_view({'patch': 'partial_update'})
    #             request = factory.patch("/run/", {"location": "Winnipeg"})
    #             force_authenticate(request, user=user)
    #             response = view(request, pk=1)
    #             response.render()
    #             data = json.loads(response.content)
    #             self.assertEqual(data["location"], "Winnipeg")
    #             # restore:
    #             self.run1.location = "Porto"
    #             self.run1.save()

    # def test_destroy_deletes_data(self):
    #     for iuser, user in enumerate((self.user1, self.superuser)):
    #         ik = iuser*2+1 # because I'll destroy the 1st and add the 3rd
    #         with self.subTest(user=user):
    #             factory = APIRequestFactory()
    #             view = UserViewSet.as_view({'delete': 'destroy'})
    #             request = factory.delete("/run/")
    #             force_authenticate(request, user=user)
    #             response = view(request, pk=ik)
    #             response.render()
    #             self.assertEqual(User.objects.count(), 1)
    #             # add one more:
    #             User.objects.create(
    #                 date=date(2020, 10, 13),
    #                 distance="5.6",
    #                 time=timedelta(minutes=53, seconds=22),
    #                 location="Porto",
    #                 owner=self.user1,
    #             )

    # # POST as staff a new user
