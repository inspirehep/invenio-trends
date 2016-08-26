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
from datetime import timedelta

from invenio_trends import etl
from invenio_trends.analysis.granularity import Granularity

SEARCH_ELASTIC_HOSTS = os.environ.get('SEARCH_ELASTIC_HOSTS', 'localhost:9200').split(';')
MAGPIE_API_URL = 'http://magpie.inspirehep.net/api'
CACHE_REDIS_URL = os.environ.get('CACHE_REDIS_URL', 'redis://localhost:6379/0')

WORD2VEC_TIMEOUT = 0.2  # seconds
WORD2VEC_THRES = 0.7
WORD2VEC_MAX = 5

CELERYBEAT_SCHEDULE = {
    'update-index': {
        'task': 'invenio_trends.tasks.update_index',
        'schedule': timedelta(hours=24)
    },
    'update-trends': {
        'task': 'invenio_trends.tasks.update_trends',
        'schedule': timedelta(hours=24)
    },
}

TRENDS_ENDPOINT = '/trends'

TRENDS_INDEX = 'records-trends'
TRENDS_SOURCE_INDEX = 'records-hep'
TRENDS_DOC_TYPE = 'hep'
TRENDS_ANALYSIS_FIELD = 'abstracts.value'
TRENDS_DATE_FIELD = 'earliest_date'
TRENDS_ID_FIELD = 'self_recid'
TRENDS_TOKENIZER = 'icu_tokenizer'
TRENDS_MINIMUM_DATE = '2013-02-01'
TRENDS_MAXIMUM_DATE = None
TRENDS_FILTER_SCRIPT = "d = doc['earliest_date'].date; d.getDayOfYear() != 1"
TRENDS_UNIGRAM = False
TRENDS_MINIMUM_NGRAM = 2
TRENDS_MAXIMUM_NGM = 3
TRENDS_STOPWORDS_FILE = os.path.dirname(etl.__file__) + '/stopwords.txt'

TRENDS_HIST_GRANULARITY = Granularity.week
TRENDS_GRANULARITY = Granularity.day
TRENDS_REDIS_KEY = 'invenio:trends'

TRENDS_FOREGROUND_WINDOW = 10
TRENDS_BACKGROUND_WINDOW = 365
TRENDS_MINIMUM_FREQUENCY_THRESHOLD = 5
TRENDS_SMOOTHING_LEN = 7
TRENDS_NUM_CLUSTER = 3
TRENDS_NUM = 9

TRENDS_PARAMS = {
    'index': TRENDS_INDEX,
    'source_index': TRENDS_SOURCE_INDEX,
    'doc_type': TRENDS_DOC_TYPE,
    'analysis_field': TRENDS_ANALYSIS_FIELD,
    'date_field': TRENDS_DATE_FIELD,
    'id_field': TRENDS_ID_FIELD,
    'tokenizer': TRENDS_TOKENIZER,
    'minimum_date': TRENDS_MINIMUM_DATE,
    'maximum_date': TRENDS_MAXIMUM_DATE,
    'filter_script': TRENDS_FILTER_SCRIPT,
    'unigram': TRENDS_UNIGRAM,
    'minimum_ngram': TRENDS_MINIMUM_NGRAM,
    'maximum_ngram': TRENDS_MAXIMUM_NGM,
    'stopwords_file': TRENDS_STOPWORDS_FILE,
}
