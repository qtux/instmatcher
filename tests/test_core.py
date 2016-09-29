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
	
	def assertNames(self, actual, expectedNames):
		scores, actualNames = [], []
		for item in actual:
			scores.append(item[1])
			actualNames.append(item[0]['name'])
		if len(scores) > len(set(scores)):
			self.assertCountEqual(actualNames, expectedNames)
		else:
			self.assertSequenceEqual(actualNames, expectedNames)
	
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
		expected = []
		self.assertNames(actual, expected)
	
	def test_zero_search_radius(self):
		actual = core.query('Geneva', None, 0, 0, 0)
		expected = [
			"University of Geneva",
			"International University in Geneva",
			"University of Edinburgh",
			"European Organization for Nuclear Research",
		]
		self.assertNames(actual, expected)
	
	def test_bad_coord_param(self):
		actual = core.query('Pisa', None, None, float('inf'), 1)
		expected = [
			"University of Pisa",
			"Scuola Normale Superiore",
		]
		self.assertNames(actual, expected)
	
	def test_illegal_coord_param(self):
		actual = core.query('Geneva', None, '120', {'lon':0}, 1)
		expected = [
			"University of Geneva",
			"International University in Geneva",
			"University of Edinburgh",
			"European Organization for Nuclear Research",
		]
		self.assertNames(actual, expected)
	
	def test_impossible_coord_param(self):
		actual = core.query('Lisbon', None, 1000, 2000, 1)
		expected = [
			"University of Lisbon",
			"Technical University of Lisbon",
			"ISCTE – Lisbon University Institute",
		]
		self.assertNames(actual, expected)
	
	def test_TU_Berlin(self):
		actual = core.query('TU Berlin', None, None, None, 1)
		expected = ["Technical University of Berlin",]
		self.assertNames(actual, expected)
	
	def test_Berlin(self):
		actual = core.query('Berlin', None, None, None, 1)
		expected = [
			"Free University of Berlin",
			"Technical University of Berlin",
			"Social Science Research Center Berlin",
			"Humboldt University of Berlin",
			"Charité",
			"Bethanien (Berlin)",
			"VLB Berlin",
			"Institute for Advanced Study",
			"American Academy in Berlin",
			"Helmholtz-Zentrum Berlin",
			"Zuse Institute Berlin",
			"SRH Hochschule Berlin",
			"Centre for Historical Research in Berlin",
			"Ferdinand-Braun-Institut",
			"Children's follow-up Clinic (Kindernachsorgeklinik) Berlin-Brandenburg",
		]
		self.assertNames(actual, expected)
	
	def test_FU_Berlin(self):
		actual = core.query('FU Berlin', None, None, None, 1)
		expected = ["Free University of Berlin",]
		self.assertNames(actual, expected)
	
	def test_Boston_no_coords(self):
		actual = core.query('Boston', None, None, None, 1)
		expected = [
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
		self.assertNames(actual, expected)
	
	def test_Boston_USA(self):
		actual = core.query('Boston', None, 42.358056, -71.063611, 1)
		expected = [
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
		self.assertNames(actual, expected)
	
	def test_Boston_Philippines(self):
		actual = core.query('Boston', None, 7.8689, 126.3734, 1)
		expected = [
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
		self.assertNames(actual, expected)
	
	def test_Boston_UK(self):
		actual = core.query('Boston', None, 52.974, -0.0214, 1)
		expected = [
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
		self.assertNames(actual, expected)
	
	def test_London(self):
		actual = core.query('London', None, None, None, 1)
		expected = [
			"University of London",
			"University of the Arts London",
			"City, University of London",
			"London Metropolitan University",
			"University of East London",
			"King's College London",
			"University of North London",
			"London School of Hygiene & Tropical Medicine",
			"London School of Economics",
			"Queen Mary, University of London",
			"Royal Holloway, University of London",
			"Imperial College London",
			"University of London Institute in Paris",
			"University of West London",
			"London Guildhall University",
			"Birkbeck, University of London",
			"Diplomatic Academy of London",
			"Goldsmiths, University of London",
			"SOAS, University of London",
			"London School of Theology",
			"Brunel University London",
			"London South Bank University",
			"University of London International Programmes",
			"Richmond, The American International University in London",
			"University of East London School of Law and Social Sciences",
			"Centre for History in Public Health, London School of Hygiene and Tropical Medicine",
			"University of Western Ontario",
			"University College Hospital",
			"London Centre for Nanotechnology",
			"London Research Institute",
			"London Chest Hospital",
			"London Lock Hospital",
			"Royal London Hospital",
			"London Bridge Hospital",
			"Wellington Hospital, London",
			"St. Mary's Hospital",
			"London Road Community Hospital",
			"St. Anthony's Hospital, London",
			"King George Hospital, London",
			"Royal London Hospital for Integrated Medicine",
		]
		self.assertNames(actual, expected)
	
	def test_London_CA(self):
		actual = core.query('London', 'CA', None, None, 1)
		expected = ["University of Western Ontario",]
		self.assertNames(actual, expected)
	
	def test_abbreviation_expansion_considering_word_boundaries(self):
		actual = core.expandAbbreviations('univ Univ univuniv univx xuniv UNIV')
		expected = 'university university univuniv univx xuniv university'
		self.assertEqual(actual, expected)
	
	def test_some_abbreviations(self):
		actual = core.expandAbbreviations('chem ACAD of sCI, INST of EngN.')
		expected = 'chemical academy of science, institute of engineering.'
		self.assertEqual(actual, expected)
	
	def test_abbreviations_no_hits(self):
		actual = core.expandAbbreviations('UNIV_univ chemacad')
		expected = 'UNIV_univ chemacad'
		self.assertEqual(actual, expected)
