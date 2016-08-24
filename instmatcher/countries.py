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

'''Module to search for a country wrapping pycountry.'''

import pycountry

dataClass = type(pycountry.countries.get(alpha2='CR'))
kosovo = {
	'alpha2': 'XK',
	'alpha3': 'UNK',
	'name': 'Kosovo',
	'official_name': 'Republic of Kosovo',
}
kosovoObj = dataClass(None, **kosovo)

def get(*args, **kwargs):
	'''
	This function wraps the pycountry.countries.get function and adds
	Kosovo to the list of retrievable countries using the temporary
	alpha-2 code "XK" and the "UNK" as the temporary alpha-3 code.
	
	It accepts the same arguments as the wrapped function from
	pycountry: Exactly one keyword argument must be supplied to retrieve
	a country specifying a single feature like its name.
	
	:param args: positional arguments (ignored)
	:param kwargs: keyword arguments (exactly one must be supplied)
	'''
	try:
		return pycountry.countries.get(*args, **kwargs)
	except KeyError as error:
		for key, value in kwargs.items():
			if (key, value) in kosovo.items():
				return kosovoObj
		raise error
