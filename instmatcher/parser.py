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
_codes = None

def init(url):
	'''
	Initialise the grobid url and the country code dictionary.
	
	:param url: the URL to the grobid service
	'''
	global _url, _codes
	_url = url
	_codes = {}
	countryInfo = resource_filename(__name__, 'data/countryInfo.txt')
	with open(countryInfo) as csvfile:
		data = filter(lambda row: not row[0].startswith('#'), csvfile)
		reader = csv.reader(data, delimiter='\t', quoting=csv.QUOTE_NONE)
		for row in reader:
			_codes[row[0]] = row[4]

def grobid(affiliation):
	'''
	Parse the given affiliation string using grobid.
	
	:param affiliation: the affiliation string to be parsed
	'''
	# default return value
	result = dict.fromkeys(['institute', 'city', 'alpha2', 'country',])
	
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
	
	# try to find an organisation (consider only the first one)
	organisations = root.findall('./affiliation/orgName')
	for org in organisations:
		if org.get('type') == 'institution':
			result['institute'] = org.text
			break
	# return immediately if none was found
	else:
		return result
	
	# try to find the alpha2 code and retrieve the corresponding country name
	try:
		countryKey = root.find('./affiliation/address/country').get('key')
		result['alpha2'] = countryKey
		result['country'] = _codes[countryKey]
	except (AttributeError, KeyError):
		result['alpha2'] = None
		result['country'] = None
	
	# try to find the city name
	try:
		result['city'] = root.find('./affiliation/address/settlement').text
	except AttributeError:
		result['city'] = None
	
	return result
