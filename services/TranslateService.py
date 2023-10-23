import json

class TranslateService:
    def __init__(self, language_config):
        self.current_language = "en"
        language_config.read_language_config()
        language = self.language_config.get_language()
        if len(language) > 0:
            self.current_language = language
        self.translations = {}
        self.load_language(self.current_language)

    def load_language(self, language):
        try:
            with open(f"lang/{language}.json", "r", encoding="utf-8") as file:
                self.translations[language] = json.load(file)
        except FileNotFoundError:
            raise Exception(f"Translation file for {language} not found")

    def get_translation(self, key):
        return self.translations[self.current_language].get(key, self.translations["en"].get(key, ""))

    def set_language(self, language):
        if language not in self.translations:
            self.load_language(language)
        self.current_language = language
