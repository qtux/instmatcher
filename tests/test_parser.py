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
from .util import GrobidServer
from instmatcher import parser

class test_parser(unittest.TestCase):
	
	def setUp(self):
		host = 'localhost'
		port = 8081
		url = 'http://' + host + ':' + str(port)
		parser.init(url)
		self.server = GrobidServer(host, port)
		self.server.start()
	
	def tearDown(self):
		self.server.stop()
	
	def test_None(self):
		expected = {
			'institution': None,
			'alpha2': None,
			'country': None,
			'settlement': None,
			'region': None,
			'postCode': None,
		}
		self.assertEqual(parser.grobid(None), expected)
	
	def test_empty(self):
		self.server.setResponse(__name__, '')
		expected = {
			'institution': None,
			'alpha2': None,
			'country': None,
			'settlement': None,
			'region': None,
			'postCode': None,
		}
		self.assertEqual(parser.grobid(__name__), expected)
	
	def test_no_institution(self):
		self.server.setResponse(
			__name__,
			'''<affiliation>
			<address>
				<country key="AQ">Irrelevant</country>
				<settlement>settlement</settlement>
			</address>
			</affiliation>'''
		)
		expected = {
			'institution': None,
			'alpha2': 'AQ',
			'country': 'Antarctica',
			'settlement': 'settlement',
			'region': None,
			'postCode': None,
		}
		self.assertEqual(parser.grobid(__name__), expected)
	
	def test_no_alpha2(self):
		self.server.setResponse(
			__name__,
			'''<affiliation>
			<orgName type="institution">institA</orgName>
			<address>
				<country>country</country>
				<settlement>settlement</settlement>
			</address>
			</affiliation>'''
		)
		expected = {
			'institution': 'institA',
			'alpha2': None,
			'country': None,
			'settlement': 'settlement',
			'region': None,
			'postCode': None,
		}
		self.assertEqual(parser.grobid(__name__), expected)
	
	def test_no_country(self):
		self.server.setResponse(
			__name__,
			'''<affiliation>
			<orgName type="institution">institB</orgName>
			<address>
				<settlement>settlement</settlement>
			</address>
			</affiliation>'''
		)
		expected = {
			'institution': 'institB',
			'alpha2': None,
			'country': None,
			'settlement': 'settlement',
			'region': None,
			'postCode': None,
		}
		self.assertEqual(parser.grobid(__name__), expected)
	
	def test_no_settlement(self):
		self.server.setResponse(
			__name__,
			'''<affiliation>
			<orgName type="institution">institC</orgName>
			<address>
				<country key="AQ">Irrelevant</country>
			</address>
			</affiliation>'''
		)
		expected = {
			'institution': 'institC',
			'alpha2': 'AQ',
			'country': 'Antarctica',
			'settlement': None,
			'region': None,
			'postCode': None,
		}
		self.assertEqual(parser.grobid(__name__), expected)
	
	def test_not_regocnised_country(self):
		affiliation = 'institA, settlement, INDIA'
		self.server.setResponse(
			affiliation,
			'''<affiliation>
			<orgName type="institution">institA</orgName>
			<address>
				<settlement>settlement</settlement>
			</address>
			</affiliation>'''
		)
		expected = {
			'institution': 'institA',
			'alpha2': 'IN',
			'country': 'India',
			'settlement': 'settlement',
			'region': None,
			'postCode': None,
		}
		self.assertEqual(parser.grobid(affiliation), expected)
	
	def test_not_regocnised_bad_country(self):
		affiliation = 'institA, settlement, Fantasia'
		self.server.setResponse(
			affiliation,
			'''<affiliation>
			<orgName type="institution">institA</orgName>
			<address>
				<settlement>settlement</settlement>
			</address>
			</affiliation>'''
		)
		expected = {
			'institution': 'institA',
			'alpha2': None,
			'country': None,
			'settlement': 'settlement',
			'region': None,
			'postCode': None,
		}
		self.assertEqual(parser.grobid(affiliation), expected)
	
	def test_not_recognised_country_no_comma_in_affiliation_string(self):
		affiliation = 'institA settlement Algeria'
		self.server.setResponse(
			affiliation,
			'''<affiliation>
			<orgName type="institution">institA</orgName>
			<address>
				<settlement>settlement</settlement>
			</address>
			</affiliation>'''
		)
		expected = {
			'institution': 'institA',
			'alpha2': 'DZ',
			'country': 'Algeria',
			'settlement': 'settlement',
			'region': None,
			'postCode': None,
		}
		self.assertEqual(parser.grobid(affiliation), expected)
	
	def test_multiple_not_recognised_countries(self):
		affiliation = 'institA settlement Algeria India'
		self.server.setResponse(
			affiliation,
			'''<affiliation>
			<orgName type="institution">institA</orgName>
			<address>
				<settlement>settlement</settlement>
			</address>
			</affiliation>'''
		)
		expected = {
			'institution': 'institA',
			'alpha2': 'IN',
			'country': 'India',
			'settlement': 'settlement',
			'region': None,
			'postCode': None,
		}
		self.assertEqual(parser.grobid(affiliation), expected)
	
	def test_releveant_tags(self):
		self.server.setResponse(
			__name__,
			'''<affiliation>
			<orgName type="institution">institD</orgName>
			<address>
				<country key="AQ">Irrelevant</country>
				<settlement>settlement</settlement>
			</address>
			</affiliation>'''
		)
		expected = {
			'institution': 'institD',
			'alpha2': 'AQ',
			'country': 'Antarctica',
			'settlement': 'settlement',
			'region': None,
			'postCode': None,
		}
		self.assertEqual(parser.grobid(__name__), expected)
	
	def test_every_tags(self):
		self.server.setResponse(
			__name__,
			'''<affiliation>
				<orgName type="laboratory">lab</orgName>
				<orgName type="department">dep</orgName>
				<orgName type="institution">institE</orgName>
				<address>
					<addrLine>addrLine</addrLine>
					<country key="AQ">Irrelevant</country>
					<postCode>postCode</postCode>
					<region>region</region>
					<settlement>settlement</settlement>
				</address>
			</affiliation>'''
		)
		expected = {
			'institution': 'institE',
			'department': 'dep',
			'laboratory': 'lab',
			'alpha2': 'AQ',
			'country': 'Antarctica',
			'settlement': 'settlement',
			'region': 'region',
			'postCode': 'postCode',
		}
		self.assertEqual(parser.grobid(__name__), expected)
	
	def test_multiple_institutions(self):
		self.server.setResponse(
			__name__,
			'''<affiliation>
				<orgName type="laboratory" key="lab1">lab1</orgName>
				<orgName type="laboratory" key="lab2">lab2</orgName>
				<orgName type="laboratory" key="lab3">lab3</orgName>
				<orgName type="department" key="dep1">dep1</orgName>
				<orgName type="department" key="dep2">dep2</orgName>
				<orgName type="department" key="dep3">dep3</orgName>
				<orgName type="institution" key="instit1">instit1</orgName>
				<orgName type="institution" key="instit2">instit2</orgName>
				<orgName type="institution" key="instit3">instit3</orgName>
				<address>
					<addrLine>addrLine1</addrLine>
					<addrLine>addrLine2</addrLine>
					<addrLine>addrLine3</addrLine>
					<country key="AQ">Irrelevant</country>
					<postCode>postCode</postCode>
					<region>region</region>
					<settlement>settlement</settlement>
				</address>
			</affiliation>'''
		)
		expected = {
			'institution': 'instit1',
			'institution2': 'instit2',
			'institution3': 'instit3',
			'department': 'dep1',
			'department2': 'dep2',
			'department3': 'dep3',
			'laboratory': 'lab1',
			'laboratory2': 'lab2',
			'laboratory3': 'lab3',
			'alpha2': 'AQ',
			'country': 'Antarctica',
			'settlement': 'settlement',
			'region': 'region',
			'postCode': 'postCode',
		}
		self.assertEqual(parser.grobid(__name__), expected)
	
	def test_invalid_xml(self):
		self.server.setResponse(__name__, '<broken tag>')
		expected = {
			'institution': None,
			'alpha2': None,
			'country': None,
			'settlement': None,
			'region': None,
			'postCode': None,
		}
		self.assertEqual(parser.grobid(__name__), expected)
