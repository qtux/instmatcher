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

_url = None
codes, countries = {}, {}
countryInfo = resource_filename(__name__, 'data/countryInfo.txt')
with open(countryInfo) as csvfile:
	data = filter(lambda row: not row[0].startswith('#'), csvfile)
	reader = csv.reader(data, delimiter='\t', quoting=csv.QUOTE_NONE)
	for row in reader:
		countries[row[0]] = row[4]
		codes[row[4]] = row[0]

def init(url):
	'''
	Set the URL pointing to the grobid service.
	
	:param url: the URL to the grobid service
	'''
	global _url
	_url = url

def extractCountry(affiliation):
	lowAffi = affiliation.lower()
	index = -1
	foundCountry = None
	for country in codes:
		newIndex = lowAffi.rfind(country.lower())
		if newIndex > index:
			index = newIndex
			foundCountry = country
	alpha2 = codes.get(foundCountry)
	return alpha2, foundCountry

def grobid(affiliation):
	'''
	Parse the given affiliation string using grobid.
	
	:param affiliation: the affiliation string to be parsed
	'''
	# retrieved address tags
	addressTags = ['settlement', 'region', 'postCode', 'country',]
	# default return value
	result = dict.fromkeys(['institution', 'alpha2',])
	result.update(dict.fromkeys(addressTags))
	
	# let grobid process the given affiliation string
	try:
		cmd = 'affiliations=' + affiliation
	except TypeError:
		return result
	r = requests.post(_url + '/processAffiliations', data=cmd)
	xml = r.content.decode('UTF-8')
	
	# return if the returned string is not parseable
	try:
		root = et.fromstring('<results>' + xml + '</results>')
	except et.ParseError:
		return result
	
	# try to find institutions and their corresponding labs and departments
	organisations = root.findall('./affiliation/orgName')
	for org in organisations:
		orgType = org.get('type')
		orgKey = org.get('key')
		number = next(filter(str.isdigit, orgKey)) if orgKey else '1'
		if number == '1':
			result[orgType] = org.text
		else:
			result[orgType + number] = org.text
	
	# try to find address data
	for tag in addressTags:
		try:
			result[tag] = root.find('./affiliation/address/' + tag).text
		except AttributeError:
			pass
	
	# try to find the alpha2 code and retrieve the corresponding country name
	try:
		countryKey = root.find('./affiliation/address/country').get('key')
		country = countries[countryKey]
	# try to search for a country name rightmost inside the affiliation string
	except (AttributeError, KeyError):
		countryKey, country = extractCountry(affiliation)
	result['alpha2'] = countryKey
	result['country'] = country
	
	return result
