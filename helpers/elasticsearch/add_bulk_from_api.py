import os

from dotenv import load_dotenv
import httpx
from elasticsearch import Elasticsearch, helpers

load_dotenv()

BUSINESSES_API_RETRIEVAL_URL = os.getenv("BUSINESSES_API_RETRIEVAL_URL")
ELASTICSEARCH_URL = os.getenv("ELASTICSEARCH_URL")

INDEX_NAME = "businesses"

es = Elasticsearch(ELASTICSEARCH_URL)

def fetch_from_api():
    response = httpx.get(BUSINESSES_API_RETRIEVAL_URL)
    response.raise_for_status()
    return response.json() 

# Generator for streaming documents
def actions():
    for record in fetch_from_api(): 
        yield {
            "_index": INDEX_NAME,
            "_id": record["id"],
            "_source": record
        }

# Bulk insert (streamed in batches)
helpers.bulk(es, actions())
