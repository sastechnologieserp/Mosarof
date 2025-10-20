from deep_translator import GoogleTranslator

def translate_text(text, target_language='en'):
    translator = GoogleTranslator(target=target_language)
    translated_text = translator.translate(text)
    return translated_text