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
import instmatcher
from .util import GrobidServer

class test_api(unittest.TestCase):
	
	def setUp(self):
		host = 'localhost'
		port = 8081
		url = 'http://' + host + ':' + str(port)
		instmatcher.init(grobidUrl=url)
		self.server = GrobidServer(host, port)
		self.server.start()
	
	def tearDown(self):
		self.server.stop()
	
	def assert_find_functions(self, arg, expected):
		first = expected[0] if expected else None
		self.assertSequenceEqual(list(instmatcher.findAll(arg)), expected)
		self.assertEqual(instmatcher.find(arg), first)
	
	def assert_extract_functions(self, arg, expected):
		first = expected[0] if expected else None
		self.assertSequenceEqual(list(instmatcher.extractAll(arg)), expected)
		self.assertEqual(instmatcher.extract(arg), first)
	
	def test_find_None(self):
		self.assert_find_functions(None, [])
	
	def test_find_String(self):
		self.assert_find_functions('University of Madrid', [])
	
	def test_find_empty(self):
		self.assert_find_functions([], [])
	
	def test_find_None_list(self):
		self.assert_find_functions([None, None,], [])
	
	def test_find_Univ_Fantasia(self):
		self.assert_find_functions(['University of Fantasia',], [])
	
	def test_find_Univ_Boston(self):
		arg = ['Univ Boston',]
		expected = [
			{
				'name': 'Boston University',
				'alpha2': 'US',
				'country': 'United States',
				'lat': '42.3496',
				'lon': '-71.0997',
				'isni': '',
				'source': 'http://www.wikidata.org/entity/Q49110',
				'type': 'university',
			},{
				'name': 'University of Massachusetts Boston',
				'alpha2': 'US',
				'country': 'United States',
				'lat': '42.313432',
				'lon': '-71.038445',
				'isni': '',
				'source': 'http://www.wikidata.org/entity/Q15144',
				'type': 'university',
			},{
				'name': 'Northeastern University',
				'alpha2': 'US',
				'country': 'United States',
				'lat': '42.338888888889',
				'lon': '-71.090277777778',
				'isni': '',
				'source': 'http://www.wikidata.org/entity/Q37548',
				'type': 'university',
			},
		]
		self.assert_find_functions(arg, expected)
	
	def test_find_TU_Berlin(self):
		arg = ['TU Berlin',]
		expected = [
			{
				'name': 'Technical University of Berlin',
				'alpha2': 'DE',
				'country': 'Germany',
				'lat': '52.511944444444',
				'lon': '13.326388888889',
				'isni': '0000 0001 2195 9817',
				'source': 'http://www.wikidata.org/entity/Q51985',
				'type': 'university',
			}
		]
		self.assert_find_functions(arg, expected)
	
	def test_extract_None(self):
		arg = None
		expected = [
			{
				'institution': [],
				'settlement': [],
				'alpha2': None,
			},
		]
		self.assert_extract_functions(arg, expected)
	
	def test_extract_Unknown(self):
		arg = 'Unknown'
		expected = [
			{
				'institution': [],
				'settlement': [],
				'alpha2': None,
			},
		]
		self.assert_extract_functions(arg, expected)
	
	def test_extract_Prague(self):
		arg = 'Charles University in Prague'
		self.server.setResponse(
			arg,
			'''<affiliation>
				<orgName type="institution">Charles University</orgName>
				<address>
					<settlement>Prague</settlement>
					<region>Prague</region>
					<country key="CZ">Czech Republic</country>
				</address>
			</affiliation>'''
		)
		expected = [
			{
				'institution': ['Charles University',],
				'settlement': ['Prague',],
				'alpha2': 'CZ',
				'country': 'Czechia',
				'countrySource': 'grobid',
				'lat': 50.08804,
				'lon': 14.42076,
				'locality': 'Prague',
				'region': 'Prague',
			},
		]
		self.assert_extract_functions(arg, expected)
	
	def test_find_Univ_Leuven(self):
		arg = ['Univ Leuven',]
		expected = [
			{
				'name': 'Katholieke Universiteit Leuven Campus Kortrijk',
				'alpha2': 'BE',
				 'country': 'Belgium',
				'lat': '50.806139',
				'lon': '3.291939',
				'isni': '',
				'source': 'http://www.wikidata.org/entity/Q1736308',
				'type': 'university',
			},{
				'name': 'Catholic University of Leuven',
				'alpha2': 'BE',
				 'country': 'Belgium',
				'lat': '50.669722222222',
				'lon': '4.6122222222222',
				'isni': '',
				'source': 'http://www.wikidata.org/entity/Q5121415',
				'type': 'university',
			},
		]
		self.assert_find_functions(arg, expected)
	
	def test_find_Univ_Louvain(self):
		arg = ['Univ Louvain',]
		expected = [
			{
				'name': 'Université catholique de Louvain',
				'alpha2': 'BE',
				'country': 'Belgium',
				'lat': '50.669611111111',
				'lon': '4.6122638888889',
				'isni': '',
				'source': 'http://www.wikidata.org/entity/Q378134',
				'type': 'university',
			},
		]
		self.assert_find_functions(arg, expected)
	
	def test_extract_London(self):
		arg = 'University of London, London'
		self.server.setResponse(
			arg,
			'''<affiliation>
				<orgName type="institution">University of London</orgName>
				<address>
					<settlement>London</settlement>
					<region>London</region>
				</address>
			</affiliation>'''
		)
		expected = [
			{
				'institution': ['University of London',],
				'settlement': ['University of London', 'London',],
				'alpha2': None,
				'lat': 51.50853,
				'lon': -0.12574,
				'locality': 'London',
				'region': 'London',
			},{
				'institution': ['University of London',],
				'settlement': ['University of London', 'London',],
				'alpha2': None,
				'lat': 42.98339,
				'lon': -81.23304,
				'locality': 'London',
				'region': 'London',
			},{
				'institution': ['University of London',],
				'settlement': ['University of London', 'London',],
				'alpha2': None,
				'lat': 37.12898,
				'lon': -84.08326,
				'locality': 'London',
				'region': 'London',
			},{
				'institution': ['University of London',],
				'settlement': ['University of London', 'London',],
				'alpha2': None,
				'lat': 39.88645,
				'lon': -83.44825,
				'locality': 'London',
				'region': 'London',
			},{
				'institution': ['University of London',],
				'settlement': ['University of London', 'London',],
				'alpha2': None,
				'lat': 51.51279,
				'lon': -0.09184,
				'locality': 'City of London',
				'region': 'London',
			},{
				'institution': ['University of London',],
				'settlement': ['University of London', 'London',],
				'alpha2': None,
				'lat': 36.47606,
				'lon': -119.44318,
				'locality': 'London',
				'region': 'London',
			},{
				'institution': ['University of London',],
				'settlement': ['University of London', 'London',],
				'alpha2': None,
				'lat': 35.32897,
				'lon': -93.25296,
				'locality': 'London',
				'region': 'London',
			},{
				'institution': ['University of London',],
				'settlement': ['University of London', 'London',],
				'alpha2': None,
				'lat': 1.98487,
				'lon': -157.47502,
				'locality': 'London Village',
				'region': 'London',
			},
		]
		self.assert_extract_functions(arg, expected)
	
	def test_match_None(self):
		self.assertEqual(instmatcher.match(''), None)
	
	def test_match_Unknown(self):
		arg = 'Unknown'
		self.server.setResponse(
			arg,
			'''<affiliation>
				<address>
					<country>Unknown</country>
				</address>
			</affiliation>'''
		)
		expected = None
		self.assertEqual(instmatcher.match(arg), expected)
	
	def test_match_Known(self):
		arg = 'University of Oxford, Oxford, UK'
		self.server.setResponse(
			arg,
			'''<affiliation>
				<orgName type="institution">University of Oxford</orgName>
				<address>
					<settlement>Oxford</settlement>
					<country key="GB">UK</country>
				</address>
			</affiliation>'''
		)
		expected = {
			'name': 'University of Oxford',
			'alpha2': 'GB',
			'country': 'United Kingdom',
			'lat': '51.7611',
			'lon': '-1.2534',
			'isni': '0000 0004 1936 8948',
			'source': 'http://www.wikidata.org/entity/Q34433',
			'type': 'university',
		}
		self.assertEqual(instmatcher.match(arg), expected)
