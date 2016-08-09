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
from instmatcher.geo import init, geocode, geocodeAll

import os
from itertools import zip_longest

cases = {
	(None, None): [],
	('x', None): [],
	('Turyan', None): [],
	('Klin Geriatr, Hamburg', 'DE'): [],
	('Sao Paulo',	None): [(-23.5475, -46.63611)],
	('São Paulo',	None): [(-23.5475, -46.63611)],
	('São Paulo',	'BR'): [(-23.5475, -46.63611)],
	('Sao Paulo',	'BR'): [(-23.5475, -46.63611)],
	('Xian', None): [(34.25833, 108.92861)],
	('Xian', 'CN'): [(34.25833, 108.92861)],
	('Gutao', None): [(37.2025, 112.17806)],
	('Gutao', 'CN'): [(37.2025, 112.17806)],
	('Boston', None): [
		(42.35843, -71.05977),
		(52.97633, -0.02664),
		(7.87111, 126.36417),
		(30.79186, -83.78989),
	],
	('Boston', 'US'): [
		(42.35843, -71.05977),
		(30.79186, -83.78989),
	],
	('London', None): [
		(51.50853, -0.12574),
		(42.98339, -81.23304),
		(37.12898, -84.08326),
		(39.88645, -83.44825),
		(51.51279, -0.09184),
		(36.47606, -119.44318),
		(35.32897, -93.25296),
		(1.98487, -157.47502),
	],
	('London', 'GB'): [
		(51.50853, -0.12574),
		(51.51279, -0.09184),
	],
	('London', 'CA'): [(42.98339, -81.23304)],
}

class test_geo(unittest.TestCase):
	
	def setUp(self):
		init(procs=os.cpu_count(), multisegment=True)
	
	def test_geocode(self):
		for args, targets in cases.items():
			coords = geocode(*args)
			for target in targets:
				self.assertEqual(coords, target, msg=args)
				break
			else:
				self.assertEqual(coords, (None, None), msg=args)
	
	def test_geocodeAll(self):
		for args, targets in cases.items():
			coords = geocodeAll(*args)
			for result, target in zip_longest(coords, targets):
				self.assertEqual(result, target, msg=args)

if __name__ == '__main__':
	init(procs=os.cpu_count(), multisegment=True)
	for query, coords in cases.items():
		coords = geocodeAll(*query)
		print('', query,': [', sep='')
		for latlon in coords:
			print('\t', latlon, ',', sep='')
		print('],')
