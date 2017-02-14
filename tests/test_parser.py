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
import xml.etree.ElementTree as et

class test_parser(unittest.TestCase):
	
	def setUp(self):
		host = 'localhost'
		port = 8081
		self.url = 'http://' + host + ':' + str(port)
		self.server = GrobidServer(host, port)
		self.server.start()
	
	def tearDown(self):
		self.server.stop()
	
	def test_parse_None(self):
		actual = list(parser.parseAll(None, self.url))
		expected = []
		self.assertEqual(actual, expected)
	
	def test_parse_empty(self):
		self.server.setResponse(__name__, '')
		actual = list(parser.parseAll(__name__, self.url))
		expected = []
		self.assertEqual(actual, expected)
	
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
		actual = list(parser.parseAll(__name__, self.url))
		expected = []
		self.assertEqual(actual, expected)
	
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
		actual = list(parser.parseAll(__name__, self.url))
		expected = [{
			'institution': 'institA',
			'institutionSource': 'grobid',
			'settlement': ['settlement',],
		},]
		self.assertEqual(actual, expected)
	
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
		actual = list(parser.parseAll(__name__, self.url))
		expected = [{
			'institution': 'institB',
			'institutionSource': 'grobid',
			'settlement': ['settlement',],
		},]
		self.assertEqual(actual, expected)
	
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
		actual = list(parser.parseAll(__name__, self.url))
		expected = [{
			'institution': 'institC',
			'institutionSource': 'grobid',
			'alpha2': 'AQ',
			'country': 'Antarctica',
			'countrySource': 'grobid',
			'settlement':[],
		},]
		self.assertEqual(actual, expected)
	
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
		actual = list(parser.parseAll(affiliation, self.url))
		expected = [{
			'institution': 'institA',
			'institutionSource': 'regexReplace',
			'alpha2': 'IN',
			'country': 'India',
			'countrySource': 'extract',
			'settlement': ['settlement',],
		},]
		self.assertEqual(actual, expected)
	
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
		actual = list(parser.parseAll(affiliation, self.url))
		expected = [{
			'institution': 'institA',
			'institutionSource': 'regexReplace',
			'settlement': ['settlement',],
		},]
		self.assertEqual(actual, expected)
	
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
		actual = list(parser.parseAll(affiliation, self.url))
		expected = [{
			'institution': 'institA',
			'institutionSource': 'grobid',
			'alpha2': 'DZ',
			'country': 'Algeria',
			'countrySource': 'extract',
			'settlement': ['settlement',],
		},]
		self.assertEqual(actual, expected)
	
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
		actual = list(parser.parseAll(affiliation, self.url))
		expected = [{
			'institution': 'institA',
			'institutionSource': 'grobid',
			'alpha2': 'IN',
			'country': 'India',
			'countrySource': 'extract',
			'settlement': ['settlement',],
		},]
		self.assertEqual(actual, expected)
	
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
		actual = list(parser.parseAll(__name__, self.url))
		expected = [{
			'institution': 'institD',
			'institutionSource': 'grobid',
			'alpha2': 'AQ',
			'country': 'Antarctica',
			'countrySource': 'grobid',
			'settlement': ['settlement',],
		},]
		self.assertEqual(actual, expected)
	
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
		actual = list(parser.parseAll(__name__, self.url))
		expected = [{
			'institution': 'institE',
			'institutionSource': 'grobid',
			'department': 'dep',
			'laboratory': 'lab',
			'alpha2': 'AQ',
			'country': 'Antarctica',
			'countrySource': 'grobid',
			'settlement': ['settlement',],
			'region': 'region',
			'postCode': 'postCode',
		},]
		self.assertEqual(actual, expected)
	
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
		actual = list(parser.parseAll(__name__, self.url))
		expected = [{
			'institution': 'instit1',
			'institutionSource': 'grobid',
			'department': 'dep1',
			'laboratory': 'lab1',
			'alpha2': 'AQ',
			'country': 'Antarctica',
			'countrySource': 'grobid',
			'settlement': ['settlement',],
			'region': 'region',
			'postCode': 'postCode',
		},{
			'institution': 'instit2',
			'institutionSource': 'grobid',
			'department': 'dep2',
			'laboratory': 'lab2',
			'alpha2': 'AQ',
			'country': 'Antarctica',
			'countrySource': 'grobid',
			'settlement': ['settlement',],
			'region': 'region',
			'postCode': 'postCode',
		},{
			'institution': 'instit3',
			'institutionSource': 'grobid',
			'department': 'dep3',
			'laboratory': 'lab3',
			'alpha2': 'AQ',
			'country': 'Antarctica',
			'countrySource': 'grobid',
			'settlement': ['settlement',],
			'region': 'region',
			'postCode': 'postCode',
		},]
		self.assertEqual(actual, expected)
	
	def test_parse_multiple_institutions_first_missing(self):
		affiliation = 'first instit,'
		self.server.setResponse(
			affiliation,
			'''<affiliation>
				<orgName type="laboratory" key="lab1">lab1</orgName>
				<orgName type="laboratory" key="lab2">lab2</orgName>
				<orgName type="department" key="dep1">dep1</orgName>
				<orgName type="department" key="dep2">dep2</orgName>
				<orgName type="institution" key="instit2">instit2</orgName>
			</affiliation>'''
		)
		actual = list(parser.parseAll(affiliation, self.url))
		expected = [{
			'institution': 'first instit',
			'institutionSource': 'regexInsert',
			'settlement': ['first instit'],
		},{
			'institutionSource': 'grobid',
			'department': 'dep1',
			'laboratory': 'lab1',
			'settlement': ['first instit'],
		},{
			'institution': 'instit2',
			'institutionSource': 'grobid',
			'department': 'dep2',
			'laboratory': 'lab2',
			'settlement': ['first instit'],
		},]
		self.assertEqual(actual, expected)
	
	def test_parse_institution_partially_recognised(self):
		affiliation = 'first instit,'
		self.server.setResponse(
			affiliation,
			'''<affiliation>
				<orgName type="laboratory" key="lab1">lab1</orgName>
				<orgName type="department" key="dep1">dep1</orgName>
				<orgName type="institution" key="instit1">first</orgName>
			</affiliation>'''
		)
		actual = list(parser.parseAll(affiliation, self.url))
		expected = [{
			'institution': 'first instit',
			'institutionSource': 'regexReplace',
			'department': 'dep1',
			'laboratory': 'lab1',
			'settlement': ['first instit'],
		},]
		self.assertEqual(actual, expected)
	
	def test_parse_institution_name_with_comma(self):
		affiliation = 'comma, inst'
		self.server.setResponse(
			affiliation,
			'''<affiliation>
				<orgName type="laboratory" key="lab1">lab1</orgName>
				<orgName type="department" key="dep1">dep1</orgName>
				<orgName type="institution" key="instit1">comma, inst</orgName>
			</affiliation>'''
		)
		actual = list(parser.parseAll(affiliation, self.url))
		expected = [{
			'institution': 'comma, inst',
			'institutionSource': 'grobid',
			'department': 'dep1',
			'laboratory': 'lab1',
			'settlement': ['comma'],
		},{
			'institution': 'comma',
			'institutionSource': 'regexInsertAfter',
			'settlement': ['comma'],
		},]
		self.assertEqual(actual, expected)
	
	def test_parse_invalid_xml(self):
		self.server.setResponse(__name__, '<broken tag>')
		actual = list(parser.parseAll(__name__, self.url))
		expected = []
		self.assertEqual(actual, expected)
	
	def test_parseAddress_Guinea(self):
		actual = parser.parseAddress('guinea', et.Element(None))
		expected = {
			'alpha2': 'GN',
			'country': 'Guinea',
			'countrySource': 'extract',
		}
		self.assertEqual(actual, expected)
	
	def test_parseAddress_Papua_New_Guinea(self):
		actual = parser.parseAddress('papua new guinea', et.Element(None))
		expected = {
			'alpha2': 'PG',
			'country': 'Papua New Guinea',
			'countrySource': 'extract',
		}
		self.assertEqual(actual, expected)
	
	def test_parseAddress_None(self):
		actual = parser.parseAddress('there is no country in this string', et.Element(None))
		expected = {}
		self.assertEqual(actual, expected)
	
	def test_parseAddress_empty(self):
		actual = parser.parseAddress('', et.Element(None))
		expected = {}
		self.assertEqual(actual, expected)
	
	def test_parseAddress_multiple_countries(self):
		actual = parser.parseAddress('Serbia Montenegro', et.Element(None))
		expected = {
			'alpha2': 'ME',
			'country': 'Montenegro',
			'countrySource': 'extract',
		}
		self.assertEqual(actual, expected)
	
	def test_parseAddress_Hong_Kong_in_China(self):
		actual = parser.parseAddress('Hong Kong, China', et.Element(None))
		expected = {
			'alpha2': 'HK',
			'country': 'Hong Kong',
			'countrySource': 'extract',
		}
		self.assertEqual(actual, expected)
	
	def test_parseAddress_Macao_in_China(self):
		actual = parser.parseAddress('Macao, PR China', et.Element(None))
		expected = {
			'alpha2': 'MO',
			'country': 'Macao',
			'countrySource': 'extract',
		}
		self.assertEqual(actual, expected)
	
	def test_countryList_successors_name_are_not_part_of_predecessors(self):
		length = len(parser.countryList)
		for i in range(length):
			for j in range(i + 1, length):
				predeccesor = parser.countryList[i][1]
				successor = parser.countryList[j][1]
				self.assertNotIn(predeccesor, successor)
	
	def test_parseOrganisations_regex_None_Element_args(self):
		actual = parser.parseOrganisations(None, et.Element(None))
		expected = []
		self.assertEqual(actual, expected)
	
	def test_parseOrganisations_regex_empty_list(self):
		affiliation = 'first words, second part, third word list'
		root = et.Element(None)
		actual = parser.parseOrganisations(affiliation, root)
		expected = [{
			'institution': 'first words',
			'institutionSource': 'regexInsert',
		},]
		self.assertEqual(actual, expected)
	
	def test_parseOrganisations_regex_comma_before_words(self):
		affiliation = ',comma before any words'
		root = et.Element(None)
		actual = parser.parseOrganisations(affiliation, root)
		expected = []
		self.assertEqual(actual, expected)
	
	def test_parseOrganisations_regex_identical(self):
		affiliation = 'first words, second part, third word list'
		root = et.fromstring('''
			<results>
				<affiliation>
					<orgName type="institution">first words</orgName>
				</affiliation>
			</results>
		''')
		actual = parser.parseOrganisations(affiliation, root)
		expected = [{
			'institution': 'first words',
			'institutionSource': 'regexReplace',
		},]
		self.assertEqual(actual, expected)
	
	def test_parseOrganisations_regex_left_part(self):
		affiliation = 'first words, second part, third word list'
		root = et.fromstring('''
			<results>
				<affiliation>
					<orgName type="institution">fir</orgName>
				</affiliation>
			</results>
		''')
		actual = parser.parseOrganisations(affiliation, root)
		expected = [{
			'institution': 'first words',
			'institutionSource': 'regexReplace',
		},]
		self.assertEqual(actual, expected)
	
	def test_parseOrganisations_regex_middle_part(self):
		affiliation = 'first words, second part, third word list'
		root = et.fromstring('''
			<results>
				<affiliation>
					<orgName type="institution">st word</orgName>
				</affiliation>
			</results>
		''')
		actual = parser.parseOrganisations(affiliation, root)
		expected = [{
			'institution': 'first words',
			'institutionSource': 'regexReplace',
		},]
		self.assertEqual(actual, expected)
	
	def test_parseOrganisations_regex_right_part(self):
		affiliation = 'first words, second part, third word list'
		root = et.fromstring('''
			<results>
				<affiliation>
					<orgName type="institution">words</orgName>
				</affiliation>
			</results>
		''')
		actual = parser.parseOrganisations(affiliation, root)
		expected = [{
			'institution': 'first words',
			'institutionSource': 'regexReplace',
		},]
		self.assertEqual(actual, expected)
	
	def test_parseOrganisations_regex_more_on_the_right(self):
		affiliation = 'first words, second part, ...'
		root = et.fromstring('''
			<results>
				<affiliation>
					<orgName type="institution">first words, seco</orgName>
				</affiliation>
			</results>
		''')
		actual = parser.parseOrganisations(affiliation, root)
		expected = [{
			'institution': 'first words, seco',
			'institutionSource': 'grobid',
		},{
			'institution': 'first words',
			'institutionSource': 'regexInsertAfter',
		},]
		self.assertEqual(actual, expected)
	
	def test_parseOrganisations_regex_overlap_on_the_right(self):
		affiliation = 'first words, second part, third word list'
		root = et.fromstring('''
			<results>
				<affiliation>
					<orgName type="institution">words, second</orgName>
				</affiliation>
			</results>
		''')
		actual = parser.parseOrganisations(affiliation, root)
		expected = [{
			'institution': 'first words',
			'institutionSource': 'regexInsertBefore',
		},{
			'institution': 'words, second',
			'institutionSource': 'grobid',
		},]
		self.assertEqual(actual, expected)
	
	def test_parseOrganisations_regex_no_overlap(self):
		affiliation = 'first words, second part, third word list'
		root = et.fromstring('''
			<results>
				<affiliation>
					<orgName type="institution">third word</orgName>
				</affiliation>
			</results>
		''')
		actual = parser.parseOrganisations(affiliation, root)
		expected = [{
			'institution': 'first words',
			'institutionSource': 'regexInsertBefore',
		},{
			'institution': 'third word',
			'institutionSource': 'grobid',
		},]
		self.assertEqual(actual, expected)
	
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
	
	def test_parseSettlement_None(self):
		actual = parser.parseSettlement(None, et.Element(None))
		expected = {'settlement':[],}
		self.assertEqual(actual, expected)
	
	def test_parseSettlement_empty(self):
		actual = parser.parseSettlement('', et.Element(None))
		expected = {'settlement':[],}
		self.assertEqual(actual, expected)
		
	def test_parseSettlement_empty_but_node(self):
		actual = parser.parseSettlement('', et.fromstring('''
				<results>
					<affiliation>
						<address>
							<settlement>settlement</settlement>
						</address>
					</affiliation>
				</results>
			''')
		)
		expected = {'settlement':['settlement',],}
		self.assertEqual(actual, expected)
	
	def test_parseSettlement_no_comma(self):
		actual = parser.parseSettlement('teststring', et.Element(None))
		expected = {'settlement':[],}
		self.assertEqual(actual, expected)
	
	def test_parseSettlement_one_comma(self):
		actual = parser.parseSettlement('before comma, after comma', et.Element(None))
		expected = {'settlement':['before comma',],}
		self.assertEqual(actual, expected)
	
	def test_parseSettlement_two_comma(self):
		actual = parser.parseSettlement('one, two, three', et.Element(None))
		expected = {'settlement':['one','two',],}
		self.assertEqual(actual, expected)
	
	def test_parseSettlement_contain_number(self):
		actual = parser.parseSettlement(
			'3 A-2 one 1 , 343-C two 4 , three',
			et.Element(None)
		)
		expected = {'settlement':['one','two',],}
		self.assertEqual(actual, expected)
	
	def test_parseSettlement_capitals(self):
		actual = parser.parseSettlement(
			'A BB CCC dD Dd test b Test worD WOrd woRd, Country',
			et.Element(None)
		)
		expected = {'settlement':['A Dd test b Test',],}
		self.assertEqual(actual, expected)
	
	def test_parseSettlement_contain_number_and_node(self):
		actual = parser.parseSettlement(
			'3 A-2 one 1 , 343-C two 4 , three',
			et.fromstring('''
				<results>
					<affiliation>
						<address>
							<settlement>settlement</settlement>
						</address>
					</affiliation>
				</results>
			''')
		)
		expected = {'settlement':['one','two','settlement'],}
		self.assertEqual(actual, expected)

