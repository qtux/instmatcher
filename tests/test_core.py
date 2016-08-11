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

default_washington = [
		("Washington University in St. Louis", 19.322445604370078),
		("Western Washington University", 18.739033600113743),
		("University of Mary Washington", 18.32768188955521),
		("George Washington University", 17.39741765208082),
		("Washington and Lee University", 17.100261142716654),
		("Washington Adventist University", 6.790551240068012),
		("Washington College of Law", 6.790551240068012),
		("Washington Female Seminary", 6.790551240068012),
		("Washington State University", 6.790551240068012),
		("Central Washington University", 6.790551240068012),
		("Eastern Washington University", 6.790551240068012),
		("Trinity Washington University", 6.790551240068012),
		("Washington State University Spokane", 6.006170328659464),
		("University of Washington School of Law", 6.006170328659464),
		("Washington State University Tri-Cities", 5.384234017909727),
		("Washington and Lee University School of Law", 5.384234017909727),
		("George Washington University Law School", 5.384234017909727),
		("George Washington University School of Nursing", 5.384234017909727),
		("University of Washington School of Social Work", 5.384234017909727),
		("Washington State University College of Veterinary Medicine", 4.879014228384662),
	]

washington = {
	('Washington University', None, None, None, 1): [
		("Washington University in St. Louis", 23.417664233009848),
		("George Washington University", 22.11830583992404),
		("Central Washington University", 8.071367147202459),
		("Eastern Washington University", 8.071367147202459),
		("Trinity Washington University", 8.071367147202459),
		("Western Washington University", 8.071367147202459),
		("George Washington University Law School", 6.399794070999632),
		("George Washington University School of Nursing", 6.399794070999632),
	],
	('Washington University in St. Louis', None, None, None, 1): [
		("Washington University in St. Louis", 19.170150612542795),
	],
	('Washington', None, 38.9169, -77.043, 0): default_washington,
	('Washington', None, 38.9169, -77.043, 100): default_washington,
	('Washington', None, None, None, 1): default_washington,
	('Washington', None, 38.9169, -77.043, 1): [
		("University of Mary Washington", 18.32768188955521),
		("George Washington University", 17.39741765208082),
		("Washington Adventist University", 6.790551240068012),
		("Washington College of Law", 6.790551240068012),
		("Trinity Washington University", 6.790551240068012),
		("George Washington University Law School", 5.384234017909727),
		("George Washington University School of Nursing", 5.384234017909727),
		("Washington University in St. Louis", 19.322445604370078),
		("Western Washington University", 18.739033600113743),
		("Washington and Lee University", 17.100261142716654),
		("Washington Female Seminary", 6.790551240068012),
		("Washington State University", 6.790551240068012),
		("Central Washington University", 6.790551240068012),
		("Eastern Washington University", 6.790551240068012),
		("Washington State University Spokane", 6.006170328659464),
		("University of Washington School of Law", 6.006170328659464),
		("Washington State University Tri-Cities", 5.384234017909727),
		("Washington and Lee University School of Law", 5.384234017909727),
		("University of Washington School of Social Work", 5.384234017909727),
		("Washington State University College of Veterinary Medicine", 4.879014228384662),
	],
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

london = {
	('London', None, None, None, 1): [
		("University of London", 20.33170234005281),
		("University of the Arts London", 19.117796794729102),
		("City University London", 18.107920424214367),
		("London Metropolitan University", 17.95981968297066),
		("University of East London", 17.831483684058934),
		("King's College London", 16.914452863800445),
		("University of North London", 16.11513142638017),
		("London School of Economics", 15.473918972566295),
		("Queen Mary, University of London", 14.228938893630183),
		("Royal Holloway, University of London", 12.311298499762149),
		("Imperial College London", 11.738845580537337),
		("University of London Institute in Paris", 11.122885450338657),
		("London Guildhall University", 6.653109699166122),
		("SOAS, University of London", 6.653109699166122),
		("Birkbeck, University of London", 6.653109699166122),
		("Goldsmiths, University of London", 6.653109699166122),
		("University of West London", 6.653109699166122),
		("Diplomatic Academy of London", 6.653109699166122),
		("London South Bank University", 5.884604747942058),
		("University of London International Programmes", 5.884604747942058),
		("Richmond, The American International University in London", 5.275256499909219),
		("University of East London School of Law and Social Sciences", 4.370193291769139),
		("Centre for History in Public Health, London School of Hygiene and Tropical Medicine", 3.7302100307592894),
		("University of Western Ontario", 2.556488732010612),
	],
	('London', None, 42.9881, -81.3318, 1): [
		("University of Western Ontario", 2.556488732010612),
		("University of London", 20.33170234005281),
		("University of the Arts London", 19.117796794729102),
		("City University London", 18.107920424214367),
		("London Metropolitan University", 17.95981968297066),
		("University of East London", 17.831483684058934),
		("King's College London", 16.914452863800445),
		("University of North London", 16.11513142638017),
		("London School of Economics", 15.473918972566295),
		("Queen Mary, University of London", 14.228938893630183),
		("Royal Holloway, University of London", 12.311298499762149),
		("Imperial College London", 11.738845580537337),
		("University of London Institute in Paris", 11.122885450338657),
		("London Guildhall University", 6.653109699166122),
		("SOAS, University of London", 6.653109699166122),
		("Birkbeck, University of London", 6.653109699166122),
		("Goldsmiths, University of London", 6.653109699166122),
		("University of West London", 6.653109699166122),
		("Diplomatic Academy of London", 6.653109699166122),
		("London South Bank University", 5.884604747942058),
		("University of London International Programmes", 5.884604747942058),
		("Richmond, The American International University in London", 5.275256499909219),
		("University of East London School of Law and Social Sciences", 4.370193291769139),
		("Centre for History in Public Health, London School of Hygiene and Tropical Medicine", 3.7302100307592894),
	],
	('London', 'CA', 42.9881, -81.3318, 1):[
		("University of Western Ontario", 3.556488732010612),
	],
	('London', 'CA', None, None, 1):[
		("University of Western Ontario", 3.556488732010612),
	],
	('London', 'GB', 42.9881, -81.3318, 1): [
		("University of London", 21.33170234005281),
		("University of the Arts London", 20.117796794729102),
		("City University London", 19.107920424214367),
		("London Metropolitan University", 18.95981968297066),
		("University of East London", 18.831483684058934),
		("King's College London", 17.914452863800445),
		("University of North London", 17.11513142638017),
		("London School of Economics", 16.473918972566295),
		("Queen Mary, University of London", 15.228938893630183),
		("Royal Holloway, University of London", 13.311298499762149),
		("Imperial College London", 12.738845580537337),
		("London Guildhall University", 7.653109699166122),
		("SOAS, University of London", 7.653109699166122),
		("Birkbeck, University of London", 7.653109699166122),
		("Goldsmiths, University of London", 7.653109699166122),
		("University of West London", 7.653109699166122),
		("Diplomatic Academy of London", 7.653109699166122),
		("London South Bank University", 6.884604747942058),
		("University of London International Programmes", 6.884604747942058),
		("Richmond, The American International University in London", 6.275256499909219),
		("University of East London School of Law and Social Sciences", 5.370193291769139),
		("Centre for History in Public Health, London School of Hygiene and Tropical Medicine", 4.73021003075929),
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
		("Sophia University", 9.991618024907513),
		("Technical University of Sofia", 9.7781524771213),
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
		core.init(procs=os.cpu_count(), multisegment=True)
	
	def run_query(self, tests):
		for args, targets in tests.items():
			institute = core.query(*args)
			for target in targets:
				self.assertEqual(institute['name'], target[0], msg=args)
				break
			else:
				self.assertEqual(institute, None, msg=args)
	
	def run_queryAll(self, tests):
		for args, targets in tests.items():
			institutes = core.queryAll(*args)
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
		self.run_queryAll(bad_param)
		self.run_query(bad_param)
	
	def test_none_perm(self):
		self.run_queryAll(none_perm)
		self.run_query(none_perm)
		
	def test_london(self):
		self.run_queryAll(london)
		self.run_query(london)
		
	def test_berlin(self):
		self.run_queryAll(berlin)
		self.run_query(berlin)
		
	def test_washington(self):
		self.run_queryAll(washington)
		self.run_query(washington)
		
	def test_boston(self):
		self.run_queryAll(boston)
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
		for args in item.keys():
			institutes = core.queryAll(*args)
			print('\t', args,': [', sep='')
			for result in institutes:
				pair = '("' + result[0]['name'] + '", ' + str(result[1]) + ')'
				print('\t\t' + pair + ',')
			print('\t],')
		print('}')
