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

import os
import shutil
import time
from tempfile import mkstemp

from system.constants import MKDIR, MOUNT, UMOUNT, RMDIR, NFS_CONFIG, NFS_EXPORT_ROOT
from system.osi import run_command, is_mounted, toggle_path_rw

EXPORTFS = "/usr/sbin/exportfs"


"""
This file is to contain intentionally low-level facilities.
Some may be directly involved in Django model definitions.
It is therefor imperative/required that no related Django
model be import as this creates a circular dependency:
I.e.:
- Model requires this file's contents to initialise.
- This file requires related model to be initialised.
"""


def nfs4_mount_teardown(export_pt):
    """
    reverse of setup. cleanup when there are no more exports
    """
    if is_mounted(export_pt):
        run_command([UMOUNT, "-l", export_pt])
        for i in range(10):
            if not is_mounted(export_pt):
                toggle_path_rw(export_pt, rw=True)
                return run_command([RMDIR, export_pt])
            time.sleep(1)
        run_command([UMOUNT, "-f", export_pt])
    if os.path.exists(export_pt):
        toggle_path_rw(export_pt, rw=True)
        run_command([RMDIR, export_pt])
    return True


def bind_mount(mnt_pt, export_pt):
    if not is_mounted(export_pt):
        run_command([MKDIR, "-p", export_pt])
        toggle_path_rw(export_pt, rw=False)
        return run_command([MOUNT, "--bind", mnt_pt, export_pt])
    return True


def refresh_nfs_exports(exports):
    """
    input format:

    {'export_point': [{'client_str': 'www.example.com',
                       'option_list': 'rw,insecure,'
                       'mnt_pt': mnt_pt,},],
                       ...}

    if 'clients' is an empty list, then unmount and cleanup.
    """
    fo, npath = mkstemp()
    with open(npath, "w") as efo:
        shares = []
        for e in exports.keys():
            if len(exports[e]) == 0:
                #  do share tear down at the end, only snaps here
                if len(e.split("/")) == 4:
                    nfs4_mount_teardown(e)
                else:
                    shares.append(e)
                continue

            if not is_mounted(e):
                bind_mount(exports[e][0]["mnt_pt"], e)
            client_str = ""
            admin_host = None
            for c in exports[e]:
                run_command(
                    [
                        EXPORTFS,
                        "-i",
                        "-o",
                        c["option_list"],
                        "{}:{}".format(c["client_str"], e),
                    ]
                )
                # TODO we have a trailing space here - likely to accommodate multiple
                #  entries but still!!
                client_str = "{}{}({}) ".format(
                    client_str, c["client_str"], c["option_list"]
                )
                if "admin_host" in c:
                    admin_host = c["admin_host"]
            if admin_host is not None:
                run_command(
                    [
                        EXPORTFS,
                        "-i",
                        "-o",
                        "rw,no_root_squash",
                        "{}:{}".format(admin_host, e),
                    ]
                )
                client_str = "{} {}(rw,no_root_squash)".format(client_str, admin_host)
            export_str = "{} {}\n".format(e, client_str)
            efo.write(export_str)
        for s in shares:
            nfs4_mount_teardown(s)
    shutil.move(npath, NFS_CONFIG)
    return run_command([EXPORTFS, "-ra"])


def remove_nfs_export(share_name_list: list[str]) -> bool:
    """
    Intended as a light-weight option to remove all NFS export entries
    pertaining to the passed list of Share.names. Intentionally low-level
    to facilitate rapid adaptation of /etc/exports to mass Share removal
    such as when a Pool's management is deleted.
    :param share_name_list: List of Share names to remove, if found, in /etc/exports.
    :return: Bool on changes written.
    """
    if not os.path.exists(NFS_CONFIG) or share_name_list == []:
        return False
    nfs_modified: bool = False
    fh, npath = mkstemp()
    with open(NFS_CONFIG, "r") as nfs_exports, open(npath, "w") as temp_file:
        for line in nfs_exports:
            if any(
                line.startswith(f"{NFS_EXPORT_ROOT}{share_name}")
                for share_name in share_name_list
            ):
                nfs_modified = True
                continue
            else:
                temp_file.write(line)
    if nfs_modified:
        shutil.move(npath, NFS_CONFIG)
        return nfs_modified
    else:
        os.remove(npath)
    return False
