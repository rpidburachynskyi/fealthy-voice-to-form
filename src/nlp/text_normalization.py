import re


def clean_special_characters(text):
    """Remove special characters from text, keeping only word characters and spaces."""
    return re.sub(r"[^\w\s]", "", text).strip()
