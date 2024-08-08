import unittest
from unittest.mock import patch, mock_open, Mock

import pygame

from events import LANGUAGE_EVENT
from services import LanguageConfiguration


class LanguageConfigurationTests(unittest.TestCase):

	def setUp(self):
		self.language_configuration = LanguageConfiguration()

	@patch('services.LanguageConfiguration.get_resource_path', return_value='mock-json/settings.json')
	@patch('builtins.open', new_callable=mock_open, read_data='file')
	@patch('json.load', return_value={'language': 'de'})
	def test_read_language_config(self, mock_json_load: Mock, mock_open: Mock, mock_get_resource_path: Mock):
		self.language_configuration.read_language_config()

		mock_get_resource_path.assert_called_once_with('json/settings.json')
		mock_open.assert_called_once_with('mock-json/settings.json', 'r', encoding='utf-8')
		mock_json_load.assert_called_once_with(mock_open())

		self.assertEqual(self.language_configuration.lang, 'de')

	@patch('services.LanguageConfiguration.get_resource_path', return_value='mock-json/settings.json')
	@patch('builtins.open', new_callable=mock_open, read_data='file')
	@patch('json.load', return_value={'language': 'en'})
	@patch('json.dump')
	@patch('pygame.event.post')
	def test_update_language_config(self, mock_event: Mock, mock_json_dump: Mock, mock_json_load: Mock, mock_open: Mock, mock_get_resource_path: Mock):
		self.language_configuration.update_language_config('de')

		mock_get_resource_path.assert_called_with('json/settings.json')
		mock_open.assert_any_call('mock-json/settings.json', 'r', encoding='utf-8')
		mock_open.assert_any_call('mock-json/settings.json', 'w', encoding='utf-8')
		mock_json_load.assert_called_once_with(mock_open())
		mock_json_dump.assert_called_once_with({'language': 'de'}, mock_open())
		mock_event.assert_called_once_with(pygame.event.Event(LANGUAGE_EVENT, message="language changed"))

	def test_get_language(self):
		result = self.language_configuration.get_language()

		self.assertEqual(result, 'en')
