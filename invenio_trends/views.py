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

from __future__ import absolute_import, print_function

import logging

from flask import Blueprint, jsonify, make_response
from invenio_search import RecordsSearch

logger = logging.getLogger(__name__)


blueprint = Blueprint(
    'invenio_trends',
    __name__,
    template_folder='templates',
    static_folder='static',
)


# @blueprint.route("/<int:recid>/") recid
@blueprint.route("/trends")
def index():
    """Basic view."""
    return "hello world"


@blueprint.route("/trends/search/<string:terms>/")
def search(terms):
    """."""
    query = RecordsSearch(index="records-hep") \
        .query("match", abstract=terms) \
        .fields("earliest_date") \
        .sort("earliest_date")[:10000]  # TODO : better

    res = query.execute()

    if not res.success():
        return internal_error("query error")

    logger.info("search completed in %dms" % res.took)
    logger.info("search returned %d elements" % res.hits.total)
    max_scores = res.hits.max_score

    buckets = []

    for elem in res:
        id = elem.meta.id
        dates = elem.earliest_date

        try:
            buckets.append({"id": id, "date": dates[0]})
        except:
            pass

    ret = [
        {
            "key": terms,
            "values": buckets
        }
    ]

    return jsonify(ret)


@blueprint.route("/trends/hist/<string:terms>/")
def hist(terms):
    """."""
    s = RecordsSearch(index="records-hep")[0:0].query("match", abstract=terms)

    s.aggs.bucket('weekly', 'date_histogram', field='earliest_date', interval='week', format='date_optional_time')

    res = s.execute()

    if not res.success():
        return internal_error("query_error")

    logger.info("search completed in %dms" % res.took)
    logger.info("search returned %d elements" % res.hits.total)

    buckets = []

    for elem in res.aggregations.weekly.buckets:
        buckets.append({"x": elem.key_as_string, "y": elem.doc_count})

    ret = [
        {
            "key": terms,
            "values": buckets
        }
    ]

    return jsonify(ret)


def unauthorized(e=""):
    """Error handler to show a 401.html page in case of a 401 error."""
    return make_response(jsonify(error="unauthorized"), 401)


def insufficient_permissions(e=""):
    """Error handler to show a 403.html page in case of a 403 error."""
    return make_response(jsonify(error="insufficient_permissions"), 403)


def page_not_found(e=""):
    """Error handler to show a 404.html page in case of a 404 error."""
    return make_response(jsonify(error="not found"), 404)


def internal_error(e=""):
    """Error handler to show a 500.html page in case of a 500 error."""
    mes = "internal error: " + e
    logger.error(mes)
    return make_response(jsonify(error=mes), 500)

