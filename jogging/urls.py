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


from django.urls import path, include
from rest_framework.routers import DefaultRouter

from jogging import views


router = DefaultRouter()
router.register(r"run", views.RunViewSet, basename="run")
router.register(
    r"weekly-reports", views.WeeklyReportViewSet, basename="weekly-reports")
router.register(r"user", views.UserViewSet, basename="user")


urlpatterns = [
    path("new-account/", views.NewAccount.as_view(), name="new-account"),
    path("", include(router.urls)),
]
