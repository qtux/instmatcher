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
import pycountry
import xml.etree.ElementTree as et

_url = None

def init(url = 'http://localhost:8080'):
	global _url
	_url = url

def grobid(affiliation):
	cmd = 'affiliations=' + affiliation
	r = requests.post(_url + '/processAffiliations', data=cmd)
	xml = r.content.decode('UTF-8')
	
	try:
		root = et.fromstring('<results>' + xml + '</results>')
	except et.ParseError:
		return None
	
	result = {}
	try:
		countryKey = root.find('./affiliation/address/country').get('key')
		result['cc'] = countryKey
		result['country'] = pycountry.countries.get(alpha2=countryKey).name
	except (AttributeError, KeyError):
		result['cc'] = None
		result['country'] = None
	
	try:
		result['city'] = root.find('./affiliation/address/settlement').text
	except AttributeError:
		result['city'] = None
	
	organisations = root.findall('./affiliation/orgName')
	for org in organisations:
		if org.get('type') == 'institution':
			result['institute'] = org.text
			return result
	return None
