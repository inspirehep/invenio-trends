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

from invenio_trends.utils import DatetimeConverter

from .config import TRENDS_ENDPOINT, TRENDS_PARAMS
from .analysis.trends_detector import TrendsDetector
from .analysis.granularity import Granularity
from flask import Blueprint, jsonify, make_response

import logging


logger = logging.getLogger(__name__)

def register_converter(state):
    state.app.url_map.converters['datetime'] = DatetimeConverter

blueprint = Blueprint(
    'invenio_trends',
    __name__,
    url_prefix=TRENDS_ENDPOINT,
)
blueprint.record_once(register_converter)


ret = {
    'stats': {
        'minValue': 0,
        'maxValue': 67,
        'minDate': '2014-03-01',
        'maxDate': '2014-12-06'
    },
    'related_terms': {
        'Quantum chromodynamics': ["QCD"],
        'plasma physics': [],
        'lasers': []
    },
    'data': [{
        'name': 'Quantum xs',
        'series': [
            {'date': '2014-03-01', 'value': 0},
            {'date': '2014-04-01', 'value': 0},
            {'date': '2014-05-01', 'value': 2},
            {'date': '2014-06-01', 'value': 5},
            {'date': '2014-07-01', 'value': 11},
            {'date': '2014-08-01', 'value': 11},
            {'date': '2014-09-01', 'value': 27},
            {'date': '2014-10-01', 'value': 27},
            {'date': '2014-11-01', 'value': 47},
            {'date': '2014-12-01', 'value': 57}
        ]
    }, {
        'name': 'plasma physics',
        'series': [
            {'date': '2014-03-01', 'value': 0},
            {'date': '2014-04-01', 'value': 0},
            {'date': '2014-05-01', 'value': 2},
            {'date': '2014-06-01', 'value': 5},
            {'date': '2014-07-01', 'value': 1},
            {'date': '2014-08-01', 'value': 7},
            {'date': '2014-09-01', 'value': 17},
            {'date': '2014-10-01', 'value': 27},
            {'date': '2014-11-01', 'value': 47},
            {'date': '2014-12-01', 'value': 49}
        ]
    },
        {
            'name': 'lasers',
            'series': [
                {'date': '2014-03-01', 'value': 0},
                {'date': '2014-04-02', 'value': 1},
                {'date': '2014-05-05', 'value': 1},
                {'date': '2014-06-27', 'value': 0},
                {'date': '2014-07-06', 'value': 0},
                {'date': '2014-08-06', 'value': 0},
                {'date': '2014-09-06', 'value': 3},
                {'date': '2014-10-06', 'value': 5},
                {'date': '2014-11-06', 'value': 9},
                {'date': '2014-12-06', 'value': 19}
            ]
        },
        {
            'name': 'QCD',
            'series': [
                {'date': '2014-03-01', 'value': 0},
                {'date': '2014-04-06', 'value': 0},
                {'date': '2014-05-06', 'value': 2},
                {'date': '2014-06-06', 'value': 5},
                {'date': '2014-07-06', 'value': 11},
                {'date': '2014-08-06', 'value': 7},
                {'date': '2014-09-06', 'value': 17},
                {'date': '2014-10-06', 'value': 17},
                {'date': '2014-11-06', 'value': 47},
                {'date': '2014-12-06', 'value': 37}
            ]
        }]
}


@blueprint.route("/search/<string:query>/")
@blueprint.route("/search/<string:query>/<string:start>")
@blueprint.route("/search/<string:query>/<string:start>/<string:end>")
@blueprint.route("/search/<string:query>/<datetime:start>/<string:end>/<string:gran>")
def search(query, start=None, end=None, gran=None):
    """."""
    if not start:
        start = ''
    if not end:
        end = ''
    if gran not in Granularity.__members__:
        gran = 'day'
    gran = Granularity[gran]

    terms = [t.strip() for t in query.split(',') if len(t.strip())]
    if not len(terms):
        return bad_request("no terms")

    td = TrendsDetector(TRENDS_PARAMS)

    print(terms)
    minValue = 0
    maxValue = 0
    minDate = 0#datetime.now
    for term in terms:
        # td.date_histogram(start, end, gran, term)
        pass



    print(ret)
    return jsonify(ret)


@blueprint.route("/emerging")
def emerging_trends():
    return jsonify(ret)


def bad_request(e=""):
    """Error handler for 400 error."""
    return make_response(jsonify(error="not found"), 400)


def internal_error(e=""):
    """Error handler for 500 error."""
    logger.error("internal error: " + e)
    return make_response(jsonify(error="internal error"), 500)

