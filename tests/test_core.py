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

class test_core(unittest.TestCase):
	def setUp(self):
		core.init(procs=os.cpu_count(), multisegment=True)
	
	def test_query(self):
		cases = {
			# some bad input parameters
			('Whasington', None, None): None,
			('Beijing', 1000, 2000): 'Beijing Foreign Studies University',
			('Rome', None, float('inf')): 'American University of Rome',
			('University Sofia', '9000', None): 'Technical University of Sofia',
			('Geneva', '120', 0): 'University of Geneva',
			# some None permutations
			(None, None, None): None,
			(None, 30, 40, 1): None,
			(None, 30, 40, None): None,
			(None, 30, None, 1): None,
			(None, None, 40, 1): None,
			(None, None, 40, None): None,
			(None, 30, None, None): None,
			(None, None, None, 1): None,
			(None, None, None, None): None,
			# Berlin universities
			('Berlin', None, None): 'Free University of Berlin',
			('TU Berlin', None, None): 'Technical University of Berlin',
			('FU Berlin', None, None): 'Free University of Berlin',
			# different London universities
			('London', None, None): 'University of London',
			('London', 42.9881,-81.3318): 'University of Western Ontario',
			# one Boston University independent on coordinates
			('Boston', None, None): 'Boston University',
			('Boston', 42.358056, -71.063611): 'Boston University',
			('Boston', 7.8689, 126.3734): 'Boston University',
			('Boston', 52.974, -0.0214): 'Boston University',
			# different Washington universities
			('Washington', None, None): 'Washington University in St. Louis',
			('Washington', 38.9169, -77.0430, 0): 'Washington University in St. Louis',
			('Washington', 38.9169, -77.0430, 100): 'Washington University in St. Louis',
			('Washington', 38.9169, -77.0430, 1): 'University of Mary Washington',
			('Washington', 38.9169, -77.0430, 1): 'University of Mary Washington',
			('Washington University in St. Louis', None, None): 'Washington University in St. Louis',
			('Washington University', None, None): 'Washington University in St. Louis',
		}
		for args, result in cases.items():
			institute = core.query(*args)
			if not institute:
				self.assertEqual(None, result, msg=args)
			else:
				self.assertEqual(institute['name'], result, msg=args)
	
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
