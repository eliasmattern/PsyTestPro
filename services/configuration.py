import json
from typing import Union

from app_types import Task, TaskGroup
from .PathService import get_resource_path


class PsyTestProConfig:
	def __init__(self):
		self.suites = None
		self.current_suite = None
		self.current_tasks: list[Union[Task, TaskGroup]] = []
		self.error_msg = ''

	def load_suites(self):
		try:
			with open(get_resource_path('json/suiteConfig.json'), 'r', encoding='utf-8') as file:
				suite = json.load(file)
				string = ','.join(str(e) for e in suite)
				self.suites = string.split(',')
		except FileNotFoundError:
			raise Exception('File Error: ./json/suiteConfig.json not found ')

	def load_suite_tasks(self, suite: str):
		self.error_msg = ''
		try:
			with open(get_resource_path('json/taskConfig.json'), 'r', encoding='utf-8') as file:
				tasks = json.load(file)
				if tasks.get(str(suite) + '_schedule') is not None:
					for task_id, task_detail in tasks.get(suite + '_schedule').get('tasks').items():
						if task_detail['is_group']:
							self.current_tasks.append(
								TaskGroup(task_id, task_detail['name'], task_detail['pause'], task_detail['loops'],
										  task_detail['tasks'], task_detail['position']))
						else:
							self.current_tasks.append(
								Task(task_id, task_detail['name'], task_detail['time'], task_detail['type'],
									 task_detail['value'], task_detail['position'], task_detail['state']))
					self.current_suite = str(suite) + '_schedule'
				elif tasks.get(str(suite) + '_list') is not None:
					for task_id, task_detail in tasks.get(suite + '_list').get('tasks').items():
						if task_detail['is_group']:
							self.current_tasks.append(
								TaskGroup(task_id, task_detail['name'], task_detail['pause'], task_detail['loops'],
										  task_detail['tasks'], task_detail['position']))
						else:
							self.current_tasks.append(
								Task(task_id, task_detail['name'], task_detail['time'], task_detail['type'],
									 task_detail['value'], task_detail['position'], task_detail['state']))
					self.current_suite = str(suite) + '_list'
				else:
					self.error_msg = 'experimentNotFound'
		except FileNotFoundError:
			raise Exception('File Error: ./json/taskConfig.json not found')

	def save_suite(self, suite_name: str, schedule: bool):
		with open(get_resource_path('json/suiteConfig.json'), 'r', encoding='utf-8') as file:
			original_suites = json.load(file)

			if not suite_name in original_suites:
				# Add a new value to the array
				original_suites.append(suite_name)

		# Save the updated array back to the file
		with open(get_resource_path('json/suiteConfig.json'), 'w', encoding='utf-8') as file:
			json.dump(original_suites, file)

		# Load the original JSON from the file
		with open(get_resource_path('json/taskConfig.json'), 'r', encoding='utf-8') as file:
			original_tasks = json.load(file)
		if schedule:
			suite_name += '_schedule'
		else:
			suite_name += '_list'

		if not suite_name in original_tasks:
			# Add a new variable with an empty task object
			original_tasks[suite_name] = {'tasks': {}}

		# Save the updated JSON back to the file
		with open(get_resource_path('json/taskConfig.json'), 'w', encoding='utf-8') as file:
			json.dump(original_tasks, file, indent=4)

	def get_suites(self):
		with open(get_resource_path('json/taskConfig.json'), 'r', encoding='utf-8') as file:
			data = json.load(file)
		del data['globalTasks']
		variable_names = data.keys()
		result = []
		for variable in variable_names:
			result.append(str(variable))

		return result

	def load_task_of_suite(self, suite: str) -> list[Union[Task, TaskGroup]]:

		with open(get_resource_path('json/taskConfig.json'), 'r', encoding='utf-8') as file:
			data = json.load(file)
		tasks = []
		for task_id, task_detail in data[suite]['tasks'].items():
			if task_detail['is_group']:
				tasks.append(
					TaskGroup(task_id, task_detail['name'], task_detail['pause'], task_detail['loops'],
							  task_detail['tasks'], task_detail['position']))
			else:
				tasks.append(
					Task(task_id, task_detail['name'], task_detail['time'], task_detail['type'], task_detail['value'],
						 task_detail['position'], task_detail['state']))
		return tasks

	def load_task_of_group(self, suite: str, group_id) -> list[Union[Task, TaskGroup]]:

		with open(get_resource_path('json/taskConfig.json'), 'r', encoding='utf-8') as file:
			data = json.load(file)
		tasks = []
		for task_id, task_detail in data[suite]['tasks'][group_id]['tasks'].items():
			tasks.append(
				Task(task_id, task_detail['name'], task_detail['time'], task_detail['type'], task_detail['value'],
					 task_detail['position'], task_detail['state']))
		return tasks

	def delete_task(self, suite: str, task_id: str, group_id: str = None):
		if suite == 'hab_variable_variable':
			suite = 'hab_variable'

		with open(get_resource_path('json/taskConfig.json'), 'r') as file:
			data = json.load(file)

		if group_id is None:
			deleted_position = data[suite]['tasks'][task_id]['position']
			del data[suite]['tasks'][task_id]
			for key in data[suite]['tasks'].keys():
				position = data[suite]['tasks'][key]['position']
				if position > deleted_position:
					data[suite]['tasks'][key]['position'] = position - 1
		else:
			deleted_position = data[suite]['tasks'][group_id]['tasks'][task_id]['position']
			del data[suite]['tasks'][group_id]['tasks'][task_id]
			for key in data[suite]['tasks'][group_id]['tasks'].keys():
				position = data[suite]['tasks'][group_id]['tasks'][key]['position']
				if position > deleted_position:
					data[suite]['tasks'][group_id]['tasks'][key]['position'] = position - 1

		# Save the updated array back to the file
		with open(get_resource_path('json/taskConfig.json'), 'w') as file:
			json.dump(data, file, indent=4)

	def save_task(self, suite: str, name: str, time: str, type: str, value: str, group_id: Union[str, None]):

		# Load the JSON data from a file
		with open(get_resource_path('json/taskConfig.json'), 'r', encoding='utf-8') as file:
			json_data = json.load(file)

		# Function to add a new task to a specific object
		def add_task_to_object(json_data: dict, suite: str, task_id: str, task_name: str, time: str, type: str,
							   value: str, group: Union[str, None]):
			if group is None:
				tasks = json_data[suite]['tasks']
			else:
				tasks = json_data[suite]['tasks'][group]['tasks']
			new_task = {
				'is_group': False,
				'name': task_name,
				'position': len(tasks) + 1,
				'time': time,
				'state': 'todo',
				'type': type,
				'value': value
			}
			if group is None:
				json_data[suite]['tasks'][task_id] = new_task
				if suite != 'globalTasks':
					global_task = new_task.copy()
					global_keys = json_data['globalTasks']['tasks'].keys()
					global_numeric_keys = [eval(i) for i in global_keys]
					global_task_id = max(global_numeric_keys) + 1 if len(global_numeric_keys) > 0 else 0
					position = len(json_data['globalTasks']['tasks']) + 1
					global_task['position'] = position
					json_data['globalTasks']['tasks'][str(global_task_id)] = global_task
			else:
				json_data[suite]['tasks'][group]['tasks'][task_id] = new_task

		keys = json_data[suite]['tasks'].keys() if group_id is None \
			else json_data[suite]['tasks'][group_id]['tasks'].keys()
		numeric_keys = [eval(i) for i in keys]
		task_id = max(numeric_keys) + 1 if len(numeric_keys) > 0 else 0

		add_task_to_object(json_data, suite, str(task_id), name, time, type, value, group_id)

		# Save the updated JSON data back to the file
		with open(get_resource_path('json/taskConfig.json'), 'w', encoding='utf-8') as file:
			json.dump(json_data, file, indent=4)

	def edit_task(self, task_id: str, suite, name: str, time: str, type: str, value: str,
				  group: Union[str, None] = None):

		# Load the JSON data from a file
		with open(get_resource_path('json/taskConfig.json'), 'r', encoding='utf-8') as file:
			json_data = json.load(file)
		if not group:
			json_data[suite]['tasks'][task_id]['time'] = time
			json_data[suite]['tasks'][task_id]['type'] = type
			json_data[suite]['tasks'][task_id]['value'] = value
			json_data[suite]['tasks'][task_id]['name'] = name
		else:
			json_data[suite]['tasks'][group]['tasks'][task_id]['time'] = time
			json_data[suite]['tasks'][group]['tasks'][task_id]['type'] = type
			json_data[suite]['tasks'][group]['tasks'][task_id]['value'] = value
			json_data[suite]['tasks'][group]['tasks'][task_id]['name'] = name
		# Save the updated JSON data back to the file
		with open(get_resource_path('json/taskConfig.json'), 'w', encoding='utf-8') as file:
			json.dump(json_data, file, indent=4)

	def load_custom_variables(self):
		with open(get_resource_path('json/customVariables.json'), 'r', encoding='utf-8') as file:
			return json.load(file)

	def save_var(self, name: str):
		with open(get_resource_path('json/customVariables.json'), 'r') as file:
			data = json.load(file)
		if len(data) >= 3:
			return False
		else:
			data.append(name)
			with open(get_resource_path('json/customVariables.json'), 'w') as file:
				json.dump(data, file)
			return True

	def delete_var(self, name: str):
		with open(get_resource_path('json/customVariables.json'), 'r', encoding='utf-8') as file:
			data = json.load(file)
		data.remove(name)
		with open(get_resource_path('json/customVariables.json'), 'w', encoding='utf-8') as file:
			json.dump(data, file)

	def get_settings(self):
		with open(get_resource_path('json/settings.json'), 'r', encoding='utf-8') as file:
			settings = json.load(file)

		return settings

	def save_settings(self, new_settings):
		with open(get_resource_path('json/settings.json'), 'r', encoding='utf-8') as file:
			settings = json.load(file)

		settings["backgroundColor"] = new_settings.background_color
		settings["primaryColor"] = new_settings.primary_color
		settings["buttonColor"] = new_settings.button_color
		settings["buttonTextColor"] = new_settings.button_text_color
		settings["activeButtonColor"] = new_settings.active_button_color
		settings["inactiveButtonColor"] = new_settings.inactive_button_color
		settings["groupButtonColor"] = new_settings.group_button_color
		settings["successColor"] = new_settings.success_color
		settings["dangerColor"] = new_settings.danger_color
		settings["warningColor"] = new_settings.warning_color
		settings["gridColor"] = new_settings.grid_color
		settings["showNextTask"] = new_settings.show_next_task
		settings["showPlayTaskButton"] = new_settings.show_play_task_button
		settings["audioPath"] = new_settings.audio_path

		with open(get_resource_path('json/settings.json'), 'w', encoding='utf-8') as file:
			json.dump(settings, file)

	def save_task_list(self, suite: str, tasks: list[Task]):
		with open(get_resource_path('json/taskConfig.json'), 'r', encoding='utf-8') as file:
			data = json.load(file)
		new_tasks = {}
		for task in tasks:
			if isinstance(task, Task):
				new_tasks[task.id] = {'is_group': False, 'name': task.name, 'time': task.duration, 'state': task.state,
									  'type': task.task_type, 'value': task.value, 'position': task.position}
			elif isinstance(task, TaskGroup):
				group_tasks = {}
				for t in task.tasks:
					group_tasks[t.id] = {'is_group': False, 'name': t.name, 'time': t.duration,
										 'state': t.state, 'type': t.task_type, 'value': t.value,
										 'position': t.position}
				new_tasks[task.id] = {"is_group": True,
									  "name": task.name,
									  "pause": str(task.pause_inbetween),
									  "loops": task.loops,
									  "tasks": group_tasks,
									  "position": task.position}
		data[suite]['tasks'] = new_tasks
		with open(get_resource_path('json/taskConfig.json'), 'w', encoding='utf-8') as file:
			json.dump(data, file, indent=4)

	def save_group_task_list(self, suite: str, group_id, tasks: list[Task]):
		with open(get_resource_path('json/taskConfig.json'), 'r', encoding='utf-8') as file:
			data = json.load(file)
		new_tasks = {}
		for task in tasks:
			new_tasks[task.id] = {'name': task.name, 'time': task.duration, 'state': task.state, 'type': task.task_type,
								  'value': task.value, 'position': task.position}
		data[suite]['tasks'][group_id]['tasks'] = new_tasks
		with open(get_resource_path('json/taskConfig.json'), 'w', encoding='utf-8') as file:
			json.dump(data, file, indent=4)

	def create_group(self, suite: str, group_name: str, loops: int, pause_between_loops: str, tasks: list[Task]):
		with open(get_resource_path('json/taskConfig.json'), 'r', encoding='utf-8') as file:
			json_data = json.load(file)

		# Function to add a new task to a specific object
		def add_task_to_object(json_data: dict, suite: str, group_id: str, group_name: str, loops: int,
							   pause_between_loops: str, task_list: list[Task]):
			tasks = json_data[suite]['tasks']
			new_task_list = {}
			for i, task in enumerate(task_list):
				new_task_list[str(i)] = {'is_group': False, 'name': task.name, 'time': task.duration,
										 'state': task.state, 'type': task.task_type, 'value': task.value,
										 'position': task.position}
			new_task = {
				"is_group": True,
				"name": group_name,
				"pause": pause_between_loops,
				"loops": loops,
				"tasks": new_task_list,
				"position": len(tasks) + 1
			}
			json_data[suite]['tasks'][group_id] = new_task
			if suite != 'globalTasks':
				keys = json_data['globalTasks']['tasks'].keys()
				numeric_keys = [eval(i) for i in keys]
				global_id = max(numeric_keys) + 1 if len(numeric_keys) > 0 else 0
				json_data['globalTasks']['tasks'][global_id] = new_task

		keys = json_data[suite]['tasks'].keys()
		numeric_keys = [eval(i) for i in keys]
		task_id = max(numeric_keys) + 1 if len(numeric_keys) > 0 else 0

		add_task_to_object(json_data, suite, str(task_id), group_name, loops, pause_between_loops, tasks)

		# Save the updated JSON data back to the file
		with open(get_resource_path('json/taskConfig.json'), 'w', encoding='utf-8') as file:
			json.dump(json_data, file, indent=4)

	def edit_group(self, suite: str, group_id: str, group_name: str, loops: int, pause: str, tasks: list[Task]):

		# Load the JSON data from a file
		with open(get_resource_path('json/taskConfig.json'), 'r', encoding='utf-8') as file:
			json_data = json.load(file)

		new_task_list = {}
		for task in tasks:
			new_task_list[task.id] = {'is_group': False, 'name': task.name, 'time': task.duration,
									  'state': task.state, 'type': task.task_type, 'value': task.value,
									  'position': task.position}

		json_data[suite]['tasks'][group_id]['name'] = group_name
		json_data[suite]['tasks'][group_id]['pause'] = pause
		json_data[suite]['tasks'][group_id]['loops'] = loops
		json_data[suite]['tasks'][group_id]['tasks'] = new_task_list

		# Save the updated JSON data back to the file
		with open(get_resource_path('json/taskConfig.json'), 'w', encoding='utf-8') as file:
			json.dump(json_data, file, indent=4)

	def load_group(self, suite, active_group) -> TaskGroup:
		with open(get_resource_path('json/taskConfig.json'), 'r', encoding='utf-8') as file:
			json_data = json.load(file)
		task = json_data[suite]['tasks'][active_group]
		return TaskGroup(active_group, task['name'], task['pause'], task['loops'],
						 task['tasks'], task['position'])
