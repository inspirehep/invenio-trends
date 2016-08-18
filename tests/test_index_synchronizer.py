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
from pytest import yield_fixture
import requests as r
import random

PARAMS = {
    'host': 'http://localhost:9200',
    'index': 'invenio-trends-tests',
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
    'stopwords_file': 'stopwords.txt',
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


@yield_fixture(scope='module', autouse=True)
def run_around_tests():
    print("befooore")

    r.post(PARAMS['host']+'/'+PARAMS['index'])
    for id, entry in enumerate([entry_correct, entry_early, entry_late, entry_script]):
        res = r.post(PARAMS['host']+'/'+PARAMS['index']+'/'+PARAMS['source']['doc_type']+'/'+str(id), json=entry).json()

    yield

    r.delete(PARAMS['host'] + '/' + PARAMS['index'])
    print("after")


def test_index():
    print(r.get(PARAMS['host']+'/'+PARAMS['index']+'/_mapping').json())

