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

from rest_framework import generics
from rest_framework import viewsets
from rest_framework import permissions
from django.contrib.auth.models import User

from .serializers import (
    RunSerializer, WeeklyReportSerializer, UserSerializer,
)

from .models import Run, WeeklyReport
from .permissions import IsOwnerOrAdmin, IsAdminOrStaff


class NewAccount(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class RunViewSet(viewsets.ModelViewSet):
    serializer_class = RunSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwnerOrAdmin)

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Run.objects.all()
        return Run.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class WeeklyReportViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = WeeklyReportSerializer
    permission_classes = (permissions.IsAuthenticated, )

    def get_queryset(self):
        return WeeklyReport.objects.filter(owner=self.request.user)


class UserViewSet(viewsets.ModelViewSet):
    #queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated, IsAdminOrStaff)

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return User.objects.all()
        else:
            return User.objects.filter(pk=user.pk)

    # def perform_create(self, serializer):
    #     user = self.request.user
    #     if user.is_staff or user.is_superuser:
    #         serializer.save()
