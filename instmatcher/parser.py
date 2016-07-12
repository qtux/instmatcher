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

try:
	_required = ['requests', 'pycountry',]
	import requests
	_required.remove('requests')
	import pycountry
	_required.remove('pycountry')
	import xml.etree.ElementTree as et
except ImportError:
	pass

def defaultParse(affiliation):
	return {
		'institute': affiliation,
		'department': None,
		'country': None,
		'city': None,
	}

def grobidParse(affiliation):
	for pkg in _required:
		raise ImportError('{} is required to use grobid'.format(pkg))
	
	cmd = 'affiliations=' + affiliation
	url = 'http://localhost:8080/processAffiliations'
	r = requests.post(url, data=cmd)
	xml = r.content.decode('UTF-8')
	
	try:
		root = et.fromstring(xml)
	except et.ParseError:
		print('Could not parse: "{}"\n{}'.format(affiliation, xml))
		return defaultParse(affiliation)
	
	result = {'institute': '', 'department': '',}
	organisations = root.findall('./orgName')
	for org in organisations:
		if org.get('type') == 'institution':
			result['institute'] = org.text
			break
	for org in organisations:
		if org.get('type') == 'department':
			result['department'] = org.text
			break
	try:
		countryKey = root.find('./address/country').get('key')
		result['country'] = pycountry.countries.get(alpha2=countryKey).name
	except (AttributeError, KeyError):
		result['country'] = None
	try:
		result['city'] = root.find('./address/settlement').text
	except AttributeError:
		result['city'] = None
	print(result)
	return result
