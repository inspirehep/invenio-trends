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

from datetime import datetime

from elasticsearch_dsl import Search

from .utils import DatetimeConverter, print_iso_date

from .config import TRENDS_ENDPOINT, TRENDS_PARAMS, WORD2VEC_TIMEOUT, WORD2VEC_URL, WORD2VEC_THRES, WORD2VEC_MAX, \
    MAGPIE_API_URL
from .analysis.trends_detector import TrendsDetector
from .analysis.granularity import Granularity
from flask import Blueprint, jsonify, make_response

import requests as r
import logging


logger = logging.getLogger(__name__)

def register_converters(state):
    state.app.url_map.converters['datetime'] = DatetimeConverter

blueprint = Blueprint(
    'invenio_trends',
    __name__,
    url_prefix=TRENDS_ENDPOINT,
)
blueprint.record_once(register_converters)


@blueprint.route("/granularities")
def granularities():
    return jsonify([gran for gran in Granularity.__members__])

@blueprint.route("/search/<string:query>/")
@blueprint.route("/search/<string:query>/<string:start>")
@blueprint.route("/search/<string:query>/<string:start>/<string:end>")
@blueprint.route("/search/<string:query>/<datetime:start>/<string:end>/<string:gran>")
def search(query, start=None, end=None, gran=None):
    """."""
    if gran not in Granularity.__members__:
        gran = 'week'
    gran = Granularity[gran]

    terms = [t.strip() for t in query.split(',') if len(t.strip())]
    if not len(terms):
        return bad_request("no terms")

    td = TrendsDetector(TRENDS_PARAMS)
    minValue = 0
    maxValue = 0
    minDate = end if end else datetime.max
    maxDate = start if start else datetime.min

    all_terms = []
    related_terms = {}
    for term in terms:
        similarities = word2vec(term)
        related_terms[term] = similarities
        all_terms.append(term)
        all_terms.extend(similarities)

    data = []
    for term in all_terms:
        dates, values = td.date_histogram(start, end, gran, term)
        if len(values):
            minValue = min(minValue, min(values))
            maxValue = max(maxValue, max(values))
            minDate = min(minDate, min(dates))
            maxDate = max(maxDate, max(dates))
        series = [{'date': print_iso_date(date), 'value': value} for date, value in zip(dates, values)]
        data.append({'name': term, 'series': series})

    ret = {
        'stats': {
            'minValue': minValue,
            'maxValue': maxValue,
            'minDate': print_iso_date(minDate),
            'maxDate': print_iso_date(maxDate)
        },
        'related_terms': related_terms,
        'data': data
    }

    return jsonify(ret)


@blueprint.route("/emerging")
def emerging_trends():


    return jsonify({})


def min_data_date():
    q = Search(using=self.client, index=self.index) \
        .fields(['']) \
        .filter('exists', field=self.analysis_field) \
        .filter('range', **{self.date_field: {'gt': start, 'lte': end}})
    return [elem.meta.id for elem in q.scan()]

def word2vec(term):
    try:
        data = {'corpus': 'keywords', 'positive': [term.replace(' ', '')], 'negative': []}
        res = r.post(MAGPIE_API_URL + '/word2vec', json=data, timeout=WORD2VEC_TIMEOUT).json()
        similarities = []
        for word, score in sorted(res['vector'], key=lambda e: -e[1])[:WORD2VEC_MAX]:
            if score >= WORD2VEC_THRES and term not in word:
                similarities.append(word.replace('-', ' '))
        return similarities
    except Exception as e:
        logger.error(e)
        return []


def bad_request(e=""):
    """Error handler for 400 error."""
    return make_response(jsonify(error="not found"), 400)


def internal_error(e=""):
    """Error handler for 500 error."""
    logger.error("internal error: " + e)
    return make_response(jsonify(error="internal error"), 500)

