#!/usr/bin/env bash
curl --silent --request DELETE 'http://localhost:9200/test?pretty'
curl --silent --request PUT 'http://localhost:9200/test?pretty' --data @settings.json
curl --silent --request POST 'http://localhost:9200/_reindex?pretty' --data '{"source": {"index": "location-en"}, "dest": {"index": "test"}}'
