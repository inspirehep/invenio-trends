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

"""CLI Commands for Trends"""

import click
from flask_cli import with_appcontext


@click.group()
def trends():
    """Trends management commands."""


@trends.command(name='initialise')
@with_appcontext
def initialise_trends():
    """Initialise the index (also copies from source index)."""
    from tasks import update_index
    update_index()


@trends.command(name='compute')
@with_appcontext
def compute_trends():
    """Calculates the trends."""
    from tasks import update_trends
    update_trends()
