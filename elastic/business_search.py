from .es_client import es, INDEX_NAME

FUZINESS_SETTINGS = {6: 2, 5: 1, 4: 0}  # length of the word : fuzziness value


def calculate_fuzziness(text: str) -> int:
    """Calculate fuzziness based on text length using FUZINESS_SETTINGS."""
    text_length = len(text)

    # Find the appropriate fuzziness value based on text length
    for min_length in sorted(FUZINESS_SETTINGS.keys(), reverse=True):
        if text_length >= min_length:
            return FUZINESS_SETTINGS[min_length]

    return 0


def search_business(text: str):
    """Search for businesses in the index."""
    fuzziness = calculate_fuzziness(text)

    search_body = {
        "query": {
            "bool": {
                "should": [
                    {
                        "match": {  # n-gram / partial match
                            "name": {"query": text, "operator": "or"}
                        }
                    },
                    {
                        "match_phrase": {  # exact / short-word match
                            "name.full": {
                                "query": text,
                            }
                        }
                    },
                    {
                        "match": {  # fuzzy match on keyword field
                            "name.keyword": {
                                "query": text,
                                "fuzziness": fuzziness,
                            }
                        }
                    },
                ],
                "minimum_should_match": 1,
            }
        }
    }
    response = es.search(index=INDEX_NAME, body=search_body)
    return response


def search_businesses(input_set: set):
    """Search for businesses using multiple search terms and return unique matches."""
    matches = []
    for match in input_set:
        response = search_business(match)
        if response["hits"]["total"]["value"] > 0:
            for hit in response["hits"]["hits"]:
                match_data = {
                    "id": hit["_source"]["id"],
                    "name": hit["_source"]["name"],
                    "score": hit["_score"],
                }
                # Avoid duplicates based on id
                if not any(m["id"] == match_data["id"] for m in matches):
                    matches.append(match_data)

    return matches
