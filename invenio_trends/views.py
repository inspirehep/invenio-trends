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

from .config import TRENDS_ENDPOINT, TRENDS_PARAMS
from .analysis.trends_detector import TrendsDetector
from flask import Blueprint, request, jsonify, make_response

import logging


logger = logging.getLogger(__name__)

blueprint = Blueprint(
    'invenio_trends',
    __name__,
    url_prefix=TRENDS_ENDPOINT
)


# @blueprint.route("/<int:recid>/") recid
@blueprint.route("/")
def index():
    """Basic view."""
    return "hello world"


#@blueprint.route("/search/<string:terms>/")
def search(terms):
    """."""
    json = request.json
    td = TrendsDetector(TRENDS_PARAMS)
    #td.date_histogram()



    print(json)
    return jsonify(json)


#@blueprint.route("/emerging")
def emerging_trends():
    return jsonify({})


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

