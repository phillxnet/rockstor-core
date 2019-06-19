"""
Copyright (c) 2012-2019 RockStor, Inc. <http://rockstor.com>
This file is part of RockStor.

RockStor is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published
by the Free Software Foundation; either version 2 of the License,
or (at your option) any later version.

RockStor is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

from osi import run_command
import collections
import json
from .services import service_status

Image = collections.namedtuple("Image", "repository tag image_id created " "virt_size")
Container = collections.namedtuple(
    "Container", "container_id image command " "created status ports name"
)

DOCKER = "/usr/bin/docker"
DNET = [DOCKER, "network"]


def image_list():
    """
    Appears to be unused currently.
    :return:
    """
    images = []
    o, e, rc = run_command([DOCKER, "images"])
    for l in o[1:-1]:
        cur_image = Image(
            l[0:20].strip(),
            l[20:40].strip(),
            l[40:60].strip(),
            l[60:80].strip(),
            l[80:].strip(),
        )
        images.append(cur_image)
    return images


def container_list():
    """
    Appears to be unused currently.
    :return:
    """
    containers = []
    o, e, rc = run_command([DOCKER, "ps", "-a"])
    for l in o[1:-1]:
        cur_con = Container(
            l[0:20].strip(),
            l[20:40].strip(),
            l[40:60].strip(),
            l[60:80].strip(),
            l[80:100].strip(),
            l[100:120].strip(),
            l[120:].strip(),
        )
        containers.append(cur_con)
    return containers


def dnets(id=None, type=None):
    """
    List the docker names of all docker networks.
    :param id: string, used to test for network presence.
    :param type: string, either 'custom' or 'builtin'
    :return: list
    """
    cmd = list(DNET) + [
        "ls",
        # '--filter', 'type=custom',
        "--format",
        "{{.Name}}",
    ]
    if id:
        cmd.extend(["--filter", "id={}".format(id)])
    if type is not None:
        if type == "custom":
            cmd.extend((["--filter", "type=custom"]))
        elif type == "builtin":
            cmd.extend((["--filter", "type=builtin"]))
        else:
            raise Exception("type must be custom or builtin")
    o, e, rc = run_command(cmd)
    return o[:-1]


def docker_status():
    o, e, rc = service_status("docker")
    if rc != 0:
        return False
    return True


def dnet_inspect(dname):
    """
    This function takes the name of a docker network as argument
    and returns a dict of its configuration.
    :param dname: docker network name
    :return: dict
    """
    cmd = list(DNET) + ["inspect", dname, "--format", "{{json .}}"]
    o, _, _ = run_command(cmd)
    return json.loads(o[0])
