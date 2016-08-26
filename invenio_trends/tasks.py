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
from datetime import datetime

from celery import shared_task
from redis import StrictRedis

from invenio_trends.analysis.trends_detector import TrendsDetector
from invenio_trends.etl.index_synchronizer import IndexSynchronizer

from .config import CACHE_REDIS_URL, TRENDS_BACKGROUND_WINDOW, \
    TRENDS_FOREGROUND_WINDOW, TRENDS_GRANULARITY, \
    TRENDS_MINIMUM_FREQUENCY_THRESHOLD, TRENDS_NUM, TRENDS_NUM_CLUSTER, \
    TRENDS_PARAMS, TRENDS_REDIS_KEY, TRENDS_SMOOTHING_LEN

logger = logging.getLogger(__name__)
redis = StrictRedis.from_url(CACHE_REDIS_URL)


@shared_task(ignore_result=True)
def update_index():
    """Synchronize index to refresh all new entries into the trends index."""
    logging.info('updating index')
    index_sync = IndexSynchronizer(TRENDS_PARAMS)
    index_sync.setup_index()
    index_sync.setup_analyzer()
    index_sync.setup_mappings()
    index_sync.synchronize()


@shared_task(ignore_result=True)
def update_trends():
    """Compute trends for the current day and cache them."""
    logging.info('updating trends')
    td = TrendsDetector(TRENDS_PARAMS)
    trends = td.run_pipeline(
        reference_date=datetime.now(),
        granularity=TRENDS_GRANULARITY,
        foreground_window=TRENDS_FOREGROUND_WINDOW,
        background_window=TRENDS_BACKGROUND_WINDOW,
        minimum_frequency_threshold=TRENDS_MINIMUM_FREQUENCY_THRESHOLD,
        smoothing_len=TRENDS_SMOOTHING_LEN,
        num_cluster=TRENDS_NUM_CLUSTER,
        num_trends=TRENDS_NUM
    )
    if not len(trends):
        return
    terms, dates = zip(*[(term, date) for term, stats, (date, score) in trends])
    logger.info('trends detected: %s', terms)
    mapping = {
        'terms': ','.join(terms),
        'start': min(dates[0]).isoformat(),
        'end': max(dates[0]).isoformat(),
        'granularity': TRENDS_GRANULARITY.name
    }
    assert(1, redis.hmset(TRENDS_REDIS_KEY, mapping))
