"""
Copyright (joint work) 2024 The Rockstor Project <https://rockstor.com>

Rockstor is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published
by the Free Software Foundation; either version 2 of the License,
or (at your option) any later version.

Rockstor is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

from django.db import models


class DiskStat(models.Model):

    name = models.CharField(max_length=128)
    reads_completed = models.FloatField()
    reads_merged = models.FloatField()
    sectors_read = models.FloatField()
    ms_reading = models.FloatField()
    writes_completed = models.FloatField()
    writes_merged = models.FloatField()
    sectors_written = models.FloatField()
    ms_writing = models.FloatField()
    ios_progress = models.FloatField()
    ms_ios = models.FloatField()
    weighted_ios = models.FloatField()
    ts = models.DateTimeField(db_index=True)

    class Meta:
        app_label = "smart_manager"
