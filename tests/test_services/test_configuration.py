import unittest
from unittest.mock import patch, mock_open

from services import PsyTestProConfig
from tests.test_services.test_services_utils import TASK_CONFIG_JSON, TASK_FROM_CONFIG


class ConfigurationTests(unittest.TestCase):

	def setUp(self):
		self.psy_test_pro_config = PsyTestProConfig()

	@patch('services.configuration.get_resource_path', return_value='json/suiteConfig.json')
	@patch('builtins.open', new_callable=mock_open, read_data='file')
	@patch('json.load')
	def test_load_suites(self, mock_json_load, mock_open, mock_get_resource_path):
		mock_json_load.return_value = ['suite']

		self.psy_test_pro_config.load_suites()

		mock_get_resource_path.assert_called_once_with('json/suiteConfig.json')
		mock_open.assert_called_once_with('json/suiteConfig.json', 'r',
										  encoding='utf-8')
		mock_json_load.assert_called_once_with(mock_open())

		self.assertEqual(self.psy_test_pro_config.suites, ['suite'])

	@patch('services.configuration.get_resource_path', return_value='mock.json/taskConfig.json')
	@patch('builtins.open', new_callable=mock_open, read_data='file')
	@patch('json.load')
	def test_load_suite_tasks(self, mock_json_load, mock_open, mock_get_resource_path):
		mock_json_load.return_value = TASK_CONFIG_JSON.copy()
		self.psy_test_pro_config.load_suite_tasks('suite')

		mock_get_resource_path.assert_called_once_with('json/taskConfig.json')
		mock_open.assert_called_once_with('mock.json/taskConfig.json', 'r', encoding='utf-8')
		mock_json_load.assert_called_once_with(mock_open())

		self.assertEqual(self.psy_test_pro_config.current_suite, 'suite_schedule')
		self.assertEqual(len(self.psy_test_pro_config.current_tasks), 1)
		task = self.psy_test_pro_config.current_tasks[0]

		self.assertEqual([task.id, task.name, task.task_type, task.duration, task.value],
						 [TASK_FROM_CONFIG.id, TASK_FROM_CONFIG.name, TASK_FROM_CONFIG.task_type,
						  TASK_FROM_CONFIG.duration, TASK_FROM_CONFIG.value])

	@patch('services.configuration.get_resource_path', return_value='mock.json/taskConfig.json')
	@patch('builtins.open', new_callable=mock_open, read_data='file')
	@patch('json.load')
	def test_get_suites(self, mock_json_load, mock_open, mock_get_resource_path):
		mock_json_load.return_value = TASK_CONFIG_JSON.copy()

		result = self.psy_test_pro_config.get_suites()

		self.assertEqual(result, list(TASK_CONFIG_JSON.keys()))


	if __name__ == '__main__':
		unittest.main()
