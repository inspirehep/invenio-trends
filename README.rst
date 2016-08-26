..
    This file is part of inspirehep.
    Copyright (C) 2016 CERN.

    inspirehep is free software; you can redistribute it
    and/or modify it under the terms of the GNU General Public License as
    published by the Free Software Foundation; either version 2 of the
    License, or (at your option) any later version.

    inspirehep is distributed in the hope that it will be
    useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
    General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with inspirehep; if not, write to the
    Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
    MA 02111-1307, USA.

    In applying this license, CERN does not
    waive the privileges and immunities granted to it by virtue of its status
    as an Intergovernmental Organization or submit itself to any jurisdiction.

================
 Invenio Trends
================

.. image:: https://img.shields.io/travis/inspirehep/invenio-trends.svg
        :target: https://travis-ci.org/inspirehep/invenio-trends

.. image:: https://img.shields.io/coveralls/inspirehep/invenio-trends.svg
        :target: https://coveralls.io/r/inspirehep/invenio-trends

.. image:: https://img.shields.io/github/tag/inspirehep/invenio-trends.svg
        :target: https://github.com/inspirehep/invenio-trends/releases

.. image:: https://img.shields.io/pypi/dm/invenio-trends.svg
        :target: https://pypi.python.org/pypi/invenio-trends

.. image:: https://img.shields.io/github/license/inspirehep/invenio-trends.svg
        :target: https://github.com/inspirehep/invenio-trends/blob/master/LICENSE
        
.. image:: https://badges.gitter.im/inspirehep/invenio-trends.svg
   :alt: Join the chat at https://gitter.im/inspirehep/invenio-trends
   :target: https://gitter.im/inspirehep/invenio-trends?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge

Invenio module that adds a trends api to the platform.

*This is an experimental developer preview release.*

* Free software: GPLv2 license
* Documentation: https://pythonhosted.org/invenio-trends/

Introduction
------------

This is a summer student project carried out at the [European Organization for Nuclear Research, CERN](http://home.cern). It was supervised by [Eamonn Maguire](https://github.com/eamonnmag) during summer 2016.

The project's goal was to build a trends detection pipeline based on [Inspirehep dataset](), an open source digital library for high energy physics publications developped at (CERN)[].  More than 1.2 millions papers since the 1970s can be browsed either using the [current](http://inspirehep.net) or [future](https://labs.inspirehep.net) interface.

This project suggests an approach to analyze noisy time series based on ngrams extracted from any textual source in near real-time. Although it is mainly designed to process InspireHEP data, it can easily be adjusted and generalized to any other systems based on (elasticsearch)[].

Infrastructure
--------------

Data to be processed should be accessible though a single elasticsearch index (`source_index`) and type (`doc_type`). Specifically, the pipeline use `analysis_field` (`string` type), `date_field` (`strict_date_optional_time||epoch_millis` type or similar) and `id_field` (any type) field to respectively to extract the ngrams, provide temporal details and eventually identify back the original entry. 

As the ngrams extraction requires the use of a custom analyzer, a new index (`index`) dedicated to this task will be created and periodically synchronzied using reindex API. This data bridge can be parametered further using `minimum_date`, `maximum_date` and `filter_script` to fit better the use case.

Text processing
---------------

The ngrams extraction goes through the following filters:

- asciifolding: keep only ascii letters and numbers
- lowercase
- delimiter removal: handle quote and dash-like cases
- mathematic expression removal: strip all latex tags
- words removal: eliminate stopwords and other predefined terms in `stopwords_file`
- stemming: normalize words
- minimum length: keep only words having at least two characters
- generate ngrams: generate words window sizes depending on `minimum_ngram`, `maximum_ngram` and `unigram`
- trim: remove double and border spaces

ETL management
--------------

Refreshing periodically the data can be done using [celery]() (`update_index` task) or using the samle stub below: 

```python
config = {
    'index': 'records-trends',
    'source_index': 'records-hep',
    'doc_type': 'hep',
    'analysis_field': 'abstracts.value',
    'date_field': 'earliest_date',
    'id_field': 'self_recid',
    'tokenizer': 'icu_tokenizer',
    'minimum_date': '2013-02-01',
    'maximum_date': None,
    'filter_script': "d = doc['earliest_date'].date; d.getDayOfYear() != 1",
    'unigram': True,
    'minimum_ngram': 2,
    'maximum_ngram': 3,
    'stopwords_file': '../invenio_trends/etl/stopwords.txt',
}

index_sync = IndexSynchronizer(TRENDS_PARAMS)
index_sync.setup_index()
index_sync.setup_analyzer()
index_sync.setup_mappings()
index_sync.synchronize()
```

Problem definition
------------------



Pipeline
--------

Once the data is correctly available, the trends detection is parameterized using some parameters:
- `reference_date`:
- `granularity`:
- `foreground_window`:
- `background_window`:
- `minimum_frequency_threshold`:
- `smoothing_len`:
- `num_cluster`:
- `num_trends`:

This will to go through the following steps:
- entry retrieval:
- term vectors fetching:
- thresholding:
- histogram retrieval:
- scoring:
- classifying:
- pruning:

Example
-------

```python
reference_date = parse_iso_date('2016-02-26T00:00:00.00')
granularity = Granularity.day
foreground_window = 10
background_window = 365
minimum_frequency_threshold = 5
smoothing_len = 7
num_cluster = 3
num_trends = 1000

td = TrendsDetector(config)

td.run_pipeline()
trends = td.run_pipeline(
    reference_date,
    granularity,
    foreground_window,
    background_window,
    minimum_frequency_threshold,
    smoothing_len,
    num_cluster,
    num_trends
)
// OR
foreground_start = reference_date - foreground_window * gran.value
background_start = reference_date - background_window * gran.value
smoothing_window = np.ones(smoothing_len)
ids = td.interval_ids(foreground_start, reference_date)
all_terms = td.term_vectors(ids)
terms = td.sorting_freq_threshold(all_terms, minimum_frequency_threshold)
hists = td.terms_histograms(terms, background_start, reference_date, gran)
scores = td.hist_scores(hists, foreground_start, smoothing_window)
trending = td.classify_scores(scores, num_cluster)
trends = td.prune_scores(trending, num_trends)
```

Results
-------



Future developments
-------------------


References
----------

- ...
