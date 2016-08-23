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

'''Module to patch the pycountry module adding Kosovo.'''

def patchGet(pycountry):
	'''
	Patch the pycountry.countries.get function adding Kosovo.
	
	Kosovo is represented using the alpha2 "XK", the alpha3 "UNK" and
	the official name "Republic of Kosovo".
	
	:param pycountry: the name of the pycountry module
	'''
	oldGet = pycountry.countries.get
	if oldGet.__name__ == 'newGet':
		return
	dataClass = type(
		pycountry.ExistingCountries.data_class_name,
		(pycountry.db.Data,),
		{}
	)
	kosovo = {
		'alpha2': 'XK',
		'alpha3': 'UNK',
		'name': 'Kosovo',
		'official_name': 'Republic of Kosovo',
	}
	def newGet(*args, **kwargs):
		try:
			return oldGet(*args, **kwargs)
		except KeyError as error:
			for key, value in kwargs.items():
				if (key, value) in kosovo.items():
					return dataClass(None, **kosovo)
			raise error
	pycountry.countries.get = newGet
