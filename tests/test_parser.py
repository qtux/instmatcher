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
		self.url = 'http://' + host + ':' + str(port)
		parser.init(self.url)
		self.server = GrobidServer(host, port)
		self.server.start()
	
	def tearDown(self):
		self.server.stop()
	
	def test_parse_None(self):
		expected = {
			'institution': [],
			'alpha2': None,
			'settlement': None,
		}
		self.assertEqual(parser.parse(None), expected)
	
	def test_parse_empty(self):
		self.server.setResponse(__name__, '')
		expected = {
			'institution': [],
			'alpha2': None,
			'settlement': None,
		}
		self.assertEqual(parser.parse(__name__), expected)
	
	def test_parse_no_institution(self):
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
			'institution': [],
			'alpha2': 'AQ',
			'country': 'Antarctica',
			'countrySource': 'grobid',
			'settlement': 'settlement',
		}
		self.assertEqual(parser.parse(__name__), expected)
	
	def test_parse_no_alpha2(self):
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
			'institution': ['institA',],
			'alpha2': None,
			'settlement': 'settlement',
		}
		self.assertEqual(parser.parse(__name__), expected)
	
	def test_parse_no_country(self):
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
			'institution': ['institB',],
			'alpha2': None,
			'settlement': 'settlement',
		}
		self.assertEqual(parser.parse(__name__), expected)
	
	def test_parse_no_settlement(self):
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
			'institution': ['institC',],
			'alpha2': 'AQ',
			'country': 'Antarctica',
			'countrySource': 'grobid',
			'settlement': None,
		}
		self.assertEqual(parser.parse(__name__), expected)
	
	def test_parse_not_regocnised_country(self):
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
			'institution': ['institA',],
			'alpha2': 'IN',
			'country': 'India',
			'countrySource': 'extract',
			'settlement': 'settlement',
		}
		self.assertEqual(parser.parse(affiliation), expected)
	
	def test_parse_not_regocnised_bad_country(self):
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
			'institution': ['institA',],
			'alpha2': None,
			'settlement': 'settlement',
		}
		self.assertEqual(parser.parse(affiliation), expected)
	
	def test_parse_not_recognised_country_no_comma_in_affiliation_string(self):
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
			'institution': ['institA',],
			'alpha2': 'DZ',
			'country': 'Algeria',
			'countrySource': 'extract',
			'settlement': 'settlement',
		}
		self.assertEqual(parser.parse(affiliation), expected)
	
	def test_parse_multiple_not_recognised_countries(self):
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
			'institution': ['institA',],
			'alpha2': 'IN',
			'country': 'India',
			'countrySource': 'extract',
			'settlement': 'settlement',
		}
		self.assertEqual(parser.parse(affiliation), expected)
	
	def test_parse_releveant_tags(self):
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
			'institution': ['institD',],
			'alpha2': 'AQ',
			'country': 'Antarctica',
			'countrySource': 'grobid',
			'settlement': 'settlement',
		}
		self.assertEqual(parser.parse(__name__), expected)
	
	def test_parse_every_tags(self):
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
			'institution': ['institE',],
			'department': ['dep',],
			'laboratory': ['lab',],
			'alpha2': 'AQ',
			'country': 'Antarctica',
			'countrySource': 'grobid',
			'settlement': 'settlement',
			'region': 'region',
			'postCode': 'postCode',
		}
		self.assertEqual(parser.parse(__name__), expected)
	
	def test_parse_multiple_institutions(self):
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
			'institution': ['instit1', 'instit2', 'instit3',],
			'department': ['dep1', 'dep2', 'dep3',],
			'laboratory': ['lab1', 'lab2', 'lab3',],
			'alpha2': 'AQ',
			'country': 'Antarctica',
			'countrySource': 'grobid',
			'settlement': 'settlement',
			'region': 'region',
			'postCode': 'postCode',
		}
		self.assertEqual(parser.parse(__name__), expected)
	
	def test_parse_invalid_xml(self):
		self.server.setResponse(__name__, '<broken tag>')
		expected = {
			'institution': [],
			'alpha2': None,
			'settlement': None,
		}
		self.assertEqual(parser.parse(__name__), expected)
	
	def test_extractCountry_Guinea(self):
		actual = parser.extractCountry('guinea')
		expected = {
			'alpha2': 'GN',
			'country': 'Guinea',
			'countrySource': 'extract',
		}
		self.assertEqual(actual, expected)
	
	def test_extractCountry_Papua_New_Guinea(self):
		actual = parser.extractCountry('papua new guinea')
		expected = {
			'alpha2': 'PG',
			'country': 'Papua New Guinea',
			'countrySource': 'extract',
		}
		self.assertEqual(actual, expected)
	
	def test_extractCountry_None(self):
		actual = parser.extractCountry('there is no country in this string')
		expected = {}
		self.assertEqual(actual, expected)
	
	def test_extractCountry_empty(self):
		actual = parser.extractCountry('')
		expected = {}
		self.assertEqual(actual, expected)
	
	def test_extractCountry_multiple_countries(self):
		actual = parser.extractCountry('Serbia Montenegro')
		expected = {
			'alpha2': 'ME',
			'country': 'Montenegro',
			'countrySource': 'extract',
		}
		self.assertEqual(actual, expected)
	
	def test_extractCountry_successors_name_are_not_part_of_predecessors(self):
		length = len(parser.countryList)
		for i in range(length):
			for j in range(i + 1, length):
				predeccesor = parser.countryList[i][1]
				successor = parser.countryList[j][1]
				self.assertNotIn(predeccesor, successor)
	
	def test_improveInstitutions_empty_args(self):
		args = ([], None)
		parser.improveInstitutions(*args)
		expected = []
		self.assertEqual(args[0], expected)
	
	def test_improveInstitutions_empty_list(self):
		args = ([], 'first words, second part, third word list')
		parser.improveInstitutions(*args)
		expected = ['first words',]
		self.assertEqual(args[0], expected)
	
	def test_improveInstitutions_comma_before_words(self):
		args = ([], ',comma before any words')
		parser.improveInstitutions(*args)
		expected = []
		self.assertEqual(args[0], expected)
	
	def test_improveInstitutions_identical(self):
		args = (['first words',], 'first words, second part, third word list')
		parser.improveInstitutions(*args)
		expected = ['first words',]
		self.assertEqual(args[0], expected)
	
	def test_improveInstitutions_left_part(self):
		args = (['fir',], 'first words, second part, third word list')
		parser.improveInstitutions(*args)
		expected = ['first words',]
		self.assertEqual(args[0], expected)
	
	def test_improveInstitutions_middle_part(self):
		args = (['st word',], 'first words, second part, third word list')
		parser.improveInstitutions(*args)
		expected = ['first words',]
		self.assertEqual(args[0], expected)
	
	def test_improveInstitutions_right_part(self):
		args = (['words',], 'first words, second part, third word list')
		parser.improveInstitutions(*args)
		expected = ['first words',]
		self.assertEqual(args[0], expected)
	
	def test_improveInstitutions_more_on_the_right(self):
		args = (['first words, second part',], 'first words, second part, ...')
		parser.improveInstitutions(*args)
		expected = ['first words, second part', 'first words',]
		self.assertEqual(args[0], expected)
	
	def test_improveInstitutions_overlap_on_the_right(self):
		args = (['words, second',], 'first words, second part, third word list')
		parser.improveInstitutions(*args)
		expected = ['first words', 'words, second',]
		self.assertEqual(args[0], expected)
	
	def test_improveInstitutions_no_overlap(self):
		args = (['third word',],  'first words, second part, third word list')
		parser.improveInstitutions(*args)
		expected = ['first words', 'third word',]
		self.assertEqual(args[0], expected)
	
	def test_queryGrobid_None(self):
		actual = parser.queryGrobid(None, self.url)
		expected = '<results></results>'
		self.assertEqual(actual, expected)
	
	def test_queryGrobid_invalid_type(self):
		actual = parser.queryGrobid([1,2,3,], self.url)
		expected = '<results></results>'
		self.assertEqual(actual, expected)
	
	def test_queryGrobid_empty_string(self):
		actual = parser.queryGrobid('', self.url)
		expected = '<results></results>'
		self.assertEqual(actual, expected)
	
	def test_queryGrobid_valid_xml(self):
		self.server.setResponse('valid_output', '<affiliation/>')
		actual = parser.queryGrobid('valid_output', self.url)
		expected = '<results><affiliation/></results>'
		self.assertEqual(actual, expected)
	
	def test_queryGrobid_invalid_xml(self):
		self.server.setResponse('invalid_output', '>invalid<')
		actual = parser.queryGrobid('invalid_output', self.url)
		expected = '<results>>invalid<</results>'
		self.assertEqual(actual, expected)
