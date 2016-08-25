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

from .util import GrobidServer
from pkg_resources import resource_filename
import xml.etree.ElementTree as et
import string
import random

import unittest
from instmatcher.parser import grobid, init

class test_parser(unittest.TestCase):
	
	def setUp(self):
		tree = et.parse(resource_filename(__name__, 'test_parser.xml'))
		root = tree.getroot()
		uniqueKeys = set()
		chars = string.ascii_letters + string.digits
		grobidResponses = {}
		self.tests = {}
		for testcase in root:
			affiTag = testcase.find('./affiliation')
			affiString = et.tostring(affiTag, encoding='unicode')
			affiString = affiString.replace('\n', '').replace('\t', '')
			
			resultTag = testcase.find('./result')
			result = {}
			result['institute'] = resultTag.find('./institute').text
			result['alpha2'] = resultTag.find('./alpha2').text
			result['country'] = resultTag.find('./country').text
			result['city'] = resultTag.find('./city').text
			
			while True:
				size = random.randrange(1, 42)
				key = ''.join(random.choice(chars) for _ in range(size))
				if key not in uniqueKeys:
					uniqueKeys.add(key)
					break
			grobidResponses[key] = affiString
			self.tests[key] = result
		
		host = 'localhost'
		port = 8081
		url = 'http://' + host + ':' + str(port)
		init(url)
		self.server = GrobidServer(host, port, grobidResponses)
		self.server.start()
	
	def test(self):
		
		for affiliation, result in self.tests.items():
			self.assertEqual(grobid(affiliation), result)
	
	def tearDown(self):
		self.server.stop()
