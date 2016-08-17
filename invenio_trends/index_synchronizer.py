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

from .utils import validate_type
from datetime import datetime
from elasticsearch_dsl import Search
from .config import TRENDS_PARAMS
from Requests import put

class IndexSynchronizer:
    """Synchronize given elasticsearch fields into another document with customized analyser."""

    def __init__(self, index, origin_doc_type, analysis_doc_type, analysis_field, date_field, minimum_date=None, maximum_date=None):

        self.index = validate_type(index, str)
        self.origin_doc_type = validate_type(origin_doc_type, str)
        self.analysis_doc_type = validate_type(analysis_doc_type, str)
        self.analysis_fields = validate_type(analysis_field, str)
        self.date_field = validate_type(date_field, str)
        self.minimum_date = validate_type(minimum_date, datetime, optional=True)
        self.maximum_date = validate_type(maximum_date, datetime, optional=True)

        q = Search(index=index, doc_type=origin_doc_type) \
            .filter('exist', fields=analysis_field) \
            .filter('exist', field=date_field) \
            .filter('range', **{date_field: {'gt': minimum_date, 'lte': maximum_date}})

        if q.count() <= 0:
            raise RuntimeError('cannot find any entry in elasticsearch')

    def parse_stopwords(self, filename):
        with open(filename) as f:
            return [l for l in f.readlines() if not l.startswith('#') and not len(l)]

    def create_analyser(self):


        self.index/_settings

        analyser = {
            "analysis": {
                "analyzer": {
                    "trends_analyser": {
                        "type": "custom",
                        "tokenizer": "icu_tokenizer",
                        "char_filter": [
                            "html_strip"
                        ],
                        "filter": [
                            "asciifolding",
                            "lowercase",
                            "trends_word_delimiter",
                            "trends_number_removal",
                            "trends_latex_removal",
                            "trends_stopwords",
                            "trends_stemmer",
                            "trends_length",
                            "trends_bigram",
                            "trends_spacing_removal",
                            "trim"
                        ]
                    }
                },
                "filter": {
                    "trends_word_delimiter": {
                        "type": "word_delimiter",
                        "generate_word_parts": False,
                        "generate_number_parts": True,
                        "catenate_words": True,
                        "catenate_numbers": True,
                        "catenate_all": False,
                        "preserve_original": False,
                        "split_on_case_change": False,
                        "split_on_numerics": False,
                        "stem_english_possessive": True
                    },
                    "trends_number_removal": {
                        "type": "pattern_replace",
                        "pattern": "([0-9]+)",
                        "replacement": ""
                    },
                    "trends_latex_removal": {
                        "type": "pattern_replace",
                        "pattern": "(\\$[^\\$]+\\$)",
                        "replacement": ""
                    },
                    "trends_spacing_removal": {
                        "type": "pattern_replace",
                        "pattern": "( +)",
                        "replacement": " "
                    },
                    "ctrends_stopwords": {
                        "type": "stop",
                        "stopwords": self.parse_stopwords(TRENDS_PARAMS['stopwords_file']),
                        "ignore_case": True,
                        "remove_trailing": True
                    },
                    "trends_stemmer" : {
                        "type": "stemmer",
                        "name": "light_english"
                    },
                    "trends_bigram" : {
                        "type" : "shingle",
                        "min_shingle_size": TRENDS_PARAMS['minimum_ngram'],
                        "max_shingle_size": TRENDS_PARAMS['maximum_ngram'],
                        "output_unigrams": TRENDS_PARAMS['unigram'],
                        "filler_token": ""
                    },
                    "trends_length": {
                        "type": "length",
                        "min": 2
                    }
                }
            }
        }






