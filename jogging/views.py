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

from .serializers import NewAccountSerializer, RunSerializer
from .models import Run


class NewAccount(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = NewAccountSerializer
    #permission_classes = (permissions.AllowAny, )


class RunViewSet(viewsets.ModelViewSet):
    queryset = Run.objects.all()
    serializer_class = RunSerializer
    permission_classes = (permissions.IsAuthenticated, )