import os
import logging
import asyncio

from dotenv import load_dotenv
import functions_framework
from flask import jsonify

from prompts import (
    MAIN_PROMPT,
    BUSINESS_PROMPT,
    make_categories_prompt,
    make_labels_prompt,
    make_accounts_prompt,
    make_datetime,
)
from gpt import transcript_audio_file, process_text
from endpoints import get_user_categories, get_user_labels, get_user_accounts
from validation import validate_and_merge_json, validate_response
from postprocessing import (
    process_time_llm_response,
    process_business_llm_response,
)


# Configure logging to only show code debug messages
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)  
console_handler.setFormatter(logging.Formatter("%(message)s"))  
logger.handlers.clear()
logger.addHandler(console_handler)

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

logger = logging.getLogger(__name__)

async def get_main_json_data(OPENAI_API_KEY, transcription_text):
    """Fetches the main JSON response based on transcription."""
    llm_response = await process_text(OPENAI_API_KEY, system_prompt=MAIN_PROMPT, user_prompt=transcription_text)
    return llm_response

async def get_categories_json_data(OPENAI_API_KEY, transcription_text, user_id):
    """Fetches the categories JSON response."""
    modified_categories, api_categories = await get_user_categories(user_id)
    system_prompt = make_categories_prompt(modified_categories)
    llm_response = await process_text(OPENAI_API_KEY, system_prompt=system_prompt, user_prompt=transcription_text)
    return llm_response, api_categories

async def get_labels_json_data(OPENAI_API_KEY, transcription_text, user_id):
    """Fetches the labels JSON response."""
    api_labels = await get_user_labels(id=user_id)
    system_prompt = make_labels_prompt(api_labels)
    llm_response = await process_text(OPENAI_API_KEY, system_prompt=system_prompt, user_prompt=transcription_text)
    return llm_response, api_labels

async def get_accounts_json_data(OPENAI_API_KEY, transcription_text, user_id):
    """Fetches the accounts JSON response."""
    api_accounts = await get_user_accounts(id=user_id)
    system_prompt = make_accounts_prompt(api_accounts)
    llm_response = await process_text(OPENAI_API_KEY, system_prompt=system_prompt, user_prompt=transcription_text)
    return llm_response, api_accounts

async def get_datetime_json_data(OPENAI_API_KEY, transcription_text):
    system_prompt = make_datetime()
    llm_response = await process_text(OPENAI_API_KEY, system_prompt=system_prompt, user_prompt=transcription_text)
    return process_time_llm_response(llm_response)

async def get_business_json_data(OPENAI_API_KEY, transcription_text):
    llm_response = await process_text(OPENAI_API_KEY, system_prompt=BUSINESS_PROMPT, user_prompt=transcription_text)
    return process_business_llm_response(llm_response)

async def parse_audio_into_json(audio_file, user_id=19):
    """Handles audio processing and runs JSON generation tasks asynchronously."""
    transcription_text = await transcript_audio_file(OPENAI_API_KEY, file=audio_file)
    logger.debug(f"### Processed audio:\n {transcription_text}")

    # Run all text-processing tasks concurrently
    main_json, \
    (categories_json, categories), \
    (labels_json, labels), \
    (accounts_json, accounts), \
    datetime_json = await asyncio.gather(
        get_main_json_data(OPENAI_API_KEY, transcription_text),
        get_categories_json_data(OPENAI_API_KEY, transcription_text, user_id),
        get_labels_json_data(OPENAI_API_KEY, transcription_text, user_id),
        get_accounts_json_data(OPENAI_API_KEY, transcription_text, user_id),
        get_datetime_json_data(OPENAI_API_KEY, transcription_text)
    )

    logger.debug(f"### Main response:\n {main_json}")
    logger.debug(f"### Categories response:\n {categories_json}")
    logger.debug(f"### Labels response:\n {labels_json}")
    logger.debug(f"### Accounts response:\n {accounts_json}")
    logger.debug(f"### Datetime response:\n {datetime_json}")

    # Merge the results
    merged_json = validate_and_merge_json((main_json, categories_json, labels_json, accounts_json, datetime_json))

    return validate_response(merged_json, categories, labels, accounts)

async def process_request(request):
    """Async function that processes the request."""
    audio_file = request.files.get('file')

    if not audio_file:
        return jsonify({"error": "No file uploaded"}), 400

    if not audio_file.filename.lower().endswith('.mp3'):
        return jsonify({"error": "Invalid file format, only MP3 allowed"}), 400

    result = await parse_audio_into_json(audio_file)
    return jsonify(result), 200


@functions_framework.http
def voice_to_form(request):
    """API Function to handle voice to form conversion."""
    return asyncio.run(process_request(request))


@functions_framework.http
def test_business(request):
    # TODO move call to main function after testing
    text = request.args.get("text")
    print("request", text)
    
    if not text:
        return jsonify({"error": "No text provided"}), 400
    
    # Test business search directly with text input
    result = asyncio.run(get_business_json_data(OPENAI_API_KEY, text))
    print("result", result)
    return jsonify(result), 200
