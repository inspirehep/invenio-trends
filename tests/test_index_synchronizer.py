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

import requests as r
from pytest import yield_fixture

from invenio_trends.index_synchronizer import IndexSynchronizer

host = 'http://localhost:9200'
index = 'invenio-trends-tests'

PARAMS = {
    'host': host,
    'index': index,
    'source': {
        'analysis_field': 'src_ana',
        'date_field': 'src_date',
        'doc_type': 'src',
    },
    'analysis': {
        'analysis_field': 'dst_ana',
        'date_field': 'dst_date',
        'doc_type': 'dst',
    },
    'minimum_date': '2015-03-01',
    'maximum_date': '2015-04-01',
    'filter_script': "d = doc['earliest_date'].date; d.getDayOfMonth() != 3",
    'unigram': True,
    'minimum_ngram': 2,
    'maximum_ngram': 3,
    'stopwords_file': '../invenio_trends/stopwords.txt',
}

entry_correct = {
    PARAMS['source']['analysis_field']: 'This is the analyzed field. It will be analyzed.',
    PARAMS['source']['date_field']: '2015-03-07',
    'not_selected': 'This field should be ignored.'
}

entry_early = entry_correct.copy()
entry_early.update({PARAMS['source']['date_field']: '2015-02-07'})

entry_late = entry_correct.copy()
entry_late.update({PARAMS['source']['date_field']: '2015-04-07'})

entry_script = entry_correct.copy()
entry_script.update({PARAMS['source']['date_field']: '2015-03-03'})

index_sync = IndexSynchronizer(PARAMS)


@yield_fixture(scope='module', autouse=True)
def run_around_tests():
    r.post(host + '/' + index)
    for id, entry in enumerate([entry_correct, entry_early, entry_late, entry_script]):
        res = r.post(host + '/' + index + '/' + PARAMS['source']['doc_type'] + '/' + str(id), json=entry).json()

    yield

    r.delete(host + '/' + index)


def test_parse_stopwords():
    stopwords = index_sync.parse_stopwords(PARAMS['stopwords_file'])
    for word in stopwords:
        assert word is not ''
        assert not word.startswith('#')
        assert word.find('\n') == -1


def test_setup_analyzer():
    before = r.get(host + '/' + index + '/_settings').json()
    assert 'analysis' not in before[index]['settings']['index']

    index_sync.setup_analyzer()
    after = r.get(host + '/' + index + '/_settings')
    assert 'analysis' in after.json()[index]['settings']['index']


def test_setup_mapping():
    index_sync.setup_mappings()
    ana_field = PARAMS['analysis']['analysis_field']
    ana_type = PARAMS['analysis']['doc_type']
    mappings = r.get(host + '/' + index + '/_mapping/' + PARAMS['analysis']['doc_type'] + '/field/' +
                     PARAMS['analysis']['analysis_field']).json()

    ana_mapping = mappings[index]['mappings'][ana_type][ana_field]['mapping'][ana_field]
    assert ana_mapping['analyzer'] == 'trends_analyzer'
    assert ana_mapping['term_vector'] == 'yes'


def test_synchronize():
    index_sync.synchronize()

    entries = r.post(host + '/' + index + '/_search', json={'query': {'match_all': {}}})
    print(entries)
