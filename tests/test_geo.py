# Copyright 2016 Matthias Gazzari
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest
import os
from instmatcher.geo import init, geocode

class test_geo(unittest.TestCase):
	
	def setUp(self):
		init(procs=os.cpu_count(), multisegment=True)
	
	def test_cases(self):
		cases = {
			(None, None): (None, None),
			('x', None): (None, None),
			('Turyan', None): (None, None),
			('Klin Geriatr, Hamburg', 'DE'): (None, None),
			('Sao Paulo',	None): (-23.5475, -46.63611),
			('São Paulo',	None): (-23.5475, -46.63611),
			('São Paulo',	'BR'): (-23.5475, -46.63611),
			('Sao Paulo',	'BR'): (-23.5475, -46.63611),
			('Xian', None): (34.25833, 108.92861),
			('Xian', 'CN'): (34.25833, 108.92861),
			('Gutao', None): (37.2025, 112.17806),
			('Gutao', 'CN'): (37.2025, 112.17806),
			('Boston', None): (42.35843, -71.05977),
			('Boston', 'US'): (42.35843, -71.05977),
			('London', None): (51.50853, -0.12574),
			('London', 'GB'): (51.50853, -0.12574),
			('London', 'CA'): (42.98339, -81.23304),
		}
		for args, result in cases.items():
			self.assertEqual(geocode(*args), result, msg=args)
