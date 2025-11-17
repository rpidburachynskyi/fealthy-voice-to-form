import os
from collections import defaultdict

from dotenv import load_dotenv
import httpx

from logging_config import logger

# Fake user data for demo purposes - to be removed in production
from _helpers.api_demo_data.categories import DEMO_CATEGORIES
from _helpers.api_demo_data.labels import DEMO_LABELS
from _helpers.api_demo_data.accounts import DEMO_ACCOUNTS


load_dotenv()
ENDPOINT_BEARER_TOKEN = os.getenv("ENDPOINT_BEARER_TOKEN")
ENDPOINT_URL = os.getenv("ENDPOINT_URL")

HEADERS = {"accept": "*/*", "Authorization": f"Bearer {ENDPOINT_BEARER_TOKEN}"}


async def get_user_data(id, user_data_type):
    """Fetch user data from the API endpoint."""
    url = f"{ENDPOINT_URL}users/{id}/{user_data_type}"

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.get(url, headers=HEADERS)

            if response.status_code == 200:
                return response.json()
            else:
                logger.error(
                    f"Error while getting {user_data_type} {response.status_code}: {response.text}"
                )
                return []
    except Exception as e:
        logger.error(
            f"Error while getting {user_data_type} for user {id}: {e}"
        )
        return []


async def get_user_categories(id):
    """Fetch and structure user categories data."""
    # TODO: In production, API should be used to get categories data
    # api_categories = await get_user_data(id, user_data_type="categories")
    api_categories = DEMO_CATEGORIES

    try:
        # Dictionary to store the structured output
        category_dict = defaultdict(list)

        # Create a mapping of category IDs to names
        id_to_name = {item["id"]: item["name"] for item in api_categories}

        # Organize data by parent category
        for item in api_categories:
            if "parentId" in item:
                parent_name = id_to_name.get(
                    item["parentId"], f"Unknown ({item['parentId']})"
                )
                category_dict[parent_name].append((item["id"], item["name"]))

        return dict(category_dict), api_categories
    except Exception as e:
        logger.error(f"Error while getting categories: {e}")
        return {}, api_categories


async def get_user_labels(id):
    """Fetch user labels data."""
    # TODO: In production, API should be used to get labels data
    # api_labels = await get_user_data(id, user_data_type="labels")
    api_labels = DEMO_LABELS
    return api_labels


async def get_user_accounts(id):
    """Fetch user accounts data."""
    # TODO: In production, API should be used to get accounts data
    # api_accounts = await get_user_data(id, user_data_type='accounts')
    api_accounts = DEMO_ACCOUNTS
    return api_accounts
