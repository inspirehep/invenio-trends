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

"""Index synchronizer."""

import logging

import Requests as r

logger = logging.getLogger(__name__)

class IndexSynchronizer:
    """Synchronization helper for maintaining another index type with customized analyser."""

    def __init__(self, config):
        """Unwrapping configuration defined in config.py."""
        self.host = config['host']
        self.index = config['index']

        self.src_analysis_fld = config['source']['analysis_field']
        self.src_date_fld = config['source']['date_field']
        self.src_doc_type = config['source']['doc_type']

        self.min_date = config['minimum_date']
        self.max_date = config['maximum_date']
        self.selector_script = config['filter_script']

        self.ana_analysis_fld = config['analysis']['analysis_field']
        self.ana_date_fld = config['analysis']['date_field']
        self.ana_doc_type = config['analysis']['doc_type']

        self.unigram = config['unigram']
        self.min_ngram = config['minimum_ngram']
        self.max_ngram = config['maximum_ngram']
        self.stopwords_file = config['stopwords_file']

    def synchronize(self):
        """Reindex entries to new analysed type."""
        logger.info('reindex %s started', self.index)
        reindex = self.synchronize_config()
        res = r.post(self.host+'/_reindex', data=reindex).json()

        if res.get('ok') is not True:
            raise RuntimeError('cannot reindex: %s' % res)
        logger.info('reindex %s terminated', self.index)

    def setup_mappings(self):
        """Create mappings for analyzed field and date field."""
        mappings = {
            "properties": {
                self.ana_date_fld: {
                    "type": "date",
                    "format": "strict_date_optional_time||epoch_millis"
                },
                self.src_analysis_fld: {
                    "type": "string",
                    "term_vector": "yes",
                    "analyzer": "trends_analyser"
                }
            }
        }

        res = r.put(self.host+'/'+self.index+'/_mapping/'+self.src_doc_type, data=mappings).json()
        if res.get('ok') is not True:
            raise RuntimeError('cannot create mappings: %s' % res)

    def setup_analyzer(self):
        """Create customized analyser into the new type resulting into a short downtime for the whole index."""
        self.close_index()

        analyser = self.analyzer_config()
        res = r.put(self.host+'/'+self.index+'/_settings', data=analyser).json()

        if res.get('ok') is not True:
            raise RuntimeError('cannot add analyzer: %s' % res)
        logger.info('setup analyzer')

        self.open_index()

    def open_index(self):
        """Open an index or raise an exception."""
        res = r.post(self.host+'/'+self.index+'/_open').json()
        if res.get('ok') is not True:
            raise RuntimeError('cannot open index: %s' % res)
        logger.info('open index %s', self.index)

    def close_index(self):
        """Close an index or raise an exception."""
        res = r.post(self.host+'/'+self.index+'/_close').json()
        if res.get('ok') is not True:
            raise RuntimeError('cannot close index: %s' % res)
        logger.info('close index %s', self.index)

    def parse_stopwords(self, filename):
        """Parse stopwords in given file eliminating comment and empty lines."""
        with open(filename) as f:
            return [l for l in f.readlines() if not l.startswith('#') and not len(l)]

    def synchronize_config(self):
        """Return query data for reindexing an index to itself (changing type)."""
        selector_script = {}
        if self.selector_script is not None:
            selector_script['script'] = {
                'script': self.selector_script
            }
        return {
            "source": {
                "index": self.index,
                "type": self.src_doc_type,
                "query": {
                    "bool": {
                        "filter": [
                            {
                                "exists": [
                                    {
                                        "field": self.src_analysis_fld
                                    },
                                    {
                                        "field": self.src_date_fld
                                    }
                                ]
                            },
                            {
                                "range": {
                                    self.src_date_fld: {
                                        "gt": self.min_date,
                                        "lte": self.max_date
                                    }
                                }
                            },
                            selector_script
                        ]
                    }
                },
                "_source": [
                    self.src_analysis_fld,
                    self.src_date_fld
                ]
            },
            "dest": {
                "index": self.index,
                "type": self.ana_doc_type
            },
            "script": {
                "inline": 'ctx._source.'+self.ana_analysis_fld+' = ctx._source.remove("'+self.src_analysis_fld+'");'
                          'ctx._source.'+self.ana_date_fld+' = ctx._source.remove("'+self.src_date_fld+'");'
            }
        }

    def analyzer_config(self):
        """Return query data for adding an analyzer."""
        return {
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
                        "stopwords": self.parse_stopwords(self.stopwords_file),
                        "ignore_case": True,
                        "remove_trailing": True
                    },
                    "trends_stemmer" : {
                        "type": "stemmer",
                        "name": "light_english"
                    },
                    "trends_bigram" : {
                        "type" : "shingle",
                        "min_shingle_size": self.min_ngram,
                        "max_shingle_size": self.max_ngram,
                        "output_unigrams": self.unigram,
                        "filler_token": ""
                    },
                    "trends_length": {
                        "type": "length",
                        "min": 2
                    }
                }
            }
        }

