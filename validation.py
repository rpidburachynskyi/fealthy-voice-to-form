import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def validate_and_merge_json(response_jsons: tuple):
    output_json = {}
    for response_json in response_jsons:
        try:
            response_json = response_json.replace('None', 'null').replace("'", '"')
            parsed_obj = json.loads(response_json)
            output_json.update(parsed_obj)
        except json.JSONDecodeError as e:
            logger.error(f'Error: "{response_json}"is not valid JSON.')
        except Exception as e:
            logger.error(f'Code error: {e}')
    return output_json


def validate_category(response, target_id):
    if target_id is None:
        return None

    target_item = next((item for item in response if item['id'] == target_id), None)
    if target_item and 'parentId' in target_item:
        return target_id
    return None


def validate_account(response, target_id):
    if target_id is None:
        return None

    return target_id if any(item['id'] == target_id for item in response) else None


def validate_labels(response, target):
    return [id for id in target if any(item['id'] == id for item in response)]


def validate_response(response_json, api_categories, api_labels, api_accounts):
    validated = {}

    # accountId
    account_id = response_json.get("accountId")
    validated["accountId"] = account_id if isinstance(account_id, int) and account_id >= 0 else None
    validated["accountId"] = validate_account(api_accounts, validated["accountId"])

    # amount
    amount = response_json.get("amount")
    validated["amount"] = amount if isinstance(amount, (int, float)) and amount > 0 else 0.0

    # categoryId
    category_id = response_json.get("categoryId")
    validated["categoryId"] = category_id if isinstance(category_id, int) and category_id >= 0 else None
    validated["categoryId"] = validate_category(api_categories, validated["categoryId"] )

    # currency
    currency = response_json.get("currency")
    validated["currency"] = currency if isinstance(currency, str) else "гривня"

    # datetime
    dt = response_json.get("datetime")
    validated["datetime"] = dt if isinstance(dt, str) else datetime.now()

    # description
    desc = response_json.get("description")
    validated["description"] = desc if isinstance(desc, str) else ""

    # labelsId
    labels = response_json.get("labelsId")
    if isinstance(labels, list) and all(isinstance(i, int) for i in labels):
        validated["labelsId"] = labels
    else:
        validated["labelsId"] = []
    validated["labelsId"] = validate_labels(api_labels, validated["labelsId"])

    return validated
