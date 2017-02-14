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

def parseAddress(affiliation, root, patternHK=re.compile(r'\b(?i)Hong Kong\b'),
		patternMO=re.compile(r'\b(?i)Macao\b')):
	'''
	Parse every address tag inside the retrieved grobid xml string and
	try to improve the country information searching for a valid country
	at the end of the affiliation string.
	
	:param affiliation: the affiliation string
	:param root: the root node of the grobid xml string
	:param patternHK: the pattern to search for Hong Kong
	:param patternMO: the pattern to search for Macao
	'''
	result = {}
	
	# extract the country code
	for alpha2, country in countryList:
		try:
			match = re.search(r'(?i)\b{}$'.format(country), affiliation)
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
	
	# fix the country codes of Hong Kong and Macao
	if alpha2 == 'CN' and re.search(patternHK, affiliation):
		alpha2 = 'HK'
	if alpha2 == 'CN' and re.search(patternMO, affiliation):
		alpha2 = 'MO'
	
	# retrieve the country information corresponding to the country code
	try:
		result['country'] = countryDict[alpha2]
		result['alpha2'] = alpha2
		result['countrySource'] = countrySource
	except KeyError:
		pass
	
	# retrieve region and postCode
	for tag in ['region', 'postCode',]:
		for addressTag in root.findall('./affiliation/address/' + tag):
			result[tag] = addressTag.text
			break
	
	return result

def parseSettlement(affiliation, root,
		pattern=re.compile(r'\b(?<!\-)[A-Za-z][a-z]*\b(?!\-)')):
	'''
	Extract every possible settlement starting with the words betweeen
	the second and third last commas, followed by the words between the
	last and second last comma and finally with the settlement extracted
	by grobid.
	
	:param affiliation: the affiliation string
	:param root: the root node of the grobid xml string
	:param pattern: the pattern for a country name
	'''
	result = {'settlement':[]}
	try:
		splitAffi = affiliation.split(',')
	except AttributeError:
		return result
	try:
		leftmost = ' '.join(re.findall(pattern, splitAffi[-3]))
		if leftmost != '':
			result['settlement'].append(leftmost)
	except IndexError:
		leftmost = None
	try:
		rightmost = ' '.join(re.findall(pattern, splitAffi[-2]))
		if rightmost != '' and leftmost != rightmost:
			result['settlement'].append(rightmost)
	except IndexError:
		rightmost = None
	for addressTag in root.findall('./affiliation/address/settlement'):
		grobid = addressTag.text
		if grobid != leftmost and grobid != rightmost:
			result['settlement'].append(grobid)
		break
	return result

def parseOrganisations(affiliation, root, pattern=re.compile(r'^[^,]+(?=,)')):
	'''
	Retrieve groups of organisations consisting of institutions,
	departments and/or laboratories based on the retrieved grobid xml
	string. Additionally, try to improve the first institution using the
	part of the affiliation string before the first comma.
	
	Note that if multiple institutions, departments or laboratories are
	in the same group they are considered identical. Only one of them is
	taken for the returned data structure.
	
	:param affiliation: the affiliation string
	:param root: the root node of the grobid xml string
	:param pattern: the pattern for the string before the first comma
	'''
	result = []
	for org in root.findall('./affiliation/orgName'):
		# determine index
		orgKey = org.get('key')
		try:
			index = int(re.search(r'\d+', orgKey).group()) - 1
		except TypeError:
			index = 0
		# update or insert item at index
		item = {org.get('type'): org.text}
		try:
			result[index].update(item)
		except IndexError:
			result.insert(index, item)
	
	for item in result:
		item.update({'institutionSource': 'grobid'})
	
	try:
		match = re.search(pattern, affiliation)
	except TypeError:
		return result
	try:
		extracted = match.group(0)
	except AttributeError:
		return result
	
	if not result or not 'institution' in result[0]:
		result.insert(0, {
			'institution': extracted,
			'institutionSource':'regexInsert',
		})
	elif result[0]['institution'] in extracted:
		result[0]['institution'] = extracted
		result[0]['institutionSource'] = 'regexReplace'
	elif extracted in result[0]['institution']:
		result.insert(1, {
			'institution': extracted,
			'institutionSource':'regexInsertAfter',
		})
	else:
		result.insert(0, {
			'institution': extracted,
			'institutionSource':'regexInsertBefore',
		})
	
	return result

def queryGrobid(affiliation, url):
	'''
	Try to retrieve a structured xml representation of the the
	affiliation string using grobid.
	
	:param affiliation: the affiliation string to be sent to grobid
	:param url: the URL to the grobid service
	'''
	try:
		cmd = 'affiliations=' + affiliation
	except TypeError:
		return '<results></results>'
	r = requests.post(url + '/processAffiliations', data=cmd)
	return '<results>' + r.content.decode('UTF-8') + '</results>'

def parseAll(affiliation, url):
	'''
	Yield all possible institutions along with their corresponding
	departments, laboratories and address information using grobid and
	regular expressions to parse the given affiliation string.
	
	:param affiliation: the affiliation string to be parsed
	:param url: the URL to the grobid service
	'''
	try:
		root = et.fromstring(queryGrobid(affiliation, url))
	except et.ParseError:
		return
	organisations = parseOrganisations(affiliation, root)
	address = parseAddress(affiliation, root)
	settlement = parseSettlement(affiliation, root)
	for organisation in organisations:
		result = {}
		result.update(organisation)
		result.update(address)
		result.update(settlement)
		yield result

def parse(affiliation, url):
	'''
	Get the first institution along with the corresponding
	department, laboratory and address information using grobid and
	regular expressions to parse the given affiliation string.
	
	:param affiliation: the affiliation string to be parsed
	:param url: the URL to the grobid service
	'''
	try:
		return next(parseAll(affiliation, url))
	except StopIteration:
		return
