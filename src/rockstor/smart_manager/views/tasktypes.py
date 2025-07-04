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

from rest_framework import generics
from rest_framework.authentication import (
    BasicAuthentication,
    SessionAuthentication,
)
from storageadmin.auth import DigestAuthentication
from rest_framework.permissions import IsAuthenticated
from smart_manager.serializers import TaskType, TaskTypeSerializer


class TaskTypeView(generics.ListAPIView):
    authentication_classes = (
        DigestAuthentication,
        SessionAuthentication,
        BasicAuthentication,
    )
    permission_classes = (IsAuthenticated,)
    serializer_class = TaskTypeSerializer

    def get_queryset(self):
        return [
            TaskType("scrub", "scrub a pool"),
            TaskType("snapshot", "take snapshot of a pool"),
        ]
