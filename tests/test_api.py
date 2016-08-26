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

from .util import GrobidServer
import os

import unittest
import instmatcher

class test_api(unittest.TestCase):
	
	def setUp(self):
		host = 'localhost'
		port = 8081
		url = 'http://' + host + ':' + str(port)
		grobidResponses = {
			'University of Oxford, Oxford, UK':
				'''<affiliation>
					<orgName type="institution">University of Oxford</orgName>
					<address>
						<settlement>Oxford</settlement>
						<country key="GB">UK</country>
					</address>
				</affiliation>''',
			'Charles University in Prague':
				'''<affiliation>
					<orgName type="institution">Charles University</orgName>
					<address>
						<settlement>Prague</settlement>
					</address>
				</affiliation>''',
			'University of London, London':
				'''<affiliation>
					<orgName type="institution">University of London</orgName>
					<address>
						<settlement>London</settlement>
					</address>
				</affiliation>''',
			'Unknown':
				'''<affiliation>
					<address>
						<country>Unknown</country>
					</address>
				</affiliation>''',
		}
		host = 'localhost'
		port = 8081
		url = 'http://' + host + ':' + str(port)
		instmatcher.init(procs=os.cpu_count(), initGeo=True, grobidUrl=url)
		self.server = GrobidServer(host, port, grobidResponses)
		self.server.start()
	
	def test_find(self):
		cases = {
			None: [],
			'University of Fantasia': [],
			'Univ Boston': [
				{
					'name': 'Boston University',
					'alpha2': 'US',
					'country': 'United States',
					'lat': '42.3496',
					'lon': '-71.0997',
					'isni': '',
				},{
					'name': 'University of Massachusetts Boston',
					'alpha2': 'US',
					'country': 'United States',
					'lat': '42.313432',
					'lon': '-71.038445',
					'isni': '',
				},{
					'name': 'Northeastern University',
					'alpha2': 'US',
					'country': 'United States',
					'lat': '42.338888888889',
					'lon': '-71.090277777778',
					'isni': '',
				},
			],
			'TU Berlin': [
				{
					'name': 'Technical University of Berlin',
					'alpha2': 'DE',
					'country': 'Germany',
					'lat': '52.511944444444',
					'lon': '13.326388888889',
					'isni': '0000 0001 2195 9817',
				}
			],
		}
		
		for args, targets in cases.items():
			singleResult = instmatcher.find(args)
			allResults = instmatcher.findAll(args)
			singleTested = False
			for result, target in zip(allResults, targets):
				if not singleTested:
					self.assertEqual(result, singleResult)
					singleTested = True
				self.assertEqual(result, target)
		
	def test_extract(self):
		cases = {
			'Unknown': [
				{
					'institute': None,
					'city': None,
					'alpha2': None,
					'country': None,
				},
			],
			'Charles University in Prague': [
				{
					'institute': 'Charles University',
					'city': 'Prague',
					'alpha2': 'CZ',
					'country': 'Czech Republic',
					'lat': 50.08804,
					'lon': 14.42076,
				},{
					'institute': 'Charles University',
					'city': 'Prague',
					'alpha2': 'US',
					'country': 'United States',
					'lat': 35.48674,
					'lon': -96.68502,
				},
			],
			'University of London, London': [
				{
					'institute': 'University of London',
					'city': 'London',
					'alpha2': 'GB',
					'country': 'United Kingdom',
					'lat': 51.50853,
					'lon': -0.12574,
				},{
					'institute': 'University of London',
					'city': 'London',
					'alpha2': 'CA',
					'country': 'Canada',
					'lat': 42.98339,
					'lon': -81.23304,
				},{
					'institute': 'University of London',
					'city': 'London',
					'alpha2':'US',
					'country': 'United States',
					'lat': 37.12898,
					'lon': -84.08326,
				},{
					'institute': 'University of London',
					'city': 'London',
					'alpha2': 'US',
					'country': 'United States',
					'lat': 39.88645,
					'lon': -83.44825,
				},{
					'institute': 'University of London',
					'city': 'London',
					'alpha2': 'GB',
					'country': 'United Kingdom',
					'lat': 51.51279,
					'lon': -0.09184,
				},{
					'institute':'University of London',
					'city': 'London',
					'alpha2': 'US',
					'country': 'United States',
					'lat': 36.47606,
					'lon': -119.44318,
				},{
					'institute': 'University of London',
					'city': 'London',
					'alpha2': 'US',
					'country': 'United States',
					'lat': 35.32897,
					'lon': -93.25296,
				},{
					'institute': 'University of London',
					'city': 'London',
					'alpha2': 'KI',
					'country': 'Kiribati',
					'lat': 1.98487,
					'lon': -157.47502,
				},
			],
		}
		for args, targets in cases.items():
			singleResult = instmatcher.extract(args)
			allResults = instmatcher.extractAll(args)
			singleTested = False
			for result, target in zip(allResults, targets):
				if not singleTested:
					self.assertEqual(result, singleResult)
					singleTested = True
				self.assertEqual(result, target)
	
	def test_match(self):
		cases = {
			'': None,
			'Unknown': None,
			'University of Oxford, Oxford, UK': {
				'name': 'University of Oxford',
				'alpha2': 'GB',
				'country': 'United Kingdom',
				'lat': '51.7611',
				'lon': '-1.2534',
				'isni': '0000 0004 1936 8948',
			},
		}
		for arg, target in cases.items():
			self.assertEqual(instmatcher.match(arg), target)
	
	def tearDown(self):
		self.server.stop()
