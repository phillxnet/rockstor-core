"""
Copyright (joint work) 2026 The Rockstor Project <https://rockstor.com>

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
from django.db import transaction
from storageadmin.exceptions import RockStorAPIException
from storageadmin.models import UpdateSubscription, Appliance
from storageadmin.util import handle_exception
from storageadmin.serializers import UpdateSubscriptionSerializer
import rest_framework_custom as rfc
from django.conf import settings
from system.pkg_mgmt import repo_status, switch_repo
import logging

logger = logging.getLogger(__name__)


class UpdateSubscriptionListView(rfc.GenericView):
    serializer_class = UpdateSubscriptionSerializer

    def get_queryset(self, *args, **kwargs):
        return UpdateSubscription.objects.all()

    def _toggle_repos(self, on:str = "stable", password:str | None = None):
        """
        Toggle between settings.UPDATE_CHANNELS repos tiers. Initially in DB,
        then pass the intended only tier DB object on-to system.pkg_mgmt.switch_repo()
        to do the system level package repository changes themselves.
        :param on: UPDATE_CHANNELS identifier string.
        :param password:
        :return:
        """
        on_channel = settings.UPDATE_CHANNELS[on]
        # e.g. off_channel_names default value would be: ['Testing', 'Edge']
        off_channel_names: list[str] = [
            info["name"]
            for channel, info in settings.UPDATE_CHANNELS.items()
            if channel != on
        ]
        for name in off_channel_names:
            try:
                off_object = UpdateSubscription.objects.get(name=name)
                if off_object.status != "inactive":
                    off_object.status = "inactive"
                    off_object.save(update_fields=["status"])
            except UpdateSubscription.DoesNotExist:  # no interest if no prior entry.
                pass
        try:
            appliance = Appliance.objects.get(current_appliance=True)
        except:
            raise RockStorAPIException(
                status_code=400, detail="Error retrieving current Appliance ID"
            )
        try:
            on_object = UpdateSubscription.objects.get(name=on_channel["name"])
        except UpdateSubscription.DoesNotExist:
            on_object = UpdateSubscription(
                name=on_channel["name"],
                description=on_channel["description"],
                url=on_channel["url"],
                appliance=appliance,
                status="active",
            )
        on_object.password = password
        status, text = repo_status(on_object)
        on_object.status = status
        on_object.save()
        if status == "inactive":
            e_msg = (
                f"Activation code ({on_object.password}) could not be authorized for your "
                f"appliance ({appliance.uuid}). Verify the code and try again. If the "
                "problem persists, email support@rockstor.com with this "
                "message."
            )
            raise RockStorAPIException(status_code=400, detail=e_msg)
        if status != "active":
            e_msg = f"Failed to activate subscription. Status code: {status} details: {text}"
            raise Exception(e_msg)
        switch_repo(on_object)
        return on_object

    @transaction.atomic
    def post(self, request, command):
        with self._handle_exception(request):
            match command:
                case "activate-stable":
                    password = request.data.get("activation_code", None)
                    if password is None or password == "":
                        e_msg = "Acknowledgement is required for Stable subscription."
                        handle_exception(Exception(e_msg), request, status_code=400)
                    # remove any leading or trailing white spaces. happens enough
                    # times due to copy-paste.
                    password = password.strip()
                    # Defaults to on="stable".
                    stableo = self._toggle_repos(password=password)
                    return Response(UpdateSubscriptionSerializer(stableo).data)
                case "activate-testing":
                    testingo = self._toggle_repos(on="testing")
                    return Response(UpdateSubscriptionSerializer(testingo).data)
                case "activate-edge":
                    edgeo = self._toggle_repos(on="edge")
                    return Response(UpdateSubscriptionSerializer(edgeo).data)
                case "check-stable":
                    name = request.data.get("name")
                    stableo = UpdateSubscription.objects.get(name=name)
                    if stableo.password is not None:
                        stableo.status, text = repo_status(stableo)
                        stableo.save()
                    return Response(UpdateSubscriptionSerializer(stableo).data)
            return Response()


class UpdateSubscriptionDetailView(rfc.GenericView):
    serializer_class = UpdateSubscriptionSerializer

    def get(self, *args, **kwargs):
        return Response()
