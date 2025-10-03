import re


def clean_special_characters(text):
    return re.sub(r'[^\w\s]', '', text).strip()
