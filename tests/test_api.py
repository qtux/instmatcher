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
		self.url = 'http://' + host + ':' + str(port)
		self.server = GrobidServer(host, port)
		self.server.start()
	
	def tearDown(self):
		self.server.stop()
	
	def test_match_None(self):
		self.assertEqual(instmatcher.match('', self.url), None)
	
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
		self.assertEqual(instmatcher.match(arg, self.url), expected)
	
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
			'lat': 51.7611,
			'lon': -1.2534,
			'isni': '0000 0004 1936 8948',
			'source': 'http://www.wikidata.org/entity/Q34433',
			'type': 'university',
		}
		self.assertEqual(instmatcher.match(arg, self.url), expected)
