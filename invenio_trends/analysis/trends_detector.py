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

"""Trends detector."""

from __future__ import division

import logging

from elasticsearch import Elasticsearch
from invenio_trends.config import SEARCH_ELASTIC_HOSTS
from sklearn.cluster import KMeans

from invenio_trends.utils import parse_iso_date
from elasticsearch_dsl import Search
import numpy as np


logger = logging.getLogger(__name__)


class TrendsDetector:
    """Trends analyzer and extractor."""

    def __init__(self, config):
        """Set up a new trends detector."""
        self.client = Elasticsearch(hosts=SEARCH_ELASTIC_HOSTS)
        self.index = config['index']
        self.date_field = config['date_field']
        self.analysis_field = config['analysis_field']
        self.doc_type = config['doc_type']

    def run_pipeline(self, reference_date, granularity, foreground_window, background_window,
                     minimum_frequency_threshold, smoothing_len, num_cluster, num_trends):
        """Run pipeline to find trends given parameters."""
        logger.debug('running trends pipeline for %s, %s over %s by %s', reference_date, foreground_window,
                     background_window, granularity)
        foreground_start = reference_date - foreground_window * granularity.value
        background_start = reference_date - background_window * granularity.value
        smoothing_window = np.ones(smoothing_len)

        ids = self.interval_ids(foreground_start, reference_date)
        all_terms = self.term_vectors(ids)
        terms = self.sorting_freq_threshold(all_terms, minimum_frequency_threshold)
        hists = self.terms_histograms(terms, background_start, reference_date, granularity)
        scores = self.hist_scores(hists, foreground_start, smoothing_window)
        trending = self.classify_scores(scores, num_cluster)
        trends = self.prune_scores(trending, num_trends)
        return trends

    def interval_ids(self, start, end):
        """Retrieve list of ids occurring between start and end."""
        logger.debug('retrieving ids from %s to %s', start, end)
        q = Search(using=self.client, index=self.index) \
            .fields(['']) \
            .filter('exists', field=self.analysis_field) \
            .filter('range', **{self.date_field: {'gt': start, 'lte': end}})
        return [elem.meta.id for elem in q.scan()]

    def term_vectors(self, ids, chunk=100):
        """Retrieve all terms together with their stats."""
        if not len(ids):
            return []
        logger.debug('retrieving term vectors for %s ids', len(ids))
        vectors = []
        for pos in range(0, len(ids), chunk):
            q = self.client.mtermvectors(
                index=self.index,
                doc_type=self.doc_type,
                ids=ids[pos:pos + chunk],
                fields=[self.analysis_field],
                field_statistics=False,
                term_statistics=True,
                offsets=False,
                payloads=False,
                positions=False,
                realtime=True
            )
            for doc in q['docs']:
                if self.analysis_field in doc['term_vectors']:
                    vectors.append(doc['term_vectors'][self.analysis_field]['terms'])

        assert len(ids) == len(vectors)
        words = {}
        for vec in vectors:
            for word, freqs in vec.items():
                if word in words:
                    words[word]['term_freq'] += freqs['term_freq']
                    words[word]['doc_freq'] += 1
                else:
                    words[word] = {
                        'term_total': freqs['ttf'],  # estimate
                        'doc_total': freqs['doc_freq'],  # estimate
                        'term_freq': freqs['term_freq'],
                        'doc_freq': 1,
                    }
        return words

    def sorting_freq_threshold(self, terms, min_freq_threshold):
        """Eliminated low frequency and sort dict into a list of tuple according to their frequency."""
        if not len(terms):
            return []
        logger.debug('thresholding %s terms with minimum %s', len(terms), min_freq_threshold)
        filtered = [(term, stats) for term, stats in terms.items() if stats['doc_freq'] >= min_freq_threshold]
        return sorted(filtered, key=lambda elem: -elem[1]['doc_freq'])

    def terms_histograms(self, terms, start, end, gran):
        """Retrieve all term histogram and normalize them."""
        if not len(terms):
            return []
        hist_reference = self.date_histogram(start, end, gran)
        hists = []
        for term, stats in terms:
            hist = self.date_histogram(start, end, gran, term=term)
            logger.debug('retrieving %s histogram bins for %s', len(hist[0]), term)
            if len(hist[0]):
                hists.append((term, stats, self.normalize_histogram(hist, hist_reference)))
        return hists

    def hist_scores(self, hists, foreground_start, smoothing_window):
        """Apply moving average and compute z-score relative to foreground."""
        if not len(hists):
            return []
        scores = []
        for term, stats, hist in hists:
            score = self.transform_score(hist, foreground_start, smoothing_window)
            scores.append((term, stats, score))
        return scores

    def classify_scores(self, scores, num_cluster):
        """Extract best trending score cluster."""
        if not len(scores):
            return []
        km = KMeans(n_clusters=num_cluster)
        values_only = [score for term, stats, (date, score) in scores]
        logger.debug('classifying %s values', len(values_only))
        pred = km.fit_predict(values_only)
        clusters = km.cluster_centers_
        trending_cluster = np.argmax(np.max(np.gradient(clusters, axis=1), axis=1))
        selected = []
        for i, (term, stats, hist) in enumerate(scores):
            if pred[i] == trending_cluster:
                selected.append((term, stats, hist))
        return selected

    def prune_scores(self, scores, num_trends):
        """Compute newness and keep only selected."""
        if not len(scores):
            return []
        newest = sorted(scores, key=lambda x: -x[1]['doc_freq'] / x[1]['doc_total'])
        logger.info(newest)
        return newest[:num_trends]

    def date_histogram(self, start, end, granularity, term=None):
        """Retrieve the date histogram of all entries or a single term is given."""
        q = Search(using=self.client, index=self.index)[0:0] \
            .filter('range', **{self.date_field: {'gt': start, 'lte': end}})
        if term is not None:
            q = q.query('match_phrase', **{self.analysis_field: term})
        q.aggs.bucket(
            'hist',
            'date_histogram',
            field=self.date_field,
            interval=granularity.name,
            format='date_optional_time'
        )
        hist = q.execute().aggregations.hist.buckets

        if not len(hist):
            return np.array([]), np.array([])

        x, y = zip(*[(parse_iso_date(elem.key_as_string), elem.doc_count) for elem in hist])
        return np.array(x), np.array(y)

    def normalize_histogram(self, hist_numerator, hist_denumerator):
        """Safely normalize given tuple of lists w.r.t. another. Numerator size will be fitted to denumerator one."""
        x, y = hist_numerator
        x_ref, y_ref = hist_denumerator

        before_count = np.where(x_ref == x[0])[0][0]
        after_count = len(x_ref) - np.where(x_ref == x[-1])[0][0] - 1
        y = np.append(np.zeros(before_count), np.append(y, np.zeros(after_count)))

        with np.errstate(divide='ignore', invalid='ignore'):
            res = np.divide(y, y_ref)
            res[~ np.isfinite(res)] = 0
            return x_ref, res

    def transform_score(self, hist, foreground_start, smoothing_window):
        """Score using moving average and z-score w.r.t. foreground."""
        x, y = hist

        y_s = np.convolve(y, smoothing_window, mode='valid')

        invalid = len(y) - len(y_s)
        invalid_before = invalid // 2
        invalid_after = invalid_before + invalid % 2
        x_s = x[invalid_before:-invalid_after] if invalid_before != 0 and invalid_after != 0 else x
        assert len(x_s) == len(y_s)

        foreground_index = np.where(x_s == foreground_start)[0][0]
        x_fg = x_s[foreground_index - invalid_after:]
        y_fg = y_s[foreground_index - invalid_after:]

        zscore = (y_fg - np.mean(y_s)) / np.std(y_s)
        return x_fg, zscore
