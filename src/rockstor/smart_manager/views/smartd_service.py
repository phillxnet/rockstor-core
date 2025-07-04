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

from rest_framework.response import Response
from system.services import systemctl
from django.db import transaction
from smart_manager.views.base_service import BaseServiceDetailView
import os
from system import smart
from smart_manager.models import Service


import logging

logger = logging.getLogger(__name__)
SMART = "/usr/sbin/smartctl"


class SMARTDServiceView(BaseServiceDetailView):
    service_name = "smartd"

    @transaction.atomic
    def post(self, request, command):
        """
        execute a command on the service
        """
        e_msg = "Failed to %s S.M.A.R.T service due to system error." % command
        with self._handle_exception(request, e_msg):
            if not os.path.exists(SMART):
                logger.info(f"{SMART} binary not found: try `zypper in smartmontools`")
                raise Exception
            if command == "config":
                service = Service.objects.get(name=self.service_name)
                config = request.data.get("config", {})
                logger.debug("config = %s" % config)
                self._save_config(service, config)
                if "custom_config" in config:
                    config = config["custom_config"]
                else:
                    config = ""
                smart.update_config(config)
                systemctl(self.service_name, "enable")
                systemctl(self.service_name, "restart")
            else:
                self._switch(command)
        return Response()

    @classmethod
    def _switch(cls, switch):
        if switch == "start":
            systemctl(cls.service_name, "enable")
            systemctl(cls.service_name, "start")
        else:
            systemctl(cls.service_name, "disable")
            systemctl(cls.service_name, "stop")
