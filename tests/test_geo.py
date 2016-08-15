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
from instmatcher.geo import init, geocode

import os
from itertools import zip_longest

cases = {
	(None, None): [],
	('x', None): [],
	('Turyan', None): [],
	('Klin Geriatr, Hamburg', 'DE'): [],
	('Sao Paulo',	None): [
		{'lat': -23.5475, 'lon': -46.63611, 'alpha2': 'BR', 'country': 'Brazil'},
	],
	('São Paulo',	None): [
		{'lat': -23.5475, 'lon': -46.63611, 'alpha2': 'BR', 'country': 'Brazil'},
	],
	('São Paulo',	'BR'): [
		{'lat': -23.5475, 'lon': -46.63611, 'alpha2': 'BR', 'country': 'Brazil'},
	],
	('Sao Paulo',	'BR'): [
		{'lat': -23.5475, 'lon': -46.63611, 'alpha2': 'BR', 'country': 'Brazil'},
	],
	('Xian', None): [
		{'lat': 34.25833, 'lon': 108.92861, 'alpha2': 'CN', 'country': 'China'},
	],
	('Xian', 'CN'): [
		{'lat': 34.25833, 'lon': 108.92861, 'alpha2': 'CN', 'country': 'China'},
	],
	('Gutao', None): [
		{'lat': 37.2025, 'lon': 112.17806, 'alpha2': 'CN', 'country': 'China'},
	],
	('Gutao', 'CN'): [
		{'lat': 37.2025, 'lon': 112.17806, 'alpha2': 'CN', 'country': 'China'},
	],
	('Boston', None): [
		{'lat': 42.35843, 'lon': -71.05977, 'alpha2': 'US', 'country': 'United States'},
		{'lat': 52.97633, 'lon': -0.02664, 'alpha2': 'GB', 'country': 'United Kingdom'},
		{'lat': 7.87111, 'lon': 126.36417, 'alpha2': 'PH', 'country': 'Philippines'},
		{'lat': 30.79186, 'lon': -83.78989, 'alpha2': 'US', 'country': 'United States'},
	],
	('Boston', 'US'): [
		{'lat': 42.35843, 'lon': -71.05977, 'alpha2': 'US', 'country': 'United States'},
		{'lat': 30.79186, 'lon': -83.78989, 'alpha2': 'US', 'country': 'United States'},
	],
	('London', None): [
		{'lat': 51.50853, 'lon': -0.12574, 'alpha2': 'GB', 'country': 'United Kingdom'},
		{'lat': 42.98339, 'lon': -81.23304, 'alpha2': 'CA', 'country': 'Canada'},
		{'lat': 37.12898, 'lon': -84.08326, 'alpha2': 'US', 'country': 'United States'},
		{'lat': 39.88645, 'lon': -83.44825, 'alpha2': 'US', 'country': 'United States'},
		{'lat': 51.51279, 'lon': -0.09184, 'alpha2': 'GB', 'country': 'United Kingdom'},
		{'lat': 36.47606, 'lon': -119.44318, 'alpha2': 'US', 'country': 'United States'},
		{'lat': 35.32897, 'lon': -93.25296, 'alpha2': 'US', 'country': 'United States'},
		{'lat': 1.98487, 'lon': -157.47502, 'alpha2': 'KI', 'country': 'Kiribati'},
	],
	('London', 'GB'): [
		{'lat': 51.50853, 'lon': -0.12574, 'alpha2': 'GB', 'country': 'United Kingdom'},
		{'lat': 51.51279, 'lon': -0.09184, 'alpha2': 'GB', 'country': 'United Kingdom'},
	],
	('London', 'CA'): [
		{'lat': 42.98339, 'lon': -81.23304, 'alpha2': 'CA', 'country': 'Canada'},
	],
	('London', 'IT'): [],
}

class test_geo(unittest.TestCase):
	
	def setUp(self):
		init(procs=os.cpu_count(), multisegment=True, ixPath='./geoindex')
	
	def test_geocode(self):
		for args, targets in cases.items():
			coords = geocode(*args)
			for result, target in zip_longest(coords, targets):
				self.assertEqual(result, target, msg=args)

if __name__ == '__main__':
	init(procs=os.cpu_count(), multisegment=True, ixPath='./geoindex')
	for query in cases.keys():
		positions = geocode(*query)
		print('', query,': [', sep='')
		for pos in positions:
			print('\t', pos, ',', sep='')
		print('],')
