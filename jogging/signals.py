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

from datetime import timedelta

from django.db.models import Sum


def run_stats_for_report(model, user, start_date, end_date):
    return model.objects.filter(
        date__range=(start_date, end_date)
    ).filter(
        owner=user
    ).aggregate(Sum("distance"), Sum("time"))

    
def run_save_handler(sender, instance, **kwargs):
    from jogging.models import WeeklyReport
    start_date = instance.date-timedelta(days=instance.date.weekday())
    end_date = start_date+timedelta(days=6)
    wr, created = WeeklyReport.objects.get_or_create(
        week_start=start_date,
        owner=instance.owner
    )
    stats = run_stats_for_report(sender, instance.owner, start_date, end_date)
    wr.total_distance_km = stats["distance__sum"]
    seconds = stats["time__sum"].seconds
    wr.average_speed_kmph = stats["distance__sum"]*3600/seconds
    wr.save()
