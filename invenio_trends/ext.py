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
from invenio_trends.cli import trends
from . import config
from .views import blueprint

class InvenioTrends(object):
    """Invenio-Trends extension."""

    def __init__(self, app=None):
        """Extension initialization."""
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Flask application initialization."""
        self.init_config(app)
        app.register_blueprint(blueprint)
        app.extensions['invenio-trends'] = self
        app.cli.add_command(trends, 'trends')

    def init_config(self, app):
        """Initialize configuration."""
        app.config.setdefault(
            'SEARCH_ELASTIC_HOSTS', ['localhost:9200'])

        app.config.setdefault(
            'CACHE_REDIS_URL', 'redis://localhost:6379/0')

        app.config.setdefault(
            'MAGPIE_API_URL', 'http://magpie.inspirehep.net/api')

        for k in dir(config):
            if k.startswith('TRENDS_') or k.startswith('WORD2VEC'):
                app.config.setdefault(k, getattr(config, k))
