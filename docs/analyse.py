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

import csv
import instmatcher
import argparse
import pprint

def analyse(sample):
	pp = pprint.PrettyPrinter(indent=4)
	instmatcher.init('http://0.0.0.0:8080')
	
	result = sample + '_classified'
	with open(sample, 'r') as s, open(result, 'w') as r:
		reader = csv.reader(s)
		writer = csv.writer(r)
		
		fieldnames = next(reader)
		fieldnames.append('classification')
		writer.writerow(fieldnames)
		
		affiStrings = []
		institutes = []
		
		print('processing affiliation strings...')
		for row in reader:
			affiStrings.append(row[0])
			institutes.append(instmatcher.match(row[0]))
		
		i = 1
		size = len(institutes)
		for affiString, institute in zip(affiStrings, institutes):
			row = [affiString]
			print(chr(27) + "[2J")
			print(affiString, '({} of {})'.format(i, size))
			pp.pprint(institute)
			
			# retrieve an valid input
			answer = input('Is this correct? [y/n] ')
			while answer not in ('y', 'n'):
				answer = input('enter either y or n')
			
			# check for true/false postive and negatives
			classification = 'negative' if not institute else 'positive'
			if answer == 'y':
				row.append('true_' + classification)
			elif answer == 'n':
				row.append('false_' + classification)
			
			# write result
			writer.writerow(row)
			i += 1

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Analyse classification.')
	parser.add_argument('-s', '--sample', help='path to the sample file')
	args = parser.parse_args()
	analyse(args.sample)
