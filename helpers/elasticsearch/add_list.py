import os
import random
from datetime import datetime
from dotenv import load_dotenv
from elasticsearch import Elasticsearch, helpers

load_dotenv()

ELASTICSEARCH_URL = os.getenv("ELASTICSEARCH_URL")
INDEX_NAME = "businesses"

es = Elasticsearch(ELASTICSEARCH_URL)

def generate_slug(name):
    """Generate a slug from business name"""
    return name.lower().replace(" ", "-").replace("'", "").replace(".", "").replace("'", "")

def add_businesses_to_index(business_list):
    """Add list of businesses to Elasticsearch index"""
    
    def actions():
        for i, business_name in enumerate(business_list, 1):
            # Generate random ID
            business_id = random.randint(30000, 99999)
            
            # Generate slug from name
            slug = generate_slug(business_name)
            
            # Current timestamp
            now = datetime.now().isoformat() + "Z"
            
            yield {
                "_index": INDEX_NAME,
                "_id": str(business_id),
                "_source": {
                    "id": business_id,
                    "createdAt": now,
                    "updatedAt": now,
                    "name": business_name,
                    "type": "commerce",
                    "slug": slug,
                    "_slug": "slug"
                }
            }
    
    # Bulk insert
    try:
        result = helpers.bulk(es, actions())
        print(f"Successfully added {result[0]} businesses to index")
        return result
    except Exception as e:
        print(f"Error adding businesses: {e}")
        return None


if __name__ == "__main__":
    LIST_OF_BUSINESSES = ["ShoCo.", "Сімі", "Apple Room", "Червоний мак"]
    
    add_businesses_to_index(LIST_OF_BUSINESSES)
