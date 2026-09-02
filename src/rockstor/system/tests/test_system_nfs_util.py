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
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""

import os
from pyfakefs.fake_filesystem_unittest import TestCase
from unittest.mock import patch

from system.constants import NFS_CONFIG
from system.nfs_util import remove_nfs_export

INITIAL_NFS_CONFIG = r"""
/export/nfs_export1 *(rw,async,insecure)
/export/nfs_export2 192.168.2.2(rw,no_root_squash,async,insecure)
/export/nfs_export3 192.168.2.4(ro,sync,insecure)  adminhost.lan(rw,no_root_squash)
"""

ONE_EXPORT_REMOVED_NFS_CONFIG = r"""
/export/nfs_export1 *(rw,async,insecure)
/export/nfs_export3 192.168.2.4(ro,sync,insecure)  adminhost.lan(rw,no_root_squash)
"""

ALL_EXPORTS_REMOVED_NFS_CONFIG = r"""
"""

class SystemNfsUtilTests(TestCase):
    """
    The tests in this suite can be run via the following command:
    cd /opt/rockstor/src/rockstor
    poetry run django-admin test -p test_system_nfs_util.py -v 2
    ...
    For NFS API tests see: storageadmin/tests/test_nfs_export.py
    """

    @classmethod
    def setUpClass(cls):
        cls.setUpClassPyfakefs()
        # Re-establish the start-state of the filesystem before every test.
        cls.fake_fs().create_file(NFS_CONFIG, contents=INITIAL_NFS_CONFIG)

    def setUp(self):
        self.patch_bindmount = patch("system.nfs_util.bind_mount")
        self.mock_bindmount = self.patch_bindmount.start()

    def tearDown(self):
        # No necessity for self.tearDownPyfakefs()
        patch.stopall()

    def test_remove_nfs_export(self):
        self.assertTrue(os.path.exists(NFS_CONFIG))
        self.assertTrue(remove_nfs_export(["nfs_export2"]))
        self.assertFalse(remove_nfs_export(["non-existent-share"]))
        with open(NFS_CONFIG) as written_content:
            self.assertEqual(written_content.read(), ONE_EXPORT_REMOVED_NFS_CONFIG)
        self.assertTrue(remove_nfs_export(["nfs_export1", "nfs_export3"]))
        with open(NFS_CONFIG) as written_content:
            self.assertEqual(written_content.read(), ALL_EXPORTS_REMOVED_NFS_CONFIG)
        self.assertFalse(remove_nfs_export([]))
        self.assertFalse(remove_nfs_export(["", ""]))
        os.remove(NFS_CONFIG)
        self.assertFalse(os.path.exists(NFS_CONFIG))
        # Ensure robustness to no NFS_CONFIG file existing.
        self.assertFalse(remove_nfs_export(["some-share"]))