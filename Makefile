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

.SUFFIXES:

# Wikidata query related variables
QUERY_URL		:= https://query.wikidata.org/bigdata/namespace/wdq/sparql
QUERIES			:= $(wildcard query/*.sparql)
QUERY_RESULTS	:= $(patsubst %.sparql,%.csv, $(QUERIES))
INSTITUTIONS	:= instmatcher/data/institutions.csv

# create the target file containing a list of institutions
.PHONY: institutions
institutions: $(INSTITUTIONS)

# join the retrieved csv files into a single file
$(INSTITUTIONS): $(QUERY_RESULTS)
	head -1 $< > $@
	tail -n +2 -q $+ >> $@

# retrieve data from WikiData as a csv file
%.csv: %.sparql
	curl -G -H "Accept: text/csv" $(QUERY_URL) --data-urlencode query@$< > $@

# remove intermediately created files
.PHONY: clean
clean:
	rm -rf $(QUERY_RESULTS)

# remove every created file
.PHONY: clean-all
clean-all: clean
	rm -rf $(INSTITUTIONS)

# run the unit tests
.PHONY: test
test:
	python3 setup.py test

# remove old indices before running unit tests --> force index recreation
.PHONY: test-recreate-indices
test-recreate-indices:
	rm -rf $(wildcard instmatcher/data/*index)
	python3 setup.py test
