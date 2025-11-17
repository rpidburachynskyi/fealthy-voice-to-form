from transliterate import translit


def transliterate_ukrainian_to_english(text):
    """Transliterate Ukrainian text to English using transliteration library."""
    return translit(text, "uk", reversed=True).replace("'", "")
