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
from flask import current_app
from flask.ext.cli import with_appcontext
from redis import StrictRedis
from werkzeug.local import LocalProxy

from invenio_trends.analysis.trends_detector import TrendsDetector
from invenio_trends.etl.index_synchronizer import IndexSynchronizer

logger = logging.getLogger(__name__)


def get_config():
    return current_app.config


@shared_task(ignore_result=True)
@with_appcontext
def update_index():
    """Synchronize index to refresh all new entries into the trends index."""
    logging.info('updating index')
    index_sync = IndexSynchronizer()
    index_sync.setup_index()
    index_sync.setup_analyzer()
    index_sync.setup_mappings()
    index_sync.synchronize()


@shared_task(ignore_result=True)
@with_appcontext
def update_trends():
    """Compute trends for the current day and cache them."""

    config = LocalProxy(get_config)

    redis = StrictRedis.from_url(config['CACHE_REDIS_URL'])

    logging.info('updating trends')
    td = TrendsDetector()
    trends = td.run_pipeline(
        reference_date=datetime.now(),
        granularity=config['TRENDS_GRANULARITY'],
        foreground_window=config['TRENDS_FOREGROUND_WINDOW'],
        background_window=config['TRENDS_BACKGROUND_WINDOW'],
        minimum_frequency_threshold=config['TRENDS_MINIMUM_FREQUENCY_THRESHOLD'],
        smoothing_len=config['TRENDS_SMOOTHING_LEN'],
        num_cluster=config['TRENDS_NUM_CLUSTER'],
        num_trends=config['TRENDS_NUM']
    )
    if not len(trends):
        return
    terms, dates = zip(*[(term, date) for term, stats, (date, score) in trends])

    logger.info('trends detected: %s', terms)
    mapping = {
        'terms': ','.join(terms),
        'start': min(dates[0]).isoformat(),
        'end': max(dates[0]).isoformat(),
        'granularity': config['TRENDS_GRANULARITY'].name
    }
    assert (1, redis.hmset(config['TRENDS_REDIS_KEY'], mapping))
