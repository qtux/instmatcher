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
from instmatcher import core
import itertools

class test_core(unittest.TestCase):
	
	def test_None_combinations(self):
		combinations = [
			['Fantasia', None],
			['AQ', None],
			[30, None],
			[40, None],
			[1, None],
		]
		expected = []
		for arg in itertools.product(*combinations):
			actual = list(core.query(*arg))
			self.assertSequenceEqual(actual, expected)
	
	def test_misspelled(self):
		actual = core.query('Whasington', None, None, None, 1)
		expectedNames = []
		actualNames = [item[0]['name'] for item in actual]
		self.assertSequenceEqual(actualNames, expectedNames)
	
	def test_zero_search_radius(self):
		actual = core.query('Geneva', None, 0, 0, 0)
		expectedNames = [
			"University of Geneva",
			"International University in Geneva",
			"University of Edinburgh",
			"CERN",
		]
		actualNames = [item[0]['name'] for item in actual]
		self.assertSequenceEqual(actualNames, expectedNames)
	
	def test_bad_coord_param(self):
		actual = core.query('Pisa', None, None, float('inf'), 1)
		expectedNames = [
			"University of Pisa",
			"Scuola Normale Superiore",
		]
		actualNames = [item[0]['name'] for item in actual]
		self.assertSequenceEqual(actualNames, expectedNames)
	
	def test_illegal_coord_param(self):
		actual = core.query('Geneva', None, '120', {'lon':0}, 1)
		expectedNames = [
			"University of Geneva",
			"International University in Geneva",
			"University of Edinburgh",
			"CERN",
		]
		actualNames = [item[0]['name'] for item in actual]
		self.assertSequenceEqual(actualNames, expectedNames)
	
	def test_impossible_coord_param(self):
		actual = core.query('Lisbon', None, 1000, 2000, 1)
		expectedNames = [
			"University of Lisbon",
			"Technical University of Lisbon",
			"ISCTE – Lisbon University Institute",
		]
		actualNames = [item[0]['name'] for item in actual]
		self.assertSequenceEqual(actualNames, expectedNames)
	
	def test_TU_Berlin(self):
		actual = core.query('TU Berlin', None, None, None, 1)
		expectedNames = ["Technical University of Berlin",]
		actualNames = [item[0]['name'] for item in actual]
		self.assertSequenceEqual(actualNames, expectedNames)
	
	def test_TU_Berlin_full(self):
		actual = core.query('TU Berlin', None, None, None, 1)
		expectedNames = ["Technical University of Berlin",]
		actualNames = [item[0]['name'] for item in actual]
		self.assertSequenceEqual(actualNames, expectedNames)
	
	def test_TU_Berlin(self):
		actual = core.query('TU Berlin', None, None, None, 1)
		expected = [{
			'alpha2': 'DE',
			'country': 'Germany',
			'isni': '0000 0001 2195 9817',
			'lat': 52.511944444444,
			'lon': 13.326388888889,
			'name': 'Technical University of Berlin',
			'source': 'http://www.wikidata.org/entity/Q51985',
			'type': 'university',
		},]
		actualResults = [item[0] for item in actual]
		self.assertSequenceEqual(actualResults, expected)
	
	def test_Boston_no_coords(self):
		actual = core.query('Boston', None, None, None, 1)
		expectedNames = [
			"Boston University",
			"University of Massachusetts Boston",
			"Boston Children's Hospital",
			"New England School of Law",
			"Northeastern University",
			"Boston College",
			"Boston Psychopathic Hospital",
			"Boston Regional Medical Center",
			"Boston College Law School",
		]
		actualNames = [item[0]['name'] for item in actual]
		try:
			self.assertSequenceEqual(actualNames, expectedNames)
		except AssertionError:
			self.assertCountEqual(actualNames, expectedNames)
	
	def test_Boston_USA(self):
		actual = core.query('Boston', None, 42.358056, -71.063611, 1)
		expectedNames = [
			"Boston University",
			"University of Massachusetts Boston",
			"Boston Children's Hospital",
			"New England School of Law",
			"Northeastern University",
			"Boston College",
			"Boston Psychopathic Hospital",
			"Boston Regional Medical Center",
			"Boston College Law School",
		]
		actualNames = [item[0]['name'] for item in actual]
		try:
			self.assertSequenceEqual(actualNames, expectedNames)
		except AssertionError:
			self.assertCountEqual(actualNames, expectedNames)
	
	def test_Boston_Philippines(self):
		actual = core.query('Boston', None, 7.8689, 126.3734, 1)
		expectedNames = [
			"Boston University",
			"University of Massachusetts Boston",
			"Boston Children's Hospital",
			"New England School of Law",
			"Northeastern University",
			"Boston College",
			"Boston Psychopathic Hospital",
			"Boston Regional Medical Center",
			"Boston College Law School",
		]
		actualNames = [item[0]['name'] for item in actual]
		try:
			self.assertSequenceEqual(actualNames, expectedNames)
		except AssertionError:
			self.assertCountEqual(actualNames, expectedNames)
	
	def test_Boston_UK(self):
		actual = core.query('Boston', None, 52.974, -0.0214, 1)
		expectedNames = [
			"Boston University",
			"University of Massachusetts Boston",
			"Boston Children's Hospital",
			"New England School of Law",
			"Northeastern University",
			"Boston College",
			"Boston Psychopathic Hospital",
			"Boston Regional Medical Center",
			"Boston College Law School",
		]
		actualNames = [item[0]['name'] for item in actual]
		try:
			self.assertSequenceEqual(actualNames, expectedNames)
		except AssertionError:
			self.assertCountEqual(actualNames, expectedNames)
	
	def test_London_CA(self):
		actual = core.query('London', 'CA', None, None, 1)
		expectedNames = ["University of Western Ontario",]
		actualNames = [item[0]['name'] for item in actual]
		self.assertSequenceEqual(actualNames, expectedNames)
	
	def test_abbreviation_expansion_considering_word_boundaries(self):
		actual = core.expandAbbreviations('univ Univ univuniv univx xuniv UNIV')
		expected = 'univ* univ* univuniv univx xuniv univ*'
		self.assertEqual(actual, expected)
	
	def test_some_abbreviations(self):
		actual = core.expandAbbreviations('chem ACAD of sCI, INST of EngN.')
		expected = 'chem* acad* of sci*, inst* of engineering.'
		self.assertEqual(actual, expected)
	
	def test_abbreviations_no_hits(self):
		actual = core.expandAbbreviations('UNIV_univ chemacad')
		expected = 'UNIV_univ chemacad'
		self.assertEqual(actual, expected)
	
	def test_find_TU_Berlin(self):
		arg = 'TU Berlin'
		expected = [
			{
				'name': 'Technical University of Berlin',
				'alpha2': 'DE',
				'country': 'Germany',
				'lat': 52.511944444444,
				'lon': 13.326388888889,
				'isni': '0000 0001 2195 9817',
				'source': 'http://www.wikidata.org/entity/Q51985',
				'type': 'university',
			}
		]
		first = expected[0]
		self.assertSequenceEqual(list(core.findAll(arg)), expected)
		self.assertEqual(core.find(arg), first)
	
	def test_find_Univ_Leuven(self):
		arg = 'Univ Leuven'
		expected = [
			{
				# dutch part of the former Catholic University of Leuven
				'name': 'Katholieke Universiteit Leuven Campus Kortrijk',
				'alpha2': 'BE',
				'country': 'Belgium',
				'lat': 50.806139,
				'lon': 3.291939,
				'isni': '',
				'source': 'http://www.wikidata.org/entity/Q1736308',
				'type': 'university',
			},{
				# Catholic University of Leuven (or Louvain), until 1986
				'name': 'Catholic University of Leuven',
				'alpha2': 'BE',
				'country': 'Belgium',
				'lat': 50.669722222222,
				'lon': 4.6122222222222,
				'isni': '',
				'source': 'http://www.wikidata.org/entity/Q5121415',
				'type': 'university',
			},
		]
		first = expected[0]
		self.assertSequenceEqual(list(core.findAll(arg)), expected)
		self.assertEqual(core.find(arg), first)
	
	def test_find_Univ_Louvain(self):
		arg = 'Univ Louvain'
		expected = [
			{
				# french part of the former Catholic University of Leuven
				'name': 'Université catholique de Louvain',
				'alpha2': 'BE',
				'country': 'Belgium',
				'lat': 50.669611111111,
				'lon': 4.6122638888889,
				'isni': '',
				'source': 'http://www.wikidata.org/entity/Q378134',
				'type': 'university',
			},{
				# Catholic University of Leuven (or Louvain), until 1986
				'name': 'Catholic University of Leuven',
				'alpha2': 'BE',
				'country': 'Belgium',
				'lat': 50.669722222222,
				'lon': 4.6122222222222,
				'isni': '',
				'source': 'http://www.wikidata.org/entity/Q5121415',
				'type': 'university',
			},
		]
		first = expected[0]
		self.assertSequenceEqual(list(core.findAll(arg)), expected)
		self.assertEqual(core.find(arg), first)
	
	def test_institution_uniqeness(self):
		visited = set()
		for item in core.findAll('*'):
			source = item['source']
			if source in visited:
				self.fail('The source column is not unique!')
				return
			else:
				visited.add(source)
