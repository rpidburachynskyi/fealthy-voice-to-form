import json
import sys
from pathlib import Path
from elasticsearch import helpers

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from elastic.es_client import es, INDEX_NAME

INPUT_FILE = Path(__file__).parent / "api_businesses.json"


def load_from_json():
    """Load businesses data from JSON file."""
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


# Generator for streaming documents
def actions():
    """Generate Elasticsearch actions for bulk indexing."""
    for record in load_from_json():
        yield {"_index": INDEX_NAME, "_id": record["id"], "_source": record}


if __name__ == "__main__":
    try:
        result = helpers.bulk(es, actions())
        print(f"Successfully added {result[0]} businesses to index")
    except Exception as e:
        print(f"Error adding businesses: {e}")
