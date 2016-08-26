# -*- coding: utf-8 -*-
#
# This file is part of inspirehep.
# Copyright (C) 2016 CERN.
#
# inspirehep is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# inspirehep is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with inspirehep; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""Index synchronizer tests."""

from time import sleep

import requests as r
from pytest import yield_fixture

from invenio_trends.config import SEARCH_ELASTIC_HOSTS, TRENDS_STOPWORDS_FILE
from invenio_trends.etl.index_synchronizer import IndexSynchronizer

host = 'http://' + SEARCH_ELASTIC_HOSTS[0]
src_index = 'invenio-trends-test-source'
index = 'invenio-trends-test-destination'
doc_type = 'trends'
analysis_field = 'analysis'
date_field = 'date'
id_field = 'id'
stopwords_file = TRENDS_STOPWORDS_FILE

PARAMS = {
    'index': index,
    'source_index': src_index,
    'doc_type': doc_type,
    'analysis_field': analysis_field,
    'date_field': date_field,
    'id_field': id_field,
    'tokenizer': 'standard',
    'minimum_date': '2015-03-01',
    'maximum_date': '2015-04-01',
    'filter_script': "d = doc['date'].date; d.getDayOfMonth() != 3",
    'unigram': True,
    'minimum_ngram': 2,
    'maximum_ngram': 3,
    'stopwords_file': stopwords_file,
}

entry_correct = {
    analysis_field: 'This is the analyzed field. It will be analyzed.',
    date_field: '2015-03-07',
    id_field: '7',
    'not_selected': 'This field should be ignored.'
}

entry_early = entry_correct.copy()
entry_early.update({date_field: '2015-02-07'})

entry_late = entry_correct.copy()
entry_late.update({date_field: '2015-04-07'})

entry_script = entry_correct.copy()
entry_script.update({date_field: '2015-03-03'})

index_sync = IndexSynchronizer(PARAMS)


@yield_fixture(scope='module', autouse=True)
def run_around_tests():
    r.post(host + '/' + src_index)
    for id, entry in enumerate([entry_correct, entry_early, entry_late, entry_script]):
        r.post(host + '/' + src_index + '/' + doc_type + '/' + str(id), json=entry).json()

    sleep(2)
    yield
    r.delete(host + '/' + src_index)
    r.delete(host + '/' + index)


def test_parse_stopwords():
    stopwords = index_sync.parse_stopwords(stopwords_file)
    for word in stopwords:
        assert word != ''
        assert not word.startswith('#')
        assert word.find('\n') == -1


def test_setup_index():
    index_sync.setup_index()
    sleep(2)
    res = r.get(host + '/' + index).json()
    assert index in res


def test_setup_analyzer():
    before = r.get(host + '/' + index + '/_settings').json()
    assert 'analysis' not in before[index]['settings']['index']

    index_sync.setup_analyzer()
    after = r.get(host + '/' + index + '/_settings')
    assert 'analysis' in after.json()[index]['settings']['index']


def test_setup_mapping():
    index_sync.setup_mappings()
    mappings = r.get(host + '/' + index + '/_mapping/' + doc_type + '/field/' +
                     PARAMS['analysis_field']).json()

    ana_mapping = mappings[index]['mappings'][doc_type][analysis_field]['mapping'][analysis_field]
    assert ana_mapping['analyzer'] == 'trends_analyzer'
    assert ana_mapping['term_vector'] == 'yes'


def test_synchronize():
    index_sync.synchronize()
    sleep(2)

    entries = r.post(host + '/' + index + '/_search', json={'query': {'match_all': {}}}).json()
    hits = entries['hits']['hits']

    assert len(hits) == 1
    assert hits[0]['_source'] == {
        analysis_field: entry_correct[analysis_field],
        date_field: entry_correct[date_field],
        id_field: entry_correct[id_field],
    }
