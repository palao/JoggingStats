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


from django.db import models

from .weather import get_weather


class Run(models.Model):
    date = models.DateField()
    distance = models.FloatField()
    time = models.DurationField()
    location = models.CharField(max_length=256)
    owner = models.ForeignKey(
        "auth.User", related_name="jogging", on_delete=models.CASCADE
    )
    weather = models.CharField(default="?", max_length=128)

    def save(self, *args, **kwargs):
        weather = get_weather(self.location, self.date)
        if weather:
            self.weather = weather
        super().save(*args, **kwargs)


class WeeklyReport(models.Model):
    week_start = models.DateField()
    total_distance_km = models.FloatField()
    average_speed_kmph = models.FloatField()
    owner = models.ForeignKey(
        "auth.User", related_name="%(app_label)s_%(class)s",
        on_delete=models.CASCADE
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["week_start", "owner"],
                name="one_report_per_week_and_owner"
            )
        ]
