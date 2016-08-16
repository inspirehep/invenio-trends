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

class IndexSynchronizer:
    """Synchronize given elasticsearch fields into another document with customized analyser."""

    def __init__(self, index, origin_doc_type, analysis_doc_type, analysis_field, date_field, minimum_date=None, maximum_date=None):

        self.index = validate_type(index, str)
        self.origin_doc_type = validate_type(origin_doc_type, str)
        self.analysis_doc_type = validate_type(analysis_doc_type, str)
        self.analysis_fields = validate_type(analysis_field, list)
        self.date_field = validate_type(date_field, str)
        self.minimum_date = validate_type(minimum_date, datetime, optional=True)
        self.maximum_date = validate_type(maximum_date, datetime, optional=True)

        q = Search(index=index, doc_type=origin_doc_type) \
            .filter('exist', fields=analysis_field) \
            .filter('exist', field=date_field)


