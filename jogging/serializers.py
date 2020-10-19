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

from rest_framework import serializers
from django.contrib.auth.models import User

from jogging.models import Run, WeeklyReport


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password', 'id')
        extra_kwargs = {'password': {'write_only': True}}
        
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(username=validated_data["username"])
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
        return super().update(instance, validated_data)


class RunSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source="owner.username", required=False)
    class Meta:
        model = Run
        fields = (
            "id", "user", "date", "distance", "time", "location", "weather"
        )
        read_only_fields = ("id", "user")


class FloatField(serializers.FloatField):
    def to_representation(self, value):
        return round(value, 2)


class WeeklyReportSerializer(serializers.ModelSerializer):
    total_distance_km = FloatField()
    average_speed_kmph = FloatField()
    
    class Meta:
        model = WeeklyReport
        fields = ("week", "total_distance_km", "average_speed_kmph")

