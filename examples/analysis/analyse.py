import csv
import os
import operator
import instmatcher

grobid_url = 'http://localhost:8080'
path = os.path.join('..', '..', 'instmatcher', 'data', 'institutions.csv')
wd_url = []
with open(path) as csvfile:
	reader = csv.DictReader(csvfile)
	for row in reader:
		wd_url.append(row['source'])

def calculate_metrics(result):
	accuracy = (result['true_pos'] + result['true_neg']) / sum(result.values())
	precision = result['true_pos'] / (result['true_pos'] + result['false_pos'])
	recall = result['true_pos'] / (result['true_pos'] + result['false_neg'])
	f1 = 2 * precision * recall / (precision + recall)
	return accuracy, precision, recall, f1

def classify(actual, expected, isNegative, isEqual=operator.eq):
	if isNegative(actual):
		if isEqual(actual, expected):
			return 'true_neg'
		else:
			return 'false_neg'
	else:
		if isEqual(actual, expected):
			return 'true_pos'
		else:
			return 'false_pos'

def classify_parser():
	classification = {
		'institution':{
			'true_pos': 0, 'true_neg': 0,
			'false_pos': 0, 'false_neg': 0
		},
		'alpha2':{
			'true_pos': 0, 'true_neg': 0,
			'false_pos': 0, 'false_neg': 0
		},
		'settlement':{
			'true_pos': 0, 'true_neg': 0,
			'false_pos': 0, 'false_neg': 0
		},
	}
	with open('pmc_optimal_extraction.csv') as csvfile:
		reader = csv.DictReader(csvfile)
		for row in reader:
			result =  instmatcher.parse(row['input'], grobid_url)
			
			inst = result['institution'] if result else ''
			category = classify(inst, row['institution'], lambda x: x == '')
			classification['institution'][category] += 1
			
			alpha2 = result.get('alpha2', '') if result else ''
			category = classify(alpha2, row['alpha2'], lambda x: x == '')
			classification['alpha2'][category] += 1
			
			settlement = result['settlement'] if result else []
			category = classify(
				settlement,
				row['settlement'],
				lambda actual: not actual,
				lambda actual, expected: (expected == '' and actual == []) or expected in actual
			)
			classification['settlement'][category] += 1
			
			
			
			if not settlement:
				if row['settlement'] == '':
					classification['settlement']['true_neg'] += 1
				else:
					classification['settlement']['false_neg'] += 1
			else:
				if row['settlement'] in settlement:
					classification['settlement']['true_pos'] += 1
				else:
					classification['settlement']['false_pos'] += 1
	return classification

def classify_geocoder():
	classification = {
		'lat/lon': {
			'true_pos': 0, 'true_neg': 0,
			'false_pos': 0, 'false_neg': 0,
		}
	}
	with open('pmc_optimal_extraction.csv') as csvfile:
		reader = csv.DictReader(csvfile)
		for row in reader:
			result = instmatcher.geocode(row['settlement'], row['alpha2'])
			lat = str(result['lat']) if result else ''
			lon = str(result['lon']) if result else ''
			category = classify(
				(lat, lon),
				(row['lat'], row['lon']),
				lambda x: x == ('','')
			)
			classification['lat/lon'][category] += 1
	return classification

def classify_find():
	classification = {
		'institution': {
			'true_pos': 0, 'true_neg': 0,
			'false_pos': 0, 'false_neg': 0,
		}
	}
	with open('pmc_optimal_extraction.csv') as csvfile:
		reader = csv.DictReader(csvfile)
		for row in reader:
			result = instmatcher.find(
				row['institution'],
				row['alpha2'],
				row['lat'],
				row['lon']
			)
			source = result['source'] if result else ''
			category = classify(source, row['wd_url'], lambda x: x == '')
			classification['institution'][category] += 1
	return classification

def classify_find_relative_to_local_database():
	classification = {
		'institution': {
			'true_pos': 0, 'true_neg': 0,
			'false_pos': 0, 'false_neg': 0,
		}
	}
	with open('pmc_optimal_extraction.csv') as csvfile:
		reader = csv.DictReader(csvfile)
		counter = 0
		for row in reader:
			if row['wd_url'] not in wd_url:
				counter += 1
				continue
			result = instmatcher.find(
				row['institution'],
				row['alpha2'],
				row['lat'],
				row['lon']
			)
			source = result['source'] if result else ''
			category = classify(source, row['wd_url'], lambda x: x == '')
			classification['institution'][category] += 1
	print('skipped {} of {} entries'.format(
		counter, counter + sum(classification['institution'].values())
	))
	return classification

def classify_match():
	classification = {
		'institution': {
			'true_pos': 0, 'true_neg': 0,
			'false_pos': 0, 'false_neg': 0,
		}
	}
	with open('pmc_optimal_extraction.csv') as csvfile:
		reader = csv.DictReader(csvfile)
		for row in reader:
			result = instmatcher.match(row['input'], grobid_url)
			source = result['source'] if result else ''
			category = classify(source, row['wd_url'], lambda x: x == '')
			classification['institution'][category] += 1
	return classification

def classify_match_relative_to_local_database():
	classification = {
		'institution': {
			'true_pos': 0, 'true_neg': 0,
			'false_pos': 0, 'false_neg': 0,
		}
	}
	with open('pmc_optimal_extraction.csv') as csvfile:
		reader = csv.DictReader(csvfile)
		counter = 0
		for row in reader:
			if row['wd_url'] not in wd_url:
				counter += 1
				continue
			result = instmatcher.match(row['input'], grobid_url)
			source = result['source'] if result else ''
			category = classify(source, row['wd_url'], lambda x: x == '')
			classification['institution'][category] += 1
	print('skipped {} of {} entries'.format(
		counter, counter + sum(classification['institution'].values())
	))
	return classification

print('Match performance (in regard to Wikidata) :')
print('label\taccuracy\tprecision\trecall\tf1')
for k,v in classify_match().items():
	metrics = calculate_metrics(v)
	print('{}\t{:.2f}\t{:.2f}\t{:.2f}\t{:.2f}'.format(k, *metrics))

print('Matching performance (in regard to the local database):')
print('label\taccuracy\tprecision\trecall\tf1')
for k,v in classify_match_relative_to_local_database().items():
	metrics = calculate_metrics(v)
	print('{}\t{:.2f}\t{:.2f}\t{:.2f}\t{:.2f}'.format(k, *metrics))

print('Parse performance:')
print('label\taccuracy\tprecision\trecall\tf1')
for k,v in classify_parser().items():
	metrics = calculate_metrics(v)
	print('{}\t{:.2f}\t{:.2f}\t{:.2f}\t{:.2f}'.format(k, *metrics))

print('Geocode performance:')
print('label\taccuracy\tprecision\trecall\tf1')
for k,v in classify_geocoder().items():
	metrics = calculate_metrics(v)
	print('{}\t{:.2f}\t{:.2f}\t{:.2f}\t{:.2f}'.format(k, *metrics))

print('Find performance (in regard to Wikidata):')
print('label\taccuracy\tprecision\trecall\tf1')
for k,v in classify_find().items():
	metrics = calculate_metrics(v)
	print('{}\t{:.2f}\t{:.2f}\t{:.2f}\t{:.2f}'.format(k, *metrics))

print('Find performance in (in regard to the local database):')
print('label\taccuracy\tprecision\trecall\tf1')
for k,v in classify_find_relative_to_local_database().items():
	metrics = calculate_metrics(v)
	print('{}\t{:.2f}\t{:.2f}\t{:.2f}\t{:.2f}'.format(k, *metrics))
