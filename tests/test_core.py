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
	"Boston University",
	"University of Massachusetts Boston",
	"New England School of Law",
	"Northeastern University",
	"Boston College",
	"Boston College Law School",
]
boston = {
	('Boston', None, 42.358056, -71.063611, 1): default_boston,
	('Boston', None, 7.8689, 126.3734, 1): default_boston,
	('Boston', None, 52.974, -0.0214, 1): default_boston,
	('Boston', None, None, None, 1): default_boston,
}

berlin = {
	('TU Berlin', None, None, None, 1): [
		"Technical University of Berlin",
	],
	('Berlin', None, None, None, 1): [
		"Free University of Berlin",
		"Technical University of Berlin",
		"Humboldt University of Berlin",
		"VLB Berlin",
		"SRH Hochschule Berlin",
	],
	('FU Berlin', None, None, None, 1): [
		"Free University of Berlin",
	],
}

bad_param = {
	('Pisa', None, None, float('inf'), 1): [
		"University of Pisa",
	],
	('Lisbon', None, 1000, 2000, 1): [
		"University of Lisbon",
		"Technical University of Lisbon",
		"ISCTE – Lisbon University Institute",
	],
	('Whasington', None, None, None, 1): [
	],
	('Geneva', None, '120', 0, 1): [
		"University of Geneva",
		"International University in Geneva",
		"University of Edinburgh",
	],
	('University Sofia', None, '9000', None, 1): [
		"Technical University of Sofia",
		"Sophia University",
		"University of Forestry, Sofia",
		"Sofia Medical University",
		"University of Architecture, Civil Engineering and Geodesy",
		"University of National and World Economy",
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
			storedScore = None
			for result, target in zip_longest(institutes, targets):
				name = result[0]['name']
				score = result[1]
				if not storedScore:
					# if the names do not match:
					# --> postpone checking of the current item (the next
					# item might have the same score but a different name)
					if name != target:
						post_check.append(name)
						storedScore = score
					else:
						self.assertEqual(name, target, msg=args)
				# check the score if the names did not match last iteration
				else:
					self.assertEqual(storedScore, score, msg=args)
					self.assertNotEqual(name, target, msg=args)
					storedScore = None
			# check postponed names for beeing inside the target list
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
				print('\t\t"' + result[0]['name'] + '",')
			print('\t],')
		print('}')
