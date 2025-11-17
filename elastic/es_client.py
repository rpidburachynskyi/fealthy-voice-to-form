"""Shared Elasticsearch client and configuration."""

import os
from dotenv import load_dotenv
from elasticsearch import Elasticsearch

load_dotenv()

ELASTICSEARCH_URL = os.getenv("ELASTICSEARCH_URL", "http://elasticsearch:9200")
INDEX_NAME = "businesses"


# Create Elasticsearch client with explicit connection settings
es = Elasticsearch(
    [ELASTICSEARCH_URL],
    request_timeout=30,
    max_retries=3,
    retry_on_timeout=True,
    sniff_on_start=False,
    sniff_on_connection_fail=False,
)
