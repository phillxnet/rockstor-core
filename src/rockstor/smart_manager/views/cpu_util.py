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

from smart_manager.models import CPUMetric
from smart_manager.serializers import CPUMetricSerializer
from smart_manager.views.generic_sprobe import GenericSProbeView


class CPUMetricView(GenericSProbeView):

    serializer_class = CPUMetricSerializer
    model_obj = CPUMetric
