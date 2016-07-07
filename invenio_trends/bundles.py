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


"""Bundles for forms used across INSPIRE."""

from invenio_assets import NpmBundle
from invenio_assets.filters import RequireJSFilter

from inspirehep.modules.theme.bundles import js as _js

js = NpmBundle(
    "js/app.js",
    output="gen/invenio_trends.%(version)s.js",
    filters=RequireJSFilter(exclude=[_js]),
    depends="js/**/*.js",
    npm={
        "angular": "~1.5.7"
    }
)

css = NpmBundle(
    "css/app.css",
    filters="cleancss",
    output="gen/invenio_trends.%(version)s.css",
    depends="css/**/*.css",
    npm={
        "bootstrap": "~3.3.6",
        "font-awesome": "~4.6.3",
    }
)
