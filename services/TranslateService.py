import json

from services import LanguageConfiguration
from .PathService import get_resource_path


class TranslateService:
	def __init__(self, language_config: LanguageConfiguration):
		self.current_language = 'en'
		language_config.read_language_config()
		language = language_config.get_language()
		if len(language) > 0:
			self.current_language = language
		self.translations = {}
		self.load_language('en')
		self.load_language(self.current_language)

	def load_language(self, language: str):
		try:
			with open(get_resource_path(f'lang/{language}.json'), 'r', encoding='utf-8') as file:
				self.translations[language] = json.load(file)
		except FileNotFoundError:
			raise Exception(f'Translation file for {language} not found')

	def get_translation(self, key: str):
		return self.translations[self.current_language].get(key, self.translations['en'].get(key, ''))

	def set_language(self, language: str):
		if language not in self.translations:
			self.load_language(language)
		self.current_language = language
