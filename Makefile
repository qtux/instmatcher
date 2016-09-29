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
JOINED_RESULT	:= query/query.csv
ORGANISATIONS	:= instmatcher/data/institutes.csv
COUNTRY_INFO	:= instmatcher/data/countryInfo.txt

# create the target file containing a list of organisations
.PHONY: organisations
organisations: $(ORGANISATIONS)

# enhance the queried items adding country information
$(ORGANISATIONS): $(JOINED_RESULT)
	python3 query/enhance.py --src $< --dest $@ --countries $(COUNTRY_INFO)

# join the retrieved csv files into a single file
$(JOINED_RESULT): $(QUERY_RESULTS)
	head -1 $< > $@
	tail -n +2 -q $+ >> $@

# retrieve data from WikiData as a csv file
%.csv: %.sparql
	curl -G -H "Accept: text/csv" $(QUERY_URL) --data-urlencode query@$< > $@

# remove intermediately created files
.PHONY: clean
clean:
	rm -rf $(QUERY_RESULTS)
	rm -rf $(JOINED_RESULT)

# remove every created file
.PHONY: clean-all
clean-all: clean
	rm -rf $(ORGANISATIONS)
