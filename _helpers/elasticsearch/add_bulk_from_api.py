import os
import httpx
from elasticsearch import helpers

import sys
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from elastic.es_client import es, INDEX_NAME

BUSINESSES_API_RETRIEVAL_URL = os.getenv("BUSINESSES_API_RETRIEVAL_URL")


def fetch_from_api():
    """Fetch businesses data from API endpoint."""
    response = httpx.get(BUSINESSES_API_RETRIEVAL_URL)
    response.raise_for_status()
    return response.json()


# Generator for streaming documents
def actions():
    """Generate Elasticsearch actions for bulk indexing."""
    for record in fetch_from_api():
        yield {"_index": INDEX_NAME, "_id": record["id"], "_source": record}


# Bulk insert (streamed in batches)
helpers.bulk(es, actions())
