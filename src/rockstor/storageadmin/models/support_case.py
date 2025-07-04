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


class SupportCase(models.Model):
    """we use default id as the case number"""

    notes = models.TextField()
    """location of the zipped logfile(s)"""
    zipped_log = models.CharField(max_length=128)
    STATUS_CHOICES = (
        ("created", "created"),
        ("submitted", "submitted"),
        ("resolved", "resolved"),
    )
    status = models.CharField(max_length=9, choices=STATUS_CHOICES)
    TYPE_CHOICES = (
        ("auto", "auto"),
        ("manual", "manual"),
    )
    case_type = models.CharField(max_length=6, choices=TYPE_CHOICES)

    class Meta:
        app_label = "storageadmin"
