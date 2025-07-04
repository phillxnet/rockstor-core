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
from storageadmin.models import Pool


class PoolBalance(models.Model):

    pool = models.ForeignKey(Pool, on_delete=models.CASCADE)
    # started|running|cancelling|cancelled|pausing|paused|finished|failed|terminated
    status = models.CharField(max_length=10, default="started")
    # huey uuid
    tid = models.CharField(max_length=36, null=True)
    message = models.CharField(max_length=1024, null=True)
    start_time = models.DateTimeField(auto_now=True)
    end_time = models.DateTimeField(null=True)
    percent_done = models.IntegerField(default=0)
    # Flag to denote internal auto initiated balance ie during dev delete.
    internal = models.BooleanField(default=False)

    class Meta:
        app_label = "storageadmin"
        get_latest_by = "start_time"
