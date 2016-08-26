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

"""Invenio module that adds a trends api to the platform."""

import logging
from datetime import datetime

import numpy as np
import requests as r
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
from flask import Blueprint, jsonify, make_response, request
from redis import StrictRedis

from .analysis.granularity import Granularity
from .analysis.trends_detector import TrendsDetector
from .config import CACHE_REDIS_URL, MAGPIE_API_URL, SEARCH_ELASTIC_HOSTS, \
    TRENDS_DATE_FIELD, TRENDS_ENDPOINT, TRENDS_HIST_GRANULARITY, \
    TRENDS_INDEX, TRENDS_PARAMS, TRENDS_REDIS_KEY, WORD2VEC_MAX, \
    WORD2VEC_THRES, WORD2VEC_TIMEOUT, TRENDS_FOREGROUND_WINDOW, TRENDS_SMOOTHING_LEN
from .utils import DatetimeConverter, GranularityConverter, parse_iso_date, \
    return_iso_date

logger = logging.getLogger(__name__)
client = Elasticsearch(hosts=SEARCH_ELASTIC_HOSTS)
redis = StrictRedis.from_url(CACHE_REDIS_URL)


def register_converters(state):
    """Register custom path converters to be used inside route directives."""
    state.app.url_map.converters['datetime'] = DatetimeConverter
    state.app.url_map.converters['granularity'] = GranularityConverter

blueprint = Blueprint(
    'invenio_trends',
    __name__,
    url_prefix=TRENDS_ENDPOINT,
)
blueprint.record_once(register_converters)


@blueprint.route('/granularities')
def granularities():
    """Return granularities choices."""
    return jsonify(list(Granularity.__members__))


@blueprint.route('/dates')
def dates():
    """Return maximum and minimum date from dataset."""
    q = Search(using=client, index=TRENDS_INDEX)[0:0]
    q.aggs.bucket('min_date', 'min', field=TRENDS_DATE_FIELD)
    q.aggs.bucket('max_date', 'max', field=TRENDS_DATE_FIELD)
    res = q.execute().aggregations
    return jsonify({'maximum': res.min_date.value_as_string, 'minimum': res.max_date.value_as_string})


@blueprint.route('/search/<string:query>/')
@blueprint.route('/search/<string:query>/<datetime:start>')
@blueprint.route('/search/<string:query>/<datetime:start>/<datetime:end>')
@blueprint.route('/search/<string:query>/<datetime:start>/<datetime:end>/<granularity:gran>')
def search_trends(query, start=None, end=None, gran=None):
    """Return histogram matching query."""
    similar_words = request.args.get('similar_words') is not None
    return_score = request.args.get('return_score') is not None
    return search(query, start, end, gran, similar_words, return_score)


@blueprint.route('/emerging')
def emerging_trends():
    """Return cached latest trends."""
    cached = redis.hmget(TRENDS_REDIS_KEY, 'terms', 'start', 'end', 'granularity')
    if cached[0] is None:
        return jsonify({})

    terms, start, end, gran = cached
    return search(terms, parse_iso_date(start), parse_iso_date(end), Granularity[gran])


def search(query, start=None, end=None, gran=None, similar_words=False, return_score=False):
    """Search index for given query string and return corresponding histograms."""
    if not gran:
        gran = TRENDS_HIST_GRANULARITY

    terms = [t.strip() for t in query.split(',') if len(t.strip())]
    if not len(terms):
        return bad_request('no terms')

    td = TrendsDetector(TRENDS_PARAMS)
    minValue = 0
    maxValue = 0
    minDate = end if end else datetime.max
    maxDate = start if start else datetime.min

    all_terms = []
    related_terms = {}
    for term in terms:
        similarities = word2vec(term) if similar_words else []
        related_terms[term] = similarities
        all_terms.append(term)
        all_terms.extend(similarities)

    data = []
    for term in all_terms:
        dates, values = td.date_histogram(start, end, gran, term)
        if return_score:
            values = np.nan_to_num((values - np.mean(values)) / np.std(values))

        if len(values):
            minValue = min(minValue, min(values))
            maxValue = max(maxValue, max(values))
            minDate = min(minDate, min(dates))
            maxDate = max(maxDate, max(dates))

        series = [{'date': return_iso_date(date), 'value': value} for date, value in zip(dates, values)]
        data.append({'name': term, 'series': series})

    ret = {
        'stats': {
            'minValue': minValue,
            'maxValue': maxValue,
            'minDate': return_iso_date(minDate),
            'maxDate': return_iso_date(maxDate)
        },
        'related_terms': related_terms,
        'data': data
    }
    return jsonify(ret)


def word2vec(term):
    """Fetch associates words and select them following their matching scores."""
    try:
        data = {'corpus': 'keywords', 'positive': [term.replace(' ', '')], 'negative': []}
        res = r.post(MAGPIE_API_URL + '/word2vec', json=data, timeout=WORD2VEC_TIMEOUT).json()
        similarities = []
        for word, score in sorted(res['vector'], key=lambda e: -e[1]):
            if score >= WORD2VEC_THRES and term not in word:
                similarities.append(word.replace('-', ' '))
        return similarities[:WORD2VEC_MAX]
    except Exception as e:
        logger.error(e)
        return []


def bad_request(e=''):
    """Error handler for 400 error."""
    return make_response(jsonify(error='not found'), 400)


def page_not_found(e=""):
    """Error handler for 404 error."""
    return make_response(jsonify(error="not found"), 404)


def internal_error(e=''):
    """Error handler for 500 error."""
    logger.error('internal error: ' + e)
    return make_response(jsonify(error='internal error'), 500)
