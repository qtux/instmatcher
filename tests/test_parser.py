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

from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
import threading

from pkg_resources import resource_filename
import xml.etree.ElementTree as et
import string
import random

import unittest
from instmatcher.parser import grobid, init

grobidAnswers = {}
tests = {}

class GrobidProxy(BaseHTTPRequestHandler):
	
	def provideResponses(self, responses):
		self.responses = responses
	
	def do_POST(self):
		self.send_response(200)
		self.send_header('Content-type', 'text/plain')
		self.end_headers()
		
		if self.path == '/processAffiliations':
			length = int(self.headers['Content-Length'])
			data = self.rfile.read(length).decode('utf-8')
			_, _, tail = data.partition('affiliations=')
			response = grobidAnswers.get(tail, '')
		else:
			response = ''
		self.wfile.write(bytes(response, 'utf-8'))
	
	def log_message(self, format, *args):
		return

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
	pass

class test_geo(unittest.TestCase):
	
	def setUp(self):
		tree = et.parse(resource_filename(__name__, 'test_parser.xml'))
		root = tree.getroot()
		uniqueKeys = set()
		chars = string.ascii_letters + string.digits
		for testcase in root:
			affiTag = testcase.find('./affiliation')
			affiString = et.tostring(affiTag, encoding='unicode')
			affiString = affiString.replace('\n', '').replace('\t', '')
			
			resultTag = testcase.find('./result')
			result = {}
			try:
				result['institute'] = resultTag.find('./institute').text
				result['alpha2'] = resultTag.find('./alpha2').text
				result['country'] = resultTag.find('./country').text
				result['city'] = resultTag.find('./city').text
			except AttributeError:
				result = None
			
			while True:
				size = random.randrange(1, 42)
				key = ''.join(random.choice(chars) for _ in range(size))
				if key not in uniqueKeys:
					uniqueKeys.add(key)
					break
			grobidAnswers[key] = affiString
			tests[key] = result
		
		self.host = 'localhost'
		self.port = 8081
		self.server = ThreadedHTTPServer((self.host, self.port), GrobidProxy)
		thread = threading.Thread(target=self.server.serve_forever)
		thread.daemon = True
		thread.start()
	
	def test(self):
		url = 'http://' + self.host + ':' + str(self.port)
		init(url)
		for affiliation, result in tests.items():
			self.assertEqual(grobid(affiliation), result)
	
	def tearDown(self):
		self.server.shutdown()
		self.server.server_close()
