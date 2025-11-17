import sys
from pathlib import Path

# Add project root to path for imports from root-level modules
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from logging_config import logger

from elastic.es_client import es, INDEX_NAME

INDEX_CONFIG = {
    "settings": {
        "analysis": {
            "analyzer": {
                "ngram_analyzer": {
                    "tokenizer": "standard",
                    "filter": ["lowercase", "asciifolding", "ngram_filter"],
                },
                "lowercase_analyzer": {
                    "tokenizer": "standard",
                    "filter": ["lowercase", "asciifolding"],
                },
            },
            "normalizer": {
                "lowercase_normalizer": {
                    "type": "custom",
                    "filter": [
                        "lowercase",
                        "asciifolding",
                        "punctuation_filter",
                    ],
                }
            },
            "filter": {
                "ngram_filter": {
                    "type": "ngram",
                    "min_gram": 5,
                    "max_gram": 5,
                },
                "punctuation_filter": {
                    "type": "pattern_replace",
                    "pattern": "[^\\p{L}\\p{N}]",
                    "replacement": "",
                },
            },
        }
    },
    "mappings": {
        "properties": {
            "name": {
                "type": "text",
                "analyzer": "ngram_analyzer",  # partial/autocomplete
                "search_analyzer": "ngram_analyzer",  # match n-grams properly
                "fields": {
                    "keyword": {  # exact match, case- & accent-insensitive
                        "type": "keyword",
                        "normalizer": "lowercase_normalizer",
                    },
                    "full": {  # short/full match, case- & accent-insensitive
                        "type": "text",
                        "analyzer": "lowercase_analyzer",
                    },
                    "fuzzy": {  # fuzzy search, case- & accent-insensitive
                        "type": "text",
                        "analyzer": "lowercase_analyzer",
                    },
                },
            }
        }
    },
}


if __name__ == "__main__":
    try:
        # Check if index already exists
        if not es.indices.exists(index=INDEX_NAME):
            es.indices.create(index=INDEX_NAME, body=INDEX_CONFIG)
            logger.info(f"Index '{INDEX_NAME}' created successfully")
        else:
            logger.info(f"Index '{INDEX_NAME}' already exists")
    except Exception as e:
        logger.error(f"Error creating index: {e}")
