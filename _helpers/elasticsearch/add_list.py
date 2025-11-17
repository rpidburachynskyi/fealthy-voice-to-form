import random
from datetime import datetime
from elasticsearch import helpers

import sys
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from elastic.es_client import es, INDEX_NAME


def generate_slug(name):
    """Generate a slug from business name."""
    return (
        name.lower()
        .replace(" ", "-")
        .replace("'", "")
        .replace(".", "")
        .replace("'", "")
    )


def add_businesses_to_index(business_list):
    """Add list of businesses to Elasticsearch index."""

    def actions():
        """Generate Elasticsearch actions for bulk indexing."""
        for i, business in enumerate(business_list, 1):
            # Extract nameUk and nameEn from list
            name_uk = business[0]
            name_en = business[1]

            # Generate random ID
            business_id = random.randint(30000, 99999)

            # Generate slug from Ukrainian name
            slug = generate_slug(name_uk)

            # Current timestamp
            now = datetime.now().isoformat() + "Z"

            yield {
                "_index": INDEX_NAME,
                "_id": str(business_id),
                "_source": {
                    "id": business_id,
                    "createdAt": now,
                    "updatedAt": now,
                    "name": name_uk,
                    "type": "commerce",
                    "slug": slug,
                    "_slug": "slug",
                    "nameUk": name_uk,
                    "_nameUk": "nameUk",
                    "nameEn": name_en,
                    "_nameEn": "nameEn",
                },
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
    LIST_OF_BUSINESSES = [
        ["Ябко", "Jabko"],
        ["Que Pasa", "Que Pasa"],
        ["1001 + 1 NIGHT RESTAURANT", "1001 + 1 NIGHT RESTAURANT"],
        ["Китайський привіт", "China Hi"],
        ["ФОКСТРОТ", "Foxtrot"],
        ["Техно Світ", "Techno Svit"],
        ["Сушія", "Sushiya"],
        ["Allo", "Allo"],
        ["Starbucks", "Starbucks"],
        ["Мобілочка", "Mobilochka"],
        ["Papa John's", "Papa John's"],
        ["Червоний мак", "Chervonyi Mak"],
        ["Di Napoli", "Di Napoli"],
        ["ТехноПарк", "TechnoPark"],
        ["Coffee Time", "Coffee Time"],
        # ["Domino's Pizza", "Domino's Pizza"],
        ["Гаджетаріум", "Gadgetarium"],
        ["ТехноМаг", "TechnoMag"],
        ["Кавова Хмаринка", "Coffee Cloud"],
        ["Sushi 3303", "Sushi 3303"],
        ["Гаджет Зона", "Gadget Zone"],
        ["Чорний кіт", "Chornyi Kit"],
        ["ТехноLand", "TechnoLand"],
        ["La Varena", "La Varena"],
        ["Mediterre", "Mediterre"],
        ["Техносито", "Technosito"],
        ["Кавова Перерва", "Coffee Break"],
        ["Зелене яблуко", "Zelene Yabluko"],
        ["Япона дім", "Japona dim"],
        ["QuickyTech", "QuickyTech"],
        ["Сімпсон", "Simpson"],
        ["Pizza King", "Pizza King"],
        ["Гaджетик", "Gadgetik"],
        ["Solodkyi Kutok", "Solodkyi Kutok"],
        ["ТехноХаус", "TechnoHouse"],
        ["Italian Courtyard", "Italian Courtyard"],
        ["BooKiss", "BooKiss"],
        ["WOK", "WOK"],
        ["Техномаркет", "Technomarket"],
        ["China Лавка", "China Lavka"],
        ["екпеліарМусс", "ekspeliarMuss"],
        ["ГаджетМолл", "GadgetMall"],
        ["Red Gragon", "Red Gragon"],
        ["Apple Room", "Apple Room"],
    ]

    add_businesses_to_index(LIST_OF_BUSINESSES)
