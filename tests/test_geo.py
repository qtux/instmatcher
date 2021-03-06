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
from instmatcher import geo

class test_geo(unittest.TestCase):
	
	def test_None(self):
		actual = list(geo.geocodeAll(None, None))
		expected = []
		self.assertSequenceEqual(actual, expected)
	
	def test_Turyan(self):
		actual = list(geo.geocodeAll('Turyan', None))
		expected = []
		self.assertSequenceEqual(actual, expected)
	
	def test_Sao(self):
		actual = list(geo.geocodeAll('Sao Paulo', None))
		expected = [
			{'lat': -23.5475, 'lon': -46.63611, 'locality': 'São Paulo',},
			{'lat': -10.54944, 'lon': -37.53444, 'locality': 'Frei Paulo',},
		]
		self.assertSequenceEqual(actual, expected)
	
	def test_Sao_diacritic(self):
		actual = list(geo.geocodeAll('São Paulo', None))
		expected = [
			{'lat': -23.5475, 'lon': -46.63611, 'locality': 'São Paulo',},
			{'lat': -10.54944, 'lon': -37.53444, 'locality': 'Frei Paulo',},
		]
		self.assertSequenceEqual(actual, expected)
	
	def test_Xian_None(self):
		actual = list(geo.geocodeAll('Xian', None))
		expected = [
			{'lat': 34.25833, 'lon': 108.92861, 'locality': 'Xi’an',},
		]
		self.assertSequenceEqual(actual, expected)
	
	def test_Xian_CN(self):
		actual = list(geo.geocodeAll('Xian', 'CN'))
		expected = [
			{'lat': 34.25833, 'lon': 108.92861, 'locality': 'Xi’an',},
		]
		self.assertSequenceEqual(actual, expected)
	
	def test_Gutao_None(self):
		actual = list(geo.geocodeAll('Gutao', None))
		expected = [
			{'lat': 37.2025, 'lon': 112.17806, 'locality': 'Gutao',},
		]
		self.assertSequenceEqual(actual, expected)
	
	def test_Gutao_CN(self):
		actual = list(geo.geocodeAll('Gutao', 'CN'))
		expected = [
			{'lat': 37.2025, 'lon': 112.17806, 'locality': 'Gutao',},
		]
		self.assertSequenceEqual(actual, expected)
	
	def test_Boston_None(self):
		actual = list(geo.geocodeAll('Boston', None))
		expected = [
			{'lat': 42.35843, 'lon': -71.05977, 'locality': 'Boston',},
			{'lat': 52.97633, 'lon': -0.02664, 'locality': 'Boston',},
			{'lat': 7.87111, 'lon': 126.36417, 'locality': 'Boston',},
			{'lat': 30.79186, 'lon': -83.78989, 'locality': 'Boston',},
		]
		self.assertSequenceEqual(actual, expected)
	
	def test_Boston_US(self):
		actual = list(geo.geocodeAll('Boston', 'US'))
		expected = [
			{'lat': 42.35843, 'lon': -71.05977, 'locality': 'Boston',},
			{'lat': 30.79186, 'lon': -83.78989, 'locality': 'Boston',},
		]
		self.assertSequenceEqual(actual, expected)
	
	def test_London_None(self):
		actual = list(geo.geocodeAll('London', None))
		expected = [
			{'lat': 51.50853, 'lon': -0.12574, 'locality': 'London',},
			{'lat': 42.98339, 'lon': -81.23304, 'locality': 'London',},
			{'lat': 37.12898, 'lon': -84.08326, 'locality': 'London',},
			{'lat': 39.88645, 'lon': -83.44825, 'locality': 'London',},
			{'lat': 51.51279, 'lon': -0.09184, 'locality': 'City of London',},
			{'lat': 36.47606, 'lon': -119.44318, 'locality': 'London',},
			{'lat': 35.32897, 'lon': -93.25296, 'locality': 'London',},
			{'lat': 1.98487, 'lon': -157.47502, 'locality': 'London Village',},
		]
		self.assertSequenceEqual(actual, expected)
	
	def test_London_GB(self):
		actual = list(geo.geocodeAll('London', 'GB'))
		expected = [
			{'lat': 51.50853, 'lon': -0.12574, 'locality': 'London',},
			{'lat': 51.51279, 'lon': -0.09184, 'locality': 'City of London',},
		]
		self.assertSequenceEqual(actual, expected)
	
	def test_London_CA(self):
		actual = list(geo.geocodeAll('London', 'CA'))
		expected = [
			{'lat': 42.98339, 'lon': -81.23304, 'locality': 'London',},
		]
		self.assertSequenceEqual(actual, expected)
	
	def test_London_IT(self):
		actual = list(geo.geocodeAll('London', 'IT'))
		expected = []
		self.assertSequenceEqual(actual, expected)
	
	def test_St_Petersburg_RU(self):
		actual = list(geo.geocodeAll('St Petersburg', 'RU'))
		expected = [{
			'lat': 59.93863,
			'lon': 30.31413,
			'locality': 'Saint Petersburg',
		},]
		self.assertSequenceEqual(actual, expected)
	
	def test_St_Petersburg_RU_wrong_case(self):
		actual = list(geo.geocodeAll('st peTERSBURg', 'RU'))
		expected = [{
			'lat': 59.93863,
			'lon': 30.31413,
			'locality': 'Saint Petersburg',
		},]
		self.assertSequenceEqual(actual, expected)
	
	def test_with_comma(self):
		actual = list(geo.geocodeAll('Pohang, Kyungbuk', 'KR'))
		expected = []
		self.assertSequenceEqual(actual, expected)
	
	def test_Santiago_De_Compostela(self):
		actual = list(geo.geocodeAll('Santiago De Compostela', None))
		expected = [{
			'lat': 42.88052,
			'lon': -8.54569,
			'locality': 'Santiago de Compostela',
		},]
		self.assertSequenceEqual(actual, expected)
	
	def test_Gif_Sur_Yvette_without_hyphens(self):
		actual = list(geo.geocodeAll('Gif Sur Yvette', None))
		expected = [{
			'lat': 48.68333,
			'lon': 2.13333,
			'locality': 'Gif-sur-Yvette',
		},]
		self.assertSequenceEqual(actual, expected)
