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
		actual = list(geo.geocode(None, None))
		expected = []
		self.assertSequenceEqual(actual, expected)
	
	def test_Turyan(self):
		actual = list(geo.geocode('Turyan', None))
		expected = []
		self.assertSequenceEqual(actual, expected)
	
	def test_Sao(self):
		actual = list(geo.geocode('Sao Paulo', None))
		expected = [
			{'lat': -23.5475, 'lon': -46.63611, 'alpha2': 'BR', 'country': 'Brazil'},
		]
		self.assertSequenceEqual(actual, expected)
	
	def test_Sao_diacritic(self):
		actual = list(geo.geocode('São Paulo', None))
		expected = [
			{'lat': -23.5475, 'lon': -46.63611, 'alpha2': 'BR', 'country': 'Brazil'},
		]
		self.assertSequenceEqual(actual, expected)
	
	def test_Xian_None(self):
		actual = list(geo.geocode('Xian', None))
		expected = [
			{'lat': 34.25833, 'lon': 108.92861, 'alpha2': 'CN', 'country': 'China'},
		]
		self.assertSequenceEqual(actual, expected)
	
	def test_Xian_CN(self):
		actual = list(geo.geocode('Xian', 'CN'))
		expected = [
			{'lat': 34.25833, 'lon': 108.92861, 'alpha2': 'CN', 'country': 'China'},
		]
		self.assertSequenceEqual(actual, expected)
	
	def test_Gutao_None(self):
		actual = list(geo.geocode('Gutao', None))
		expected = [
			{'lat': 37.2025, 'lon': 112.17806, 'alpha2': 'CN', 'country': 'China'},
		]
		self.assertSequenceEqual(actual, expected)
	
	def test_Gutao_CN(self):
		actual = list(geo.geocode('Gutao', 'CN'))
		expected = [
			{'lat': 37.2025, 'lon': 112.17806, 'alpha2': 'CN', 'country': 'China'},
		]
		self.assertSequenceEqual(actual, expected)
	
	def test_Boston_None(self):
		actual = list(geo.geocode('Boston', None))
		expected = [
			{'lat': 42.35843, 'lon': -71.05977, 'alpha2': 'US', 'country': 'United States'},
			{'lat': 52.97633, 'lon': -0.02664, 'alpha2': 'GB', 'country': 'United Kingdom'},
			{'lat': 7.87111, 'lon': 126.36417, 'alpha2': 'PH', 'country': 'Philippines'},
			{'lat': 30.79186, 'lon': -83.78989, 'alpha2': 'US', 'country': 'United States'},
		]
		self.assertSequenceEqual(actual, expected)
	
	def test_Boston_None(self):
		actual = list(geo.geocode('Boston', 'US'))
		expected = [
			{'lat': 42.35843, 'lon': -71.05977, 'alpha2': 'US', 'country': 'United States'},
			{'lat': 30.79186, 'lon': -83.78989, 'alpha2': 'US', 'country': 'United States'},
		]
		self.assertSequenceEqual(actual, expected)
	
	def test_London_None(self):
		actual = list(geo.geocode('London', None))
		expected = [
			{'lat': 51.50853, 'lon': -0.12574, 'alpha2': 'GB', 'country': 'United Kingdom'},
			{'lat': 42.98339, 'lon': -81.23304, 'alpha2': 'CA', 'country': 'Canada'},
			{'lat': 37.12898, 'lon': -84.08326, 'alpha2': 'US', 'country': 'United States'},
			{'lat': 39.88645, 'lon': -83.44825, 'alpha2': 'US', 'country': 'United States'},
			{'lat': 51.51279, 'lon': -0.09184, 'alpha2': 'GB', 'country': 'United Kingdom'},
			{'lat': 36.47606, 'lon': -119.44318, 'alpha2': 'US', 'country': 'United States'},
			{'lat': 35.32897, 'lon': -93.25296, 'alpha2': 'US', 'country': 'United States'},
			{'lat': 1.98487, 'lon': -157.47502, 'alpha2': 'KI', 'country': 'Kiribati'},
		]
		self.assertSequenceEqual(actual, expected)
	
	def test_London_GB(self):
		actual = list(geo.geocode('London', 'GB'))
		expected = [
			{'lat': 51.50853, 'lon': -0.12574, 'alpha2': 'GB', 'country': 'United Kingdom'},
			{'lat': 51.51279, 'lon': -0.09184, 'alpha2': 'GB', 'country': 'United Kingdom'},
		]
		self.assertSequenceEqual(actual, expected)
	
	def test_London_CA(self):
		actual = list(geo.geocode('London', 'CA'))
		expected = [
			{'lat': 42.98339, 'lon': -81.23304, 'alpha2': 'CA', 'country': 'Canada'},
		]
		self.assertSequenceEqual(actual, expected)
	
	def test_London_IT(self):
		actual = list(geo.geocode('London', 'IT'))
		expected = []
		self.assertSequenceEqual(actual, expected)
