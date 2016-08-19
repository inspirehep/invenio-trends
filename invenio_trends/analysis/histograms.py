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

"""Histograms utility."""

from elasticsearch_dsl import Search
from utils import parse_iso_date
import numpy as np


def unzip_date_value(date_value_list):
    """Transform a list of dict into two ndarray containing dates and values."""
    x, y = zip(*[(parse_iso_date(elem.key_as_string), elem.doc_count) for elem in date_value_list])
    return np.array(x), np.array(y)


def date_histogram(index, start, end, granularity, date_field, analysis_field, term=None):
    """Retrieve the date histogram of all entries or a single term is given"""
    q = Search(index=index)[0:0] \
        .filter('range', **{date_field: {'gt': start, 'lte': end}})
    if term != None:
        q = q.query('match_phrase', **{analysis_field: term})
    q.aggs.bucket(
        'hist',
        'date_histogram',
        field=date_field,
        interval=granularity.name,
        format='date_optional_time'
    )
    return unzip_date_value(q.execute().aggregations.hist.buckets)
