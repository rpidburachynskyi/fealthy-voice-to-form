from transliterate import translit


def transliterate_ukrainian_to_english(text):
    return translit(text, 'uk', reversed=True).replace("'", "") 
