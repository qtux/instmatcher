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

boston = {
	('Boston', None, 42.358056, -71.063611, 1): [
		"Boston University",
		"University of Massachusetts Boston",
		"New England School of Law",
		"Northeastern University",
		"Boston College",
		"Boston College Law School",
	],
	('Boston', None, 7.8689, 126.3734, 1): [
		"Boston University",
		"University of Massachusetts Boston",
		"New England School of Law",
		"Northeastern University",
		"Boston College",
		"Boston College Law School",
	],
	('Boston', None, 52.974, -0.0214, 1): [
		"Boston University",
		"University of Massachusetts Boston",
		"New England School of Law",
		"Northeastern University",
		"Boston College",
		"Boston College Law School",
	],
	('Boston', None, None, None, 1): [
		"Boston University",
		"University of Massachusetts Boston",
		"New England School of Law",
		"Northeastern University",
		"Boston College",
		"Boston College Law School",
	],
}

washington = {
	('Washington University', None, None, None, 1): [
		"Washington University in St. Louis",
		"George Washington University",
		"Central Washington University",
		"Trinity Washington University",
		"Eastern Washington University",
		"Western Washington University",
		"George Washington University Law School",
		"George Washington University School of Nursing",
	],
	('Washington', None, 38.9169, -77.043, 0): [
		"Washington University in St. Louis",
		"Western Washington University",
		"University of Mary Washington",
		"George Washington University",
		"Washington and Lee University",
		"Central Washington University",
		"Trinity Washington University",
		"Eastern Washington University",
		"Washington Adventist University",
		"Washington College of Law",
		"Washington Female Seminary",
		"Washington State University",
		"Washington State University Spokane",
		"University of Washington School of Law",
		"George Washington University Law School",
		"George Washington University School of Nursing",
		"Washington State University Tri-Cities",
		"Washington and Lee University School of Law",
		"University of Washington School of Social Work",
		"Washington State University College of Veterinary Medicine",
	],
	('Washington', None, 38.9169, -77.043, 100): [
		"Washington University in St. Louis",
		"Western Washington University",
		"University of Mary Washington",
		"George Washington University",
		"Washington and Lee University",
		"Central Washington University",
		"Trinity Washington University",
		"Eastern Washington University",
		"Washington Adventist University",
		"Washington College of Law",
		"Washington Female Seminary",
		"Washington State University",
		"Washington State University Spokane",
		"University of Washington School of Law",
		"George Washington University Law School",
		"George Washington University School of Nursing",
		"Washington State University Tri-Cities",
		"Washington and Lee University School of Law",
		"University of Washington School of Social Work",
		"Washington State University College of Veterinary Medicine",
	],
	('Washington University in St. Louis', None, None, None, 1): [
		"Washington University in St. Louis",
	],
	('Washington', None, 38.9169, -77.043, 1): [
		"University of Mary Washington",
		"George Washington University",
		"Trinity Washington University",
		"Washington Adventist University",
		"Washington College of Law",
		"George Washington University Law School",
		"George Washington University School of Nursing",
		"Washington University in St. Louis",
		"Western Washington University",
		"Washington and Lee University",
		"Central Washington University",
		"Eastern Washington University",
		"Washington Female Seminary",
		"Washington State University",
		"Washington State University Spokane",
		"University of Washington School of Law",
		"Washington State University Tri-Cities",
		"Washington and Lee University School of Law",
		"University of Washington School of Social Work",
		"Washington State University College of Veterinary Medicine",
	],
	('Washington', None, None, None, 1): [
		"Washington University in St. Louis",
		"Western Washington University",
		"University of Mary Washington",
		"George Washington University",
		"Washington and Lee University",
		"Central Washington University",
		"Trinity Washington University",
		"Eastern Washington University",
		"Washington Adventist University",
		"Washington College of Law",
		"Washington Female Seminary",
		"Washington State University",
		"Washington State University Spokane",
		"University of Washington School of Law",
		"George Washington University Law School",
		"George Washington University School of Nursing",
		"Washington State University Tri-Cities",
		"Washington and Lee University School of Law",
		"University of Washington School of Social Work",
		"Washington State University College of Veterinary Medicine",
	],
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

london = {
	('London', None, None, None, 1): [
		"University of London",
		"University of the Arts London",
		"City University London",
		"London Metropolitan University",
		"University of East London",
		"King's College London",
		"University of North London",
		"London School of Economics",
		"Queen Mary, University of London",
		"Royal Holloway, University of London",
		"Imperial College London",
		"University of London Institute in Paris",
		"Goldsmiths, University of London",
		"Birkbeck, University of London",
		"SOAS, University of London",
		"London Guildhall University",
		"Diplomatic Academy of London",
		"University of West London",
		"London South Bank University",
		"University of London International Programmes",
		"Richmond, The American International University in London",
		"University of East London School of Law and Social Sciences",
		"Centre for History in Public Health, London School of Hygiene and Tropical Medicine",
		"University of Western Ontario",
	],
	('London', None, 42.9881, -81.3318, 1): [
		"University of Western Ontario",
		"University of London",
		"University of the Arts London",
		"City University London",
		"London Metropolitan University",
		"University of East London",
		"King's College London",
		"University of North London",
		"London School of Economics",
		"Queen Mary, University of London",
		"Royal Holloway, University of London",
		"Imperial College London",
		"University of London Institute in Paris",
		"Goldsmiths, University of London",
		"Birkbeck, University of London",
		"SOAS, University of London",
		"London Guildhall University",
		"Diplomatic Academy of London",
		"University of West London",
		"London South Bank University",
		"University of London International Programmes",
		"Richmond, The American International University in London",
		"University of East London School of Law and Social Sciences",
		"Centre for History in Public Health, London School of Hygiene and Tropical Medicine",
	],
	('London', 'CA', 42.9881, -81.3318, 1):[
		"University of Western Ontario",
	],
	('London', 'CA', None, None, 1):[
		"University of Western Ontario",
	],
	('London', 'GB', 42.9881, -81.3318, 1): [
		"University of London",
		"University of the Arts London",
		"City University London",
		"London Metropolitan University",
		"University of East London",
		"King's College London",
		"University of North London",
		"London School of Economics",
		"Queen Mary, University of London",
		"Royal Holloway, University of London",
		"Imperial College London",
		"Goldsmiths, University of London",
		"Birkbeck, University of London",
		"SOAS, University of London",
		"London Guildhall University",
		"Diplomatic Academy of London",
		"University of West London",
		"London South Bank University",
		"University of London International Programmes",
		"Richmond, The American International University in London",
		"University of East London School of Law and Social Sciences",
		"Centre for History in Public Health, London School of Hygiene and Tropical Medicine",
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
	('Whasington', None, None, None, 1): [],
	('Geneva', None, '120', 0, 1): [
		"University of Geneva",
		"International University in Geneva",
		"University of Edinburgh",
	],
	('University Sofia', None, '9000', None, 1): [
		"Sophia University",
		"Technical University of Sofia",
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

cases =  {
	**boston,
	**washington,
	**berlin,
	**london,
	**bad_param,
	**none_perm
}

class test_core(unittest.TestCase):
	def setUp(self):
		core.init(procs=os.cpu_count(), multisegment=True)
	
	def test_queryAll(self):
		for args, targets in cases.items():
			institutes = core.queryAll(*args)
			for result, target in zip_longest(institutes, targets):
				self.assertEqual(result['name'], target, msg=args)
	
	def test_query(self):
		for args, targets in cases.items():
			institute = core.query(*args)
			for target in targets:
				self.assertEqual(institute['name'], target, msg=args)
				break
			else:
				self.assertEqual(institute, None, msg=args)
	
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
	core.init(procs=os.cpu_count(), multisegment=True)
	dicts = {
		'boston': boston,
		'washington': washington,
		'berlin': berlin,
		'london': london,
		'bad_param': bad_param,
	}
	for name, item in dicts.items():
		print(name + ' = {')
		for args, targets in item.items():
			institutes = core.queryAll(*args)
			print('\t', args,': [', sep='')
			for result in institutes:
				print('\t\t"' + result['name'] + '",')
			print('\t],')
		print('}')
