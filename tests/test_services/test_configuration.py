import copy
import unittest
from unittest.mock import patch, mock_open

from app_types import Task, TaskGroup
from services import PsyTestProConfig
from tests.test_services.test_services_utils import TASK_CONFIG_JSON, TASK_FROM_CONFIG, GROUP_FROM_CONFIG, \
	TASK_CONFIG_JSON_WITH_DELETED_TASK, CUSTOM_VARIABLES, SETTINGS_JSON, NEW_SETTINGS


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
	def test_delete_task_from_group(self, mock_json_dump, mock_json_load, mock_open, mock_get_resource_path):
		tasks = copy.deepcopy(TASK_CONFIG_JSON)
		del tasks['suite_schedule']['tasks']['1']['tasks']['0']
		mock_json_load.return_value = copy.deepcopy(TASK_CONFIG_JSON)

		self.psy_test_pro_config.delete_task('suite_schedule', '0', '1')

		mock_get_resource_path.assert_any_call('json/taskConfig.json')
		mock_open.assert_any_call('mock.json/taskConfig.json', 'r')
		mock_json_load.assert_called_once_with(mock_open())
		mock_json_dump.assert_called_once_with(tasks, mock_open(), indent=4)

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

	@patch('services.configuration.get_resource_path', return_value='mock.json/taskConfig.json')
	@patch('builtins.open', new_callable=mock_open, read_data='file')
	@patch('json.load')
	@patch('json.dump')
	def test_edit_task(self, mock_json_dump, mock_json_load, mock_open, mock_get_resource_path):
		tasks = copy.deepcopy(TASK_CONFIG_JSON)
		new_name = 'new name'
		new_time = '10:00:00'
		new_type = 'command'
		new_value = 'new value'
		task = {
			"is_group": False,
			"name": new_name,
			"position": 1,
			"time": new_time,
			"state": "todo",
			"type": new_type,
			"value": new_value
		}
		tasks['suite_schedule']['tasks']['0'] = task
		mock_json_load.return_value = copy.deepcopy(TASK_CONFIG_JSON)

		self.psy_test_pro_config.edit_task('0', 'suite_schedule', new_name, new_time, new_type, new_value)

		mock_get_resource_path.assert_any_call('json/taskConfig.json')
		mock_open.assert_any_call('mock.json/taskConfig.json', 'r', encoding='utf-8')
		mock_json_load.assert_called_once_with(mock_open())
		mock_json_dump.assert_called_once_with(tasks, mock_open(), indent=4)

	@patch('services.configuration.get_resource_path', return_value='mock.json/customVariables.json')
	@patch('builtins.open', new_callable=mock_open, read_data='file')
	@patch('json.load')
	def test_load_custom_variables(self, mock_json_load, mock_open, mock_get_resource_path):
		mock_json_load.return_value = copy.deepcopy(CUSTOM_VARIABLES)

		result = self.psy_test_pro_config.load_custom_variables()

		mock_get_resource_path.assert_any_call('json/customVariables.json')
		mock_open.assert_any_call('mock.json/customVariables.json', 'r', encoding='utf-8')
		mock_json_load.assert_called_once_with(mock_open())
		self.assertEqual(result, CUSTOM_VARIABLES)

	@patch('services.configuration.get_resource_path', return_value='mock.json/customVariables.json')
	@patch('builtins.open', new_callable=mock_open, read_data='file')
	@patch('json.load')
	@patch('json.dump')
	def test_save_var(self, mock_json_dump, mock_json_load, mock_open, mock_get_resource_path):
		vars = copy.deepcopy(CUSTOM_VARIABLES)
		vars.append('var3')
		mock_json_load.return_value = copy.deepcopy(CUSTOM_VARIABLES)

		result = self.psy_test_pro_config.save_var('var3')

		mock_get_resource_path.assert_any_call('json/customVariables.json')
		mock_open.assert_any_call('mock.json/customVariables.json', 'r')
		mock_json_load.assert_called_once_with(mock_open())
		mock_json_dump.assert_called_once_with(vars, mock_open())

		self.assertTrue(result)

	@patch('services.configuration.get_resource_path', return_value='mock.json/customVariables.json')
	@patch('builtins.open', new_callable=mock_open, read_data='file')
	@patch('json.load')
	@patch('json.dump')
	def test_do_not_save_var_if_length_3(self, mock_json_dump, mock_json_load, mock_open, mock_get_resource_path):
		mock_json_load.return_value = ['var1', 'var2', 'var3']

		result = self.psy_test_pro_config.save_var('var3')

		mock_get_resource_path.assert_called_once_with('json/customVariables.json')
		mock_open.assert_called_once_with('mock.json/customVariables.json', 'r')
		mock_json_load.assert_called_once_with(mock_open())

		self.assertFalse(result)

	@patch('services.configuration.get_resource_path', return_value='mock.json/customVariables.json')
	@patch('builtins.open', new_callable=mock_open, read_data='file')
	@patch('json.load')
	@patch('json.dump')
	def test_delete_var(self, mock_json_dump, mock_json_load, mock_open, mock_get_resource_path):
		vars = ['var1']
		mock_json_load.return_value = copy.deepcopy(CUSTOM_VARIABLES)

		self.psy_test_pro_config.delete_var('var2')

		mock_get_resource_path.assert_any_call('json/customVariables.json')
		mock_open.assert_any_call('mock.json/customVariables.json', 'r', encoding='utf-8')
		mock_json_load.assert_called_once_with(mock_open())
		mock_json_dump.assert_called_once_with(vars, mock_open())

	@patch('services.configuration.get_resource_path', return_value='mock.json/settings.json')
	@patch('builtins.open', new_callable=mock_open, read_data='file')
	@patch('json.load')
	def test_get_settings(self, mock_json_load, mock_open, mock_get_resource_path):
		mock_json_load.return_value = copy.deepcopy(SETTINGS_JSON)

		result = self.psy_test_pro_config.get_settings()

		mock_get_resource_path.assert_any_call('json/settings.json')
		mock_open.assert_any_call('mock.json/settings.json', 'r', encoding='utf-8')
		mock_json_load.assert_called_once_with(mock_open())
		self.assertEqual(result, SETTINGS_JSON)

	@patch('services.configuration.get_resource_path', return_value='mock.json/settings.json')
	@patch('builtins.open', new_callable=mock_open, read_data='file')
	@patch('json.load')
	@patch('json.dump')
	def test_save_settings(self, mock_json_dump, mock_json_load, mock_open, mock_get_resource_path):
		mock_json_load.return_value = copy.deepcopy(SETTINGS_JSON)
		new_settings_json = {
			"language": "en",
			"backgroundColor": NEW_SETTINGS.background_color,
			"primaryColor": NEW_SETTINGS.primary_color,
			"buttonColor": NEW_SETTINGS.button_color,
			"buttonTextColor": NEW_SETTINGS.button_text_color,
			"successColor": NEW_SETTINGS.success_color,
			"dangerColor": NEW_SETTINGS.danger_color,
			"warningColor": NEW_SETTINGS.warning_color,
			"activeButtonColor": NEW_SETTINGS.active_button_color,
			"inactiveButtonColor": NEW_SETTINGS.inactive_button_color,
			"groupButtonColor": NEW_SETTINGS.group_button_color,
			"gridColor": NEW_SETTINGS.grid_color,
			"showNextTask": NEW_SETTINGS.show_next_task,
			"showPlayTaskButton": NEW_SETTINGS.show_play_task_button,
			"audioPath": NEW_SETTINGS.audio_path,
		}

		self.psy_test_pro_config.save_settings(NEW_SETTINGS)

		mock_get_resource_path.assert_any_call('json/settings.json')
		mock_open.assert_any_call('mock.json/settings.json', 'r', encoding='utf-8')
		mock_json_load.assert_called_once_with(mock_open())
		mock_json_dump.assert_called_once_with(new_settings_json, mock_open())

	@patch('services.configuration.get_resource_path', return_value='mock.json/taskConfig.json')
	@patch('builtins.open', new_callable=mock_open, read_data='file')
	@patch('json.load')
	@patch('json.dump')
	def test_create_group(self, mock_json_dump, mock_json_load, mock_open, mock_get_resource_path):
		tasks = copy.deepcopy(TASK_CONFIG_JSON)
		task = {
			"is_group": True,
			"name": "new group",
			"pause": "00:05:00",
			"loops": 2,
			"tasks": {
				"0": {
					"is_group": False,
					"name": "TESTTASK",
					"time": "00:05:00",
					"state": "todo",
					"type": "text",
					"value": {"title": "Title", "description": "Description"},
					"position": 1
				}
			},
			'position': 3
		}
		tasks['globalTasks']['tasks']['2'] = task
		tasks['suite_schedule']['tasks']['2'] = task
		mock_json_load.return_value = copy.deepcopy(TASK_CONFIG_JSON)

		self.psy_test_pro_config.create_group('suite_schedule', 'new group', 2, '00:05:00', [TASK_FROM_CONFIG])

		mock_get_resource_path.assert_any_call('json/taskConfig.json')
		mock_open.assert_any_call('mock.json/taskConfig.json', 'r', encoding='utf-8')
		mock_json_load.assert_called_once_with(mock_open())
		mock_json_dump.assert_called_once_with(tasks, mock_open(), indent=4)

	@patch('services.configuration.get_resource_path', return_value='mock.json/taskConfig.json')
	@patch('builtins.open', new_callable=mock_open, read_data='file')
	@patch('json.load')
	@patch('json.dump')
	def test_edit_group(self, mock_json_dump, mock_json_load, mock_open, mock_get_resource_path):
		tasks = copy.deepcopy(TASK_CONFIG_JSON)
		new_group_name = 'new group name'
		new_loops = 4
		new_pause = '10:00:00'
		task = {
			"is_group": False,
			"name": "TESTTASK",
			"time": "00:05:00",
			"state": "todo",
			"type": "text",
			"value": {"title": "Title", "description": "Description"},
			"position": 2
		}
		tasks['suite_schedule']['tasks']['1']['name'] = new_group_name
		tasks['suite_schedule']['tasks']['1']['pause'] = new_pause
		tasks['suite_schedule']['tasks']['1']['loops'] = new_loops
		tasks['suite_schedule']['tasks']['1']['tasks']['1'] = task
		mock_json_load.return_value = copy.deepcopy(TASK_CONFIG_JSON)

		new_task = Task('1', 'TESTTASK', '00:05:00', 'text', {"title": "Title", "description": "Description"}, 2)

		self.psy_test_pro_config.edit_group('suite_schedule', '1', new_group_name, new_loops, new_pause, [TASK_FROM_CONFIG, new_task])

		mock_get_resource_path.assert_any_call('json/taskConfig.json')
		mock_open.assert_any_call('mock.json/taskConfig.json', 'r', encoding='utf-8')
		mock_json_load.assert_called_once_with(mock_open())
		mock_json_dump.assert_called_once_with(tasks, mock_open(), indent=4)


if __name__ == '__main__':
	unittest.main()
