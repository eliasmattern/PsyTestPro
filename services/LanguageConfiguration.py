import json


class LanguageConfiguration:
    def __init__(self):
        self.lang = 'en'
        self.config_file = 'language_config.csv'

    def read_language_config(self):
        try:
            with open(f'json/settings.json', 'r', encoding='utf-8') as file:
                settings = json.load(file)
                self.lang = settings['language']
        except Exception as e:
            print(e)
            print('not able to access ./json/settings.json!')

    def update_language_config(self, new_language):
        try:
            with open(f'json/settings.json', 'r', encoding='utf-8') as file:
                settings = json.load(file)
            settings['language'] = new_language
            with open('json/settings.json', 'w') as file:
                json.dump(settings, file)
        except Exception as e:
            print(e)
            print('not able to access ./json/settings.json! Couldn\'t save language!')

    def get_language(self):
        return self.lang
