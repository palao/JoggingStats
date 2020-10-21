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
from .search import make_Qexpr_from_search_string


class NewAccount(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class RunViewSet(viewsets.ModelViewSet):
    serializer_class = RunSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwnerOrAdmin)
    filterset_fields = [
        'date', 'distance', 'time', 'owner', 'location', 'weather', 'id']
    
    def get_queryset(self):
        if self.request.user.is_superuser:
            queryset0 = Run.objects.all()
        else:
            queryset0 = Run.objects.filter(owner=self.request.user)
        q = self.request.query_params.get("search", None)
        if q:
            q = make_Qexpr_from_search_string(q)
            queryset = queryset0.filter(q)
        else:
            queryset = queryset0
        return queryset

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class WeeklyReportViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = WeeklyReportSerializer
    permission_classes = (permissions.IsAuthenticated, )
    filterset_fields = [
        'average_speed_kmph', 'total_distance_km', 'week_start']
    
    def get_queryset(self):
        return WeeklyReport.objects.filter(owner=self.request.user)


class UserViewSet(viewsets.ModelViewSet):
    #queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated, IsAdminOrStaff)
    filterset_fields = ["username"]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return User.objects.all()
        else:
            return User.objects.filter(pk=user.pk)
