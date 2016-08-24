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
import pycountry
from instmatcher import countries

class test_countries(unittest.TestCase):
	
	def test_ISO(self):
		for country in list(pycountry.countries):
			# check searching with alpha2
			alpha2 = country.alpha2
			newCountry = countries.get(alpha2=alpha2)
			oldCountry = pycountry.countries.get(alpha2=alpha2)
			self.assertEqual(newCountry, oldCountry)
			
			# check searching with alpha3
			alpha3 = country.alpha3
			newCountry = countries.get(alpha3=alpha3)
			oldCountry = pycountry.countries.get(alpha3=alpha3)
			self.assertEqual(newCountry, oldCountry)
			
			# check searching with country name
			name = country.name
			newCountry = countries.get(name=name)
			oldCountry = pycountry.countries.get(name=name)
			self.assertEqual(newCountry, oldCountry)
			
			# check searching with official country name
			try:
				official_name = country.official_name
			except AttributeError:
				continue
			newCountry = countries.get(official_name=official_name)
			oldCountry = pycountry.countries.get(official_name=official_name)
			self.assertEqual(newCountry, oldCountry)
	
	def test_kosovo(self):
		kosovo = countries.kosovoObj
		
		# check searching with alpha2
		result = countries.get(alpha2='XK')
		self.assertEqual(result, kosovo)
		
		# check searching with alpha3
		result = countries.get(alpha3='UNK')
		self.assertEqual(result, kosovo)
		
		# check searching with country name
		result = countries.get(name='Kosovo')
		self.assertEqual(result, kosovo)
		
		# check searching with official country name
		result = countries.get(official_name='Republic of Kosovo')
		self.assertEqual(result, kosovo)
	
	def test_bad(self):
		with self.assertRaises(AssertionError):
			countries.get(alpha2='XK', alpha3='UNK')
		with self.assertRaises(KeyError):
			countries.get(name='Fantasia')
