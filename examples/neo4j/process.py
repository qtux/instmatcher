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

import argparse
import yaml
from py2neo import authenticate, Graph, Node, Relationship, NodeSelector
from py2neo.packages.httpstream.http import SocketError
import instmatcher
from multiprocessing import Pool
from time import time
import json
from functools import partial

def printStatistics(processedNodes, duration):
	stats = printStatistics.stats
	stats['time'] += duration
	stats['processed'] += processedNodes
	try:
		stats['ratio'] = stats['processed'] / stats['nodes']
	except ZeroDivisionError:
		stats['ratio'] = float('inf')
	stats['secLeft'] = stats['time'] / stats['ratio'] - stats['time']
	try:
		stats['speed'] = stats['processed'] / stats['time']
	except ZeroDivisionError:
		stats['speed'] = float('inf')
	print('processed {processed:,} of {nodes:,} nodes ({ratio:.2%}) in ' \
		'{time:.2f} s'.format(**stats))
	print('estimated time to finish: {secLeft:.2f} s ' \
		'- performance: {speed:.2f} nodes/s'.format(**stats))

def initialiseStatistics(selection):
	selectionQuery = selection._query_and_parameters[0]
	printStatistics.stats = {'time': 0, 'processed': 0}
	countQuery = selectionQuery.partition('RETURN _ ')[0] + 'RETURN COUNT(_)'
	printStatistics.stats['nodes'] = graph.run(countQuery).evaluate()

def processNodes(graph, task):
	# run task until no nodes are left to be processed
	while True:
		t1 = time()
		processedNodes = task(graph)
		t2 = time()
		if processedNodes == 0:
			break
		printStatistics(processedNodes, t2 - t1)
	print('no nodes left to be processed')

def extract(string, url):
	result = []
	for org in instmatcher.parseAll(string, url):
		alpha2 = org.get('alpha2')
		for settlement in org['settlement']:
			coord = instmatcher.geocode(settlement, alpha2)
			if coord != None:
				org.update(coord)
				break
		result.append(org)
	return result

def createExtractTask(config, limit, procs):
	# define the query to get a chunk of data and init the runtime statistics
	selection = NodeSelector(graph).select(config['affi-label']) \
					.where('NOT _:{}'.format(config['extract-success-label'])) \
					.where('NOT _:{}'.format(config['extract-failure-label'])) \
					.limit(limit)
	initialiseStatistics(selection)
	customExtract = partial(extract, url=config['grobid']['url'])
	
	def task(graph):
		# extract a chunk of data
		nodes, affiliations = [], []
		for node in selection:
			nodes.append(node)
			affiliations.append(node[config['affi-key']])
		
		# process the data using instmatcher in parallel
		with Pool(procs) as pool:
			extractions = pool.map(customExtract, affiliations)
		
		# augment the retrieved nodes in one transaction
		tx = graph.begin()
		for node, extraction in zip(nodes, extractions):
			if not extraction:
				node.add_label(config['extract-failure-label'])
			else:
				node['extraction'] = json.dumps(extraction)
				node.add_label(config['extract-success-label'])
			node.push()
		tx.commit()
		return len(nodes)
	
	return task

def findFirst(extraction):
	for item in extraction:
		result = instmatcher.find(
			item.get('institution'),
			item.get('alpha2'),
			item.get('lat'),
			item.get('lon')
		)
		if result != None:
			return result

def createFindTask(config, limit, procs):
	# create unique constraints on the nodes to be created
	label, property_key = config['inst-label'], 'source'
	if not property_key in graph.schema.get_uniqueness_constraints(label):
		graph.schema.create_uniqueness_constraint(label, property_key)
	
	# define the query to get a chunk of data and init the runtime statistics
	selection = NodeSelector(graph).select(config['affi-label']) \
					.where('_:{}'.format(config['extract-success-label'])) \
					.where('NOT _:{}'.format(config['find-success-label'])) \
					.where('NOT _:{}'.format(config['find-failure-label'])) \
					.limit(limit)
	initialiseStatistics(selection)
	
	def task(graph):
		# extract a chunk of data
		nodes, extractions = [], []
		for node in selection:
			nodes.append(node)
			extractions.append(json.loads(node['extraction']))
		
		# process the data using instmatcher in parallel
		with Pool(procs) as pool:
			institutions = pool.map(findFirst, extractions)
		
		# augment the retrieved nodes in one transaction
		tx = graph.begin()
		for node, institution in zip(nodes, institutions):
			if not institution:
				# mark the node for failure
				node.add_label(config['find-failure-label'])
			else:
				# link the node to the institution and country
				inst = Node(config['inst-label'], **institution)
				# merge the newly created nodes to avoid duplicates
				tx.merge(inst)
				tx.merge(Relationship(inst, config['instOf'], node))
				# mark the node for success
				node.add_label(config['find-success-label'])
			node.push()
		tx.commit()
		return len(nodes)
	
	return task

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Match institutions based' \
		' on affiliation strings contained in Neo4j nodes.')
	parser.add_argument('-p', '--procs', default=4, type=int,
		help='number of processes used (default: %(default)s)')
	parser.add_argument('-l', '--limit', default=250, type=int,
		help='number of nodes to be queried at once (default: %(default)s)')
	parser.add_argument('-c', '--config', default='config.yaml',
		help='path to the configuration file (default: %(default)s)')
	group = parser.add_argument_group('pocessing arguments')
	group.add_argument('--extract', action='store_true',
		help='extract information from affiliation strings')
	group.add_argument('--find', action='store_true',
		help='find the first matching institution for an affiliation')
	args = parser.parse_args()
	if not (args.extract or args.find):
		args = '--extract --find'
		parser.error('at least one of the arguments ' + args + ' is required')
	with open(args.config) as f:
		config = yaml.safe_load(f)
	url = config['neo4j']['host'] + ':' + str(config['neo4j']['port'])
	authenticate(url, config['neo4j']['user'], config['neo4j']['password'])
	try:
		graph = Graph('https://' + url)
	except SocketError:
		raise SystemExit('Could not connect to the Neo4j database.')
	if args.extract:
		print('extracting affiliation strings ...')
		processNodes(graph, createExtractTask(config, args.limit, args.procs))
	if args.find:
		print('finding institutions ...')
		processNodes(graph, createFindTask(config, args.limit, args.procs))
