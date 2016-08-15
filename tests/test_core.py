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
import instmatcher.core as core

import os
import string
from pkg_resources import resource_filename
import csv
from itertools import zip_longest

default_boston = [
	("Boston University", 21.856071646733387),
	("University of Massachusetts Boston", 20.61416140861746),
	("New England School of Law", 11.309155130404424),
	("Northeastern University", 10.85321409560593),
	("Boston College", 9.509569030224858),
	("Boston College Law School", 7.312656243817379),
]
boston = {
	('Boston', None, 42.358056, -71.063611, 1): default_boston,
	('Boston', None, 7.8689, 126.3734, 1): default_boston,
	('Boston', None, 52.974, -0.0214, 1): default_boston,
	('Boston', None, None, None, 1): default_boston,
}

berlin = {
	('TU Berlin', None, None, None, 1): [
		("Technical University of Berlin", 17.772187737824495),
	],
	('Berlin', None, None, None, 1): [
		("Free University of Berlin", 21.277674188171165),
		("Technical University of Berlin", 20.111968757513647),
		("Humboldt University of Berlin", 19.27791467983046),
		("VLB Berlin", 9.29371957936834),
		("SRH Hochschule Berlin", 8.079998383474871),
	],
	('FU Berlin', None, None, None, 1): [
		("Free University of Berlin", 22.304592901557243),
	],
}

bad_param = {
	('Pisa', None, None, float('inf'), 1): [
		("University of Pisa", 24.950498759665194),
	],
	('Lisbon', None, 1000, 2000, 1): [
		("University of Lisbon", 9.773747407484867),
		("Technical University of Lisbon", 8.497336569986855),
		("ISCTE – Lisbon University Institute", 7.515803794859055),
	],
	('Whasington', None, None, None, 1): [
	],
	('Geneva', None, '120', 0, 1): [
		("University of Geneva", 13.012221790177914),
		("International University in Geneva", 8.793442725629246),
		("University of Edinburgh", 1.160123103124587),
	],
	('University Sofia', None, '9000', None, 1): [
		("Technical University of Sofia", 15.183401999021697),
		("Sophia University", 11.464829195103638),
		("University of Forestry, Sofia", 9.7781524771213),
		("Sofia Medical University", 9.7781524771213),
		("University of Architecture, Civil Engineering and Geodesy", 7.304763384472515),
		("University of National and World Economy", 4.637933156639801),
	],
}

none_perm = {
	('Fantasia', 'AQ', 30,   40,   1):    [],
	('Fantasia', 'AQ', 30,   40,   None): [],
	('Fantasia', 'AQ', 30,   None, 1):    [],
	('Fantasia', 'AQ', 30,   None, None): [],
	('Fantasia', 'AQ', None, 40,   1):    [],
	('Fantasia', 'AQ', None, 40,   None): [],
	('Fantasia', 'AQ', None, None, 1):    [],
	('Fantasia', 'AQ', None, None, None): [],
	('Fantasia', None, 30,   40,   1):    [],
	('Fantasia', None, 30,   40,   None): [],
	('Fantasia', None, 30,   None, 1):    [],
	('Fantasia', None, 30,   None, None): [],
	('Fantasia', None, None, 40,   1):    [],
	('Fantasia', None, None, 40,   None): [],
	('Fantasia', None, None, None, 1):    [],
	('Fantasia', None, None, None, None): [],
	(None,       'AQ', 30,   40,   1):    [],
	(None,       'AQ', 30,   40,   None): [],
	(None,       'AQ', 30,   None, 1):    [],
	(None,       'AQ', 30,   None, None): [],
	(None,       'AQ', None, 40,   1):    [],
	(None,       'AQ', None, 40,   None): [],
	(None,       'AQ', None, None, 1):    [],
	(None,       'AQ', None, None, None): [],
	(None,       None, 30,   40,   1):    [],
	(None,       None, 30,   40,   None): [],
	(None,       None, 30,   None, 1):    [],
	(None,       None, 30,   None, None): [],
	(None,       None, None, 40,   1):    [],
	(None,       None, None, 40,   None): [],
	(None,       None, None, None, 1):    [],
	(None,       None, None, None, None): [],
}

class test_core(unittest.TestCase):
	def setUp(self):
		core.init(procs=os.cpu_count(), multisegment=True, ixPath='./index')
	
	def run_query(self, tests):
		for args, targets in tests.items():
			institutes = core.query(*args)
			post_check = []
			for result, target in zip_longest(institutes, targets):
				# if the names do not match but the score does:
				# --> postpone checking of the current item
				if result[0]['name'] != target[0] and result[1] == target[1]:
					post_check.append((result[0]['name'], result[1]))
				else:
					self.assertEqual(result[0]['name'], target[0], msg=args)
			# check postponed items for beeing inside the target list,
			# note that the order of elements cannot be checked this way
			for item in post_check:
				self.assertTrue(item in targets, msg=args)
	
	def test_bad_param(self):
		self.run_query(bad_param)
	
	def test_none_perm(self):
		self.run_query(none_perm)
		
	def test_berlin(self):
		self.run_query(berlin)
		
	def test_boston(self):
		self.run_query(boston)
	
	def test_expandAbbreviations(self):
		source = resource_filename(core.__name__, 'data/abbreviations.csv')
		with open(source) as csvfile:
			reader = csv.reader(csvfile)
			for row in reader:
				separators = string.whitespace
				separators += string.punctuation.replace('_', '')
				for sep in separators:
					test = sep + row[0] + sep
					result = sep + row[1] + sep
					self.assertEqual(core.expandAbbreviations(test), result)
				links = string.ascii_letters + string.digits + '_'
				for link in links:
					test = link + row[0] + link
					self.assertEqual(core.expandAbbreviations(test), test)

if __name__ == '__main__':
	core.init(procs=os.cpu_count(), multisegment=True, ixPath='./index')
	dicts = {
		'boston': boston,
		'berlin': berlin,
		'bad_param': bad_param,
	}
	for name, item in dicts.items():
		print(name + ' = {')
		for args in item.keys():
			institutes = core.query(*args)
			print('\t', args,': [', sep='')
			for result in institutes:
				pair = '("' + result[0]['name'] + '", ' + str(result[1]) + ')'
				print('\t\t' + pair + ',')
			print('\t],')
		print('}')
