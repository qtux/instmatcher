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
# generate a dictionary of the ISO 3166-1 alpha-2 country codes mapping to the
# corresponding country names
countries = {}
countryInfo = resource_filename(__name__, 'data/countryInfo.txt')
with open(countryInfo) as csvfile:
	data = filter(lambda row: not row[0].startswith('#'), csvfile)
	reader = csv.reader(data, delimiter='\t', quoting=csv.QUOTE_NONE)
	for row in reader:
		countries[row[0]] = row[4]
# create a list of country code and country tuples sorted by the length of the
# country name to avoid false positive recognition of countries when the name is
# part of another country name
countryList = list(countries.items())
countryList.sort(key=lambda item: len(item[1]), reverse=True)

def init(url):
	'''
	Set the URL pointing to the grobid service.
	
	:param url: the URL to the grobid service
	'''
	global _url
	_url = url

def extractCountry(affiliation):
	'''
	Try to extract a country from an affiliation string.
	
	:param affiliation: the affiliation to be searched in
	'''
	for alpha2, country in countryList:
		match = re.search(r'\b(?i){}$'.format(country), affiliation)
		if match:
			return alpha2, country
	return None, None

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
	
	# try to find the alpha2 code and the corresponding country name
	try:
		countryKey = root.find('./affiliation/address/country').get('key')
		country = countries[countryKey]
	except (AttributeError, KeyError):
		countryKey, country = extractCountry(affiliation)
	result['alpha2'] = countryKey
	result['country'] = country
	
	return result
