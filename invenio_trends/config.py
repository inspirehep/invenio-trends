TRENDS_ENDPOINT = "api/trends"

TRENDS_SOURCE = {
    'index': 'records-hep',
    'origin_doc_type': 'hep',
    'analysis_doc_type': 'trends-analysis',
    'analysis_field': [
        'abstracts.value'
    ],
    'date_field': 'earliest_date',
    'minimum_date': '2013-02-01',
    'maximum_date': None
}
