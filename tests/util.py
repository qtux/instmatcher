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
from urllib.parse import unquote_plus

class GrobidProxy(BaseHTTPRequestHandler):
	
	def do_POST(self):
		self.send_response(200)
		self.send_header('Content-type', 'text/plain')
		self.end_headers()
		
		if self.path == '/processAffiliations':
			length = int(self.headers['Content-Length'])
			data = self.rfile.read(length).decode('utf-8')
			_, _, tail = data.partition('affiliations=')
			response = GrobidProxy.responses.get(unquote_plus(tail), '')
		else:
			response = ''
		self.wfile.write(bytes(response, 'utf-8'))
	
	def log_message(self, format, *args):
		return

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
	pass

class GrobidServer():
	
	def __init__(self, host, port):
		self.host = host
		self.port = port
		self.proxy = GrobidProxy
		self.proxy.response = {}
		
	def start(self):
		self.server = ThreadedHTTPServer((self.host, self.port), self.proxy)
		thread = threading.Thread(target=self.server.serve_forever)
		thread.daemon = True
		thread.start()
	
	def stop(self):
		self.server.shutdown()
		self.server.server_close()
	
	def setResponse(self, question, response):
		self.proxy.responses[question] = response



