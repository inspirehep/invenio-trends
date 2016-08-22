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

"""Configuration options."""

import os

from invenio_trends import analysis

TRENDS_ENDPOINT = "/api/trends"

TRENDS_PARAMS = {
    'host': 'http://localhost:9200',
    'index': 'records-trends',
    'source_index': 'records-hep',
    'doc_type': 'hep',
    'analysis_field': 'abstracts.value',
    'date_field': 'earliest_date',
    'id_field': 'self_recid',
    'tokenizer': 'icu_tokenizer',
    'minimum_date': '2013-02-01',
    'maximum_date': None,
    'filter_script': "d = doc['earliest_date'].date; d.getDayOfYear() != 1",
    'unigram': True,
    'minimum_ngram': 2,
    'maximum_ngram': 3,
    'stopwords_file': os.path.dirname(analysis.__file__) + '/stopwords.txt',
}
