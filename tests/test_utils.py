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

"""Utils tests."""

from datetime import datetime

import numpy as np
from invenio_trends.utils import parse_iso_date


def test_parse_iso_date():
    date = parse_iso_date('2015-02-05T08:47:22.01Z')
    assert date == parse_iso_date('2015-02-05T08:47:22.01')
    assert date.year == 2015
    assert date.month == 2
    assert date.day == 5
    assert date.hour == 8
    assert date.minute == 47
    assert date.second == 22
    assert date.microsecond == 10000


def test_parse_iso_date_loop():
    date = datetime(2016, 4, 8, 9, 48, 23, 20000)
    assert date == parse_iso_date(date.isoformat())
