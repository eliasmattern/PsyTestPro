import copy
import unittest
from unittest.mock import patch, mock_open

from app_types import Task, TaskGroup
from services import PsyTestProConfig
from tests.test_services.test_services_utils import TASK_CONFIG_JSON, TASK_FROM_CONFIG, GROUP_FROM_CONFIG, \
	TASK_CONFIG_JSON_WITH_DELETED_TASK


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
		mock_json_load.return_value = copy.deepcopy(TASK_CONFIG_JSON)
		self.psy_test_pro_config.load_suite_tasks('suite')

		mock_get_resource_path.assert_called_once_with('json/taskConfig.json')
		mock_open.assert_called_once_with('mock.json/taskConfig.json', 'r', encoding='utf-8')
		mock_json_load.assert_called_once_with(mock_open())

		self.assertEqual(self.psy_test_pro_config.current_suite, 'suite_schedule')
		self.assertGreater(len(self.psy_test_pro_config.current_tasks), 0)
		task = self.psy_test_pro_config.current_tasks[0]

		self.assertEqual([task.id, task.name, task.task_type, task.duration, task.value],
						 [TASK_FROM_CONFIG.id, TASK_FROM_CONFIG.name, TASK_FROM_CONFIG.task_type,
						  TASK_FROM_CONFIG.duration, TASK_FROM_CONFIG.value])

	@patch('services.configuration.get_resource_path', return_value='mock.json/taskConfig.json')
	@patch('builtins.open', new_callable=mock_open, read_data='file')
	@patch('json.load')
	def test_get_suites(self, mock_json_load, mock_open, mock_get_resource_path):
		tasks = copy.deepcopy(TASK_CONFIG_JSON)
		del tasks['globalTasks']
		mock_json_load.return_value = copy.deepcopy(TASK_CONFIG_JSON)

		result = self.psy_test_pro_config.get_suites()

		mock_get_resource_path.assert_called_once_with('json/taskConfig.json')
		self.assertEqual(result, list(tasks.keys()))

	@patch('services.configuration.get_resource_path', return_value='mock.json/taskConfig.json')
	@patch('builtins.open', new_callable=mock_open, read_data='file')
	@patch('json.load')
	def test_load_task_of_suite(self, mock_json_load, mock_open, mock_get_resource_path):
		mock_json_load.return_value = copy.deepcopy(TASK_CONFIG_JSON)
		result = self.psy_test_pro_config.load_task_of_suite('suite_schedule')

		mock_get_resource_path.assert_called_once_with('json/taskConfig.json')
		mock_open.assert_called_once_with('mock.json/taskConfig.json', 'r',
										  encoding='utf-8')
		mock_json_load.assert_called_once_with(mock_open())
		print(result)
		self.assertEqual(len(result), 2)
		self.assertIsInstance(result[0], Task)
		self.assertIsInstance(result[1], TaskGroup)

		task = result[0]
		task_group = result[1]
		self.assertEqual([task.id, task.name, task.task_type, task.duration, task.value],
						 [TASK_FROM_CONFIG.id, TASK_FROM_CONFIG.name, TASK_FROM_CONFIG.task_type,
						  TASK_FROM_CONFIG.duration, TASK_FROM_CONFIG.value])
		self.assertEqual([task_group.id, task_group.name, task_group.pause_inbetween, task_group.loops],
						 [GROUP_FROM_CONFIG.id, GROUP_FROM_CONFIG.name, GROUP_FROM_CONFIG.pause_inbetween,
						  GROUP_FROM_CONFIG.loops])

		self.assertEqual(len(task_group.tasks), len(GROUP_FROM_CONFIG.tasks))

	@patch('services.configuration.get_resource_path', return_value='mock.json/taskConfig.json')
	@patch('builtins.open', new_callable=mock_open, read_data='file')
	@patch('json.load')
	def test_load_task_of_group(self, mock_json_load, mock_open, mock_get_resource_path):
		mock_json_load.return_value = copy.deepcopy(copy.deepcopy(TASK_CONFIG_JSON))

		result = self.psy_test_pro_config.load_task_of_group('suite_schedule', '1')

		mock_get_resource_path.assert_called_once_with('json/taskConfig.json')
		mock_open.assert_called_once_with('mock.json/taskConfig.json', 'r', encoding='utf-8')
		mock_json_load.assert_called_once_with(mock_open())

		self.assertEqual(len(result), 1)
		task = result[0]
		self.assertEqual([task.id, task.name, task.task_type, task.duration, task.value],
						 [TASK_FROM_CONFIG.id, TASK_FROM_CONFIG.name, TASK_FROM_CONFIG.task_type,
						  TASK_FROM_CONFIG.duration, TASK_FROM_CONFIG.value])

	@patch('services.configuration.get_resource_path', return_value='mock.json/taskConfig.json')
	@patch('builtins.open', new_callable=mock_open, read_data='file')
	@patch('json.load')
	@patch('json.dump')
	def test_delete_task(self, mock_json_dump, mock_json_load, mock_open, mock_get_resource_path):
		mock_json_load.return_value = copy.deepcopy(TASK_CONFIG_JSON)

		self.psy_test_pro_config.delete_task('suite_schedule', '0')

		mock_get_resource_path.assert_any_call('json/taskConfig.json')
		mock_open.assert_any_call('mock.json/taskConfig.json', 'r')
		mock_json_load.assert_called_once_with(mock_open())
		mock_json_dump.assert_called_once_with(TASK_CONFIG_JSON_WITH_DELETED_TASK, mock_open(), indent=4)

	@patch('services.configuration.get_resource_path', return_value='mock.json/taskConfig.json')
	@patch('builtins.open', new_callable=mock_open, read_data='file')
	@patch('json.load')
	@patch('json.dump')
	def test_save_task(self, mock_json_dump, mock_json_load, mock_open, mock_get_resource_path):
		tasks = copy.deepcopy(TASK_CONFIG_JSON)
		task = {
			"is_group": False,
			"name": "new_task",
			"position": 3,
			"time": "00:05:00",
			"state": "todo",
			"type": "command",
			"value": "print hello"
		}
		tasks['globalTasks']['tasks']['2'] = task
		tasks['suite_schedule']['tasks']['2'] = task
		mock_json_load.return_value = copy.deepcopy(TASK_CONFIG_JSON)

		self.psy_test_pro_config.save_task('suite_schedule', 'new_task', '00:05:00', 'command', 'print hello', None)

		mock_get_resource_path.assert_any_call('json/taskConfig.json')
		mock_open.assert_any_call('mock.json/taskConfig.json', 'r', encoding='utf-8')
		mock_json_load.assert_called_once_with(mock_open())
		mock_json_dump.assert_called_once_with(tasks, mock_open(), indent=4)

	if __name__ == '__main__':
		unittest.main()
