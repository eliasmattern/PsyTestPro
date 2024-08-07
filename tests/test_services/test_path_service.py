import sys
import unittest
from unittest.mock import patch, Mock

from services import get_resource_path


class PathServiceTests(unittest.TestCase):

	@patch('os.path.abspath', return_value='/User/installation/path')
	def test_execute_command(self, os_base_path_mock: Mock):
		path = './path/to/file'
		result = get_resource_path(path)
		os_base_path_mock.assert_called_once()
		self.assertEqual(result, '/User/installation/path/' + path)

	def test_execute_command_with_meipass(self):
		sys._MEIPASS = '/absolute/meipass/path'
		path = './path/to/file'

		result = get_resource_path(path)

		self.assertEqual(result, '/absolute/meipass/path/' + path)

	def test_execute_command_outside_of_installation_folder(self):
		sys._MEIPASS = '/absolute/meipass/path'
		path = './path/to/file'

		result = get_resource_path(path, True)

		self.assertEqual(result, '/absolute/meipass/path/.' + path)

	@patch('sys.platform', 'darwin')
	def test_execute_command_outside_of_installation_folder_macos(self):
		# On macos the path should be changed and the folders /Contents/Frameworks/ should be removed from the path
		sys._MEIPASS = '/absolute/meipass/path/Contents/Frameworks/'
		path = './path/to/file'

		result = get_resource_path(path, True)

		self.assertEqual(result, '/absolute/meipass/path/.' + path)
