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

TRENDS_ENDPOINT = "api/trends"

TRENDS_SOURCE = {
    'index': 'records-hep',
    'origin_doc_type': 'hep',
    'analysis_doc_type': 'trends-analysis',
    'analysis_field': 'abstracts.value',
    'date_field': 'earliest_date',
    'minimum_date': '2013-02-01',
    'maximum_date': None
}
