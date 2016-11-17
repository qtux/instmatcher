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

'''Module to parse an affiliation string using grobid.'''

import requests
import xml.etree.ElementTree as et
import csv
from pkg_resources import resource_filename
import re

_url = None
# generate two dictionaries mapping the ISO 3166-1 alpha-2 country codes to
# the corresponding country names and to the corresponding population sizes
countryDict, populationDict = {}, {}
countryInfo = resource_filename(__name__, 'data/countryInfo.txt')
with open(countryInfo) as csvfile:
	data = filter(lambda row: not row[0].startswith('#'), csvfile)
	reader = csv.reader(data, delimiter='\t', quoting=csv.QUOTE_NONE)
	for row in reader:
		countryDict[row[0]] = row[4]
		populationDict[row[0]] = int(row[7])

# create a list of country code and country tuples
countryList = list(countryDict.items())
# add alternative country names
altCountries = resource_filename(__name__, 'data/alternativeCountryNames.csv')
with open(altCountries) as csvfile:
	reader = csv.reader(csvfile)
	for row in reader:
		countryList.append((row[0], row[1]))
# sort the list by the population size
countryList.sort(key=lambda item: populationDict[item[0]], reverse=True)
# move country names which contain a part of another country name before these
# countries in order to avoid false assignments when extracting them
for i in range(len(countryList)):
	for j in range(i + 1, len(countryList)):
		if countryList[i][1] in countryList[j][1]:
			countryList.insert(i, countryList.pop(j))

def init(url):
	'''
	Set the URL pointing to the grobid service.
	
	:param url: the URL to the grobid service
	'''
	global _url
	_url = url

def parseAddress(affiliation, root):
	'''
	Parse every address tag inside the retrieved grobid xml string and
	try to improve the country information searching for a valid country
	at the end of the affiliation string.
	
	:param affiliation: the affiliation string
	:param root: the root node of the grobid xml string
	'''
	result = {}
	
	# extract the country code
	for alpha2, country in countryList:
		try:
			match = re.search(r'\b(?i){}$'.format(country), affiliation)
		except TypeError:
			return result
		if match:
			countrySource = 'extract'
			break
	else:
		for country in root.findall('./affiliation/address/country'):
			alpha2 = country.get('key')
			countrySource = 'grobid'
			break
		else:
			alpha2 = None
	
	# retrieve the country information corresponding to the country code
	try:
		result['country'] = countryDict[alpha2]
		result['alpha2'] = alpha2
		result['countrySource'] = countrySource
	except KeyError:
		pass
	
	# retrieve settlement, region and postCode
	for tag in ['settlement', 'region', 'postCode',]:
		for addressTag in root.findall('./affiliation/address/' + tag):
			result[tag] = addressTag.text
			break
	
	return result

def parseOrganisations(affiliation, root, pattern=re.compile(r'^[^,]+(?=,)')):
	'''
	Parse every type of organisation inside the retrieved grobid xml
	string and try to improve the list of possible institutions using
	the part of the affiliation string before the first comma.
	
	:param affiliation: the affiliation string
	:param root: the root node of the grobid xml string
	:param pattern: the pattern for the string before the first comma
	'''
	result = {'institution': []}
	for org in root.findall('./affiliation/orgName'):
		result.setdefault(org.get('type'), []).append(org.text)
	
	try:
		match = re.search(pattern, affiliation)
	except TypeError:
		return result
	try:
		extracted = match.group(0)
	except AttributeError:
		return result
	
	if not result['institution']:
		result['institution'].append(extracted)
	elif result['institution'][0] in extracted:
		result['institution'][0] = extracted
	elif extracted in result['institution'][0]:
		result['institution'].insert(1, extracted)
	else:
		result['institution'].insert(0, extracted)
	
	return result

def queryGrobid(affiliation, url):
	'''
	Try to retrieve a structured xml representation of the the
	affiliation string using grobid.
	
	:param affiliation: the affiliation string to be sent to grobid
	'''
	try:
		cmd = 'affiliations=' + affiliation
	except TypeError:
		return '<results></results>'
	r = requests.post(url + '/processAffiliations', data=cmd)
	return '<results>' + r.content.decode('UTF-8') + '</results>'

def parse(affiliation):
	'''
	Parse the given affiliation string.
	
	:param affiliation: the affiliation string to be parsed
	'''
	# required return values
	result = {
		'institution': [],
		'alpha2': None,
		'settlement': None,
	}
	try:
		root = et.fromstring(queryGrobid(affiliation, _url))
	except et.ParseError:
		return result
	result.update(parseOrganisations(affiliation, root))
	result.update(parseAddress(affiliation, root))
	return result
