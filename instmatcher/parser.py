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

import requests
import xml.etree.ElementTree as et
from . import countries

_url = None

def init(url):
	global _url
	_url = url

def grobid(affiliation):
	cmd = 'affiliations=' + affiliation
	r = requests.post(_url + '/processAffiliations', data=cmd)
	xml = r.content.decode('UTF-8')
	result = dict.fromkeys(['institute', 'city', 'alpha2', 'country',])
	
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
		result['country'] = countries.get(alpha2=countryKey).name
	except (AttributeError, KeyError):
		result['alpha2'] = None
		result['country'] = None
	
	# try to find the city name
	try:
		result['city'] = root.find('./affiliation/address/settlement').text
	except AttributeError:
		result['city'] = None
	
	return result
