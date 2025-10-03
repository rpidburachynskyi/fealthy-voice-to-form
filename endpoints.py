import os
import logging
from collections import defaultdict

from dotenv import load_dotenv
import httpx

logger = logging.getLogger(__name__)


load_dotenv()
ENDPOINT_BEARER_TOKEN = os.getenv("ENDPOINT_BEARER_TOKEN")
ENDPOINT_URL = os.getenv("ENDPOINT_URL")

HEADERS = {
    "accept": "*/*",
    "Authorization": f"Bearer {ENDPOINT_BEARER_TOKEN}"
}


async def get_user_data(id, user_data_type):
    url = f"{ENDPOINT_URL}users/{id}/{user_data_type}"

    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.get(url, headers=HEADERS)

        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Error while getting {user_data_type} {response.status_code}: {response.text}")
            return {}


async def get_user_categories(id):
    user_data_type = 'categories'
    api_categories = await get_user_data(id, user_data_type)
    try:
        # Dictionary to store the structured output
        category_dict = defaultdict(list)

        # Create a mapping of category IDs to names
        id_to_name = {item["id"]: item["name"] for item in api_categories}

        # Organize data by parent category
        for item in api_categories:
            if "parentId" in item:
                parent_name = id_to_name.get(item["parentId"], f"Unknown ({item['parentId']})")
                category_dict[parent_name].append((item["id"], item["name"]))

        return dict(category_dict), api_categories
    except Exception as e:
        logger.error(f"Error while getting {user_data_type}: {e}")
        return {}, api_categories


async def get_user_labels(id):
    user_data_type='labels'
    user_data = await get_user_data(id, user_data_type)
    
    #TODO return 'user_data' instead of 'dummy_user_data' when API will be ready
    dummy_user_data = [
    {"id":1002,"name":"Groceries"},
    {"id":1003,"name":"Продукти"},
    {"id":1004,"name":"Electronics"},
    {"id":1005,"name":"Електроніка"},
    {"id":1006,"name":"Clothing"},
    {"id":1007,"name":"Одяг"},
    {"id":1008,"name":"Transport"},
    {"id":1009,"name":"Транспорт"},
    {"id":1010,"name":"Fuel"},
    {"id":1011,"name":"Паливо"},
    {"id":1012,"name":"Internet"},
    {"id":1013,"name":"Інтернет"},
    {"id":1014,"name":"Utilities"},
    {"id":1015,"name":"Комунальні послуги"},
    {"id":1016,"name":"Rent"},
    {"id":1017,"name":"Оренда"},
    {"id":1018,"name":"Healthcare"},
    {"id":1019,"name":"Охорона здоров'я"},
    {"id":1020,"name":"Insurance"},
    {"id":1021,"name":"Страхування"},
    {"id":1022,"name":"Entertainment"},
    {"id":1023,"name":"Розваги"},
    {"id":1024,"name":"Restaurants"},
    {"id":1025,"name":"Ресторани"},
    {"id":1026,"name":"Fast Food"},
    {"id":1027,"name":"Фаст-фуд"},
    {"id":1028,"name":"Coffee"},
    {"id":1029,"name":"Кава"},
    {"id":1030,"name":"Education"},
    {"id":1031,"name":"Освіта"},
    {"id":1032,"name":"Books"},
    {"id":1033,"name":"Книги"},
    {"id":1034,"name":"Gifts"},
    {"id":1035,"name":"Подарунки"},
    {"id":1036,"name":"Charity"},
    {"id":1037,"name":"Благодійність"},
    {"id":1038,"name":"Pets"},
    {"id":1039,"name":"Домашні тварини"},
    {"id":1040,"name":"Beauty"},
    {"id":1041,"name":"Косметика"},
    {"id":1042,"name":"Hobbies"},
    {"id":1043,"name":"Хобі"},
    {"id":1044,"name":"Subscriptions"},
    {"id":1045,"name":"Підписки"},
    {"id":1046,"name":"Home Improvement"},
    {"id":1047,"name":"Ремонт дому"},
    {"id":1048,"name":"Work"},
    {"id":1049,"name":"Робота"},
    {"id":1050,"name":"Travel"},
    {"id":1051,"name":"Подорожі"},
    {"id":1052,"name":"Friends"},
    {"id":1053,"name":"Друзі"},
    {"id":1054,"name":"Family"},
    {"id":1055,"name":"Сім'я"},
    {"id":1056,"name":"Loans"},
    {"id":1057,"name":"Кредити"},
    {"id":1058,"name":"Taxes"},
    {"id":1059,"name":"Податки"},
    ]
    
    return dummy_user_data


async def get_user_accounts(id):
    user_data_type='accounts'
    user_data = await get_user_data(id, user_data_type)

    #TODO return 'user_data' instead of 'dummy_user_data' when API will be ready
    dummy_user_data = [
    {
        "id": 52,
        "name": "Чорна картка",
        "provider": {
            "id": 1,
            "name": "Monobank",
            "nameEn": "Monobank"
        }
    },
    {
        "id": 55,
        "name": "Геніальна",
        "provider": {
            "id": 1,
            "name": "Аваль",
            "nameEn": "Aval"
        }
    },
    {
        "id": 152,
        "name": "Для виплат",
        "provider": {
            "id": 1,
            "name": "Аваль",
            "nameEn": "Aval"
        }
    },
    ]
    
    return dummy_user_data
