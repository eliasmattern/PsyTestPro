import json

import pygame
from events import LANGUAGE_EVENT


class LanguageConfiguration:
    def __init__(self):
        self.lang = 'en'
        self.config_file = 'language_config.csv'

    def read_language_config(self):
        try:
            with open('json/settings.json', 'r', encoding='utf-8') as file:
                settings = json.load(file)
                self.lang = settings['language']
        except Exception as e:
            print(e)
            print('not able to access ./json/settings.json!')

    def update_language_config(self, new_language: str):
        try:
            with open('json/settings.json', 'r', encoding='utf-8') as file:
                settings = json.load(file)
            settings['language'] = new_language
            with open('json/settings.json', 'w', encoding='utf-8') as file:
                json.dump(settings, file)
            event = pygame.event.Event(LANGUAGE_EVENT, message="language changed")
            pygame.event.post(event)
        except Exception as e:
            print(e)
            print('not able to access ./json/settings.json! Couldn\'t save language!')

    def get_language(self):
        return self.lang
