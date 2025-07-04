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
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""


from rest_framework import status
from storageadmin.tests.test_api import APITestMixin


class LoginTests(APITestMixin):
    # Proposed fixture "test_login.json" was "fix2.json"
    fixtures = ["test_api.json"]
    BASE_URL = "/api/login"

    @classmethod
    def setUpClass(cls):
        super(LoginTests, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        super(LoginTests, cls).tearDownClass()

    def test_post_requests(self):

        # Unauthorised user
        data = {"username": "admin", "password": "invalid"}
        response = self.client.post(self.BASE_URL, data=data)
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED, msg=response.data
        )

        # TODO:
        # The following fails but we have admin/admin setup in APITestMixin.
        # also on real system
        # curl -d "username=admin&password=admin" --insecure -X POST
        # https://127.0.0.1:443/api/login
        # logs 200 in "/var/log/nginx/access.log"

        # # happy path
        # data = {'username': 'admin', 'password': 'admin'}
        # response = self.client.post(self.BASE_URL, data=data)
        # self.assertEqual(response.status_code,
        #                  status.HTTP_200_OK, msg=response.data)
