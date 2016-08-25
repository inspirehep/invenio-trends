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

"""Tasks to be periodically scheduled."""

import logging

from celery import shared_task

from .config import TRENDS_PARAMS
from .index_synchronizer import IndexSynchronizer

logger = logging.getLogger(__name__)


@shared_task(ignore_result=True)
def index_synchronizer():
    """Synchronize index task."""
    logging.info('running index_synchronizer task')
    index_sync = IndexSynchronizer(TRENDS_PARAMS)
    index_sync.setup_analyzer()
    index_sync.setup_mappings()
    index_sync.synchronize()


GET invenio-trends-tests/
{
    "dest": {
		"index": "destination",
		"type": "dst"
	},
	"source": {
		"index": "source",
		"_source": ["src_ana", "src_date"],
		"type": "src",
		"query": {
			"bool": {
				"filter": [{
					"exists": [{
						"field": "src_ana"
					}, {
						"field": "src_date"
					}]
				}, {
					"range": {
						"src_date": {
							"gt": "2015-03-01",
							"lte": "2015-04-01"
						}
					}
				}, {
					"script": {
						"script": "d = doc[\"src_date\"].date; d.getDayOfMonth() != 3"
					}
				}]
			}
		}
	},
	"script": {
		"inline": "ctx._source.dst_ana = ctx._source.remove(\"src_ana\");ctx._source.dst_date = ctx._source.remove(\"src_date\");"
	}
}
