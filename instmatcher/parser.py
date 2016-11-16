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
	for alpha2, country in countryList:
		try:
			match = re.search(r'\b(?i){}$'.format(country), affiliation)
		except TypeError:
			return result
		if match:
			result['alpha2'] = alpha2
			result['country'] = countryDict[alpha2]
			result['countrySource'] = 'extract'
			break
	else:
		for country in root.findall('./affiliation/address/country'):
			result['alpha2'] = country.get('key')
			try:
				result['country'] = countryDict[result['alpha2']]
				result['countrySource'] = 'grobid'
				break
			except KeyError:
				pass
	
	for tag in ['settlement', 'region', 'postCode',]:
		for addressTag in root.findall('./affiliation/address/' + tag):
			result[tag] = addressTag.text
			break
	
	return result

def improveInstitutions(institutionList, affiliation):
	'''
	Try to correct a list of institutions retrieved from an affiliation.
	
	:param institutionList: the list of institutions
	:param affiliation: the affiliation string
	'''
	# try to extract the string before the first comma
	pattern = re.compile(r'^[^,]+(?=,)')
	try:
		match = re.search(pattern, affiliation)
	except TypeError:
		return
	try:
		extracted = match.group(0)
	except AttributeError:
		return
	
	# improve the institution list
	if not institutionList:
		institutionList.append(extracted)
	elif institutionList[0] in extracted:
		institutionList[0] = extracted
	elif extracted in institutionList[0]:
		institutionList.insert(1, extracted)
	else:
		institutionList.insert(0, extracted)

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

def grobid(affiliation):
	'''
	Try to extract information from an affiliation string using grobid.
	
	:param affiliation: the affiliation string to be parsed
	'''
	# default return value
	result = {}
	
	# return if the returned string is not parseable
	try:
		root = et.fromstring(queryGrobid(affiliation, _url))
	except et.ParseError:
		return result
	
	# try to find institutions and their corresponding labs and departments
	organisations = root.findall('./affiliation/orgName')
	for org in organisations:
		result.setdefault(org.get('type'), []).append(org.text)
	
	result.update(parseAddress(affiliation, root))
	
	return result

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
	result.update(grobid(affiliation))
	improveInstitutions(result['institution'], affiliation)
	return result
