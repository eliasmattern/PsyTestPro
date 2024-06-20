import json

from .PathService import get_resource_path


class PsyTestProConfig:
    def __init__(self):
        self.suites = None
        self.current_suite = None
        self.current_tasks: dict = None
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
                    self.current_tasks = tasks.get(suite + '_schedule').get('tasks')
                    self.current_suite = str(suite) + '_schedule'
                elif tasks.get(str(suite) + '_list') is not None:
                    self.current_tasks = tasks.get(suite + '_list').get('tasks')
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
        variable_names = data.keys()
        result = []
        for variable in variable_names:
            result.append(str(variable))

        return result

    def load_task_names_of_suites(self, suite: str) -> list:

        with open(get_resource_path('json/taskConfig.json'), 'r', encoding='utf-8') as file:
            data = json.load(file)
        tasks = data[suite]['tasks']

        sorted_tasks = sorted(tasks.items(), key=lambda item: item[1]['position'])
        current_tasks = {k: v for k, v in sorted_tasks}
        tasks = list(current_tasks.keys())

        return tasks

    def load_task_of_suite(self, suite: str) -> dict:

        with open(get_resource_path('json/taskConfig.json'), 'r', encoding='utf-8') as file:
            data = json.load(file)
        return data[suite]['tasks']

    def delete_task(self, suite: str, task: str):
        if suite == 'hab_variable_variable':
            suite = 'hab_variable'

        with open(get_resource_path('json/taskConfig.json'), 'r') as file:
            data = json.load(file)
        deleted_position = data[suite]['tasks'][task]['position']
        del data[suite]['tasks'][task]

        for key in data[suite]['tasks'].keys():
            position = data[suite]['tasks'][key]['position']
            if position > deleted_position:
                data[suite]['tasks'][key]['position'] = position - 1
        # Save the updated array back to the file
        with open(get_resource_path('json/taskConfig.json'), 'w') as file:
            json.dump(data, file, indent=4)

    def save_task(self, variable, name: str, time: str, type: str, value: str):

        # Load the JSON data from a file
        with open(get_resource_path('json/taskConfig.json'), 'r', encoding='utf-8') as file:
            json_data = json.load(file)

        # Function to add a new task to a specific object
        def add_task_to_object(json_data: dict, object_name: str, task_name: str, time: str, type: str, value: str):
            tasks = json_data[object_name]['tasks']
            new_task = {
                'position': len(tasks) + 1,
                'time': time,
                'state': 'todo',
                'type': type,
                'value': value
            }
            json_data[object_name]['tasks'][task_name] = new_task

        name = name.replace(' ', '_')

        add_task_to_object(json_data, variable, name, time, type, value)

        # Save the updated JSON data back to the file
        with open(get_resource_path('json/taskConfig.json'), 'w', encoding='utf-8') as file:
            json.dump(json_data, file, indent=4)

    def edit_task(self, old_task_name, variable, name: str, time: str, type: str, value: str):

        # Load the JSON data from a file
        with open(get_resource_path('json/taskConfig.json'), 'r', encoding='utf-8') as file:
            json_data = json.load(file)

        name = name.replace(' ', '_')
        old_task_name = old_task_name.replace(' ', '_')
        json_data[variable]['tasks'][old_task_name]['time'] = time
        json_data[variable]['tasks'][old_task_name]['type'] = type
        json_data[variable]['tasks'][old_task_name]['value'] = value
        json_data[variable]['tasks'][name] = json_data[variable]['tasks'].pop(old_task_name)
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

    def save_colors(self, background_color: str,
                    primary_color: str,
                    button_color: str,
                    button_text_color: str,
                    active_button_color: str,
                    inactive_button_color: str,
                    success_color: str,
                    danger_color: str,
                    warning_color: str,
                    grid_color: str,
                    show_next_task_and_time: bool,
                    show_play_task: bool):
        with open(get_resource_path('json/settings.json'), 'r', encoding='utf-8') as file:
            settings = json.load(file)

        settings["backgroundColor"] = background_color
        settings["primaryColor"] = primary_color
        settings["buttonColor"] = button_color
        settings["buttonTextColor"] = button_text_color
        settings["activeButtonColor"] = active_button_color
        settings["inactiveButtonColor"] = inactive_button_color
        settings["successColor"] = success_color
        settings["dangerColor"] = danger_color
        settings["warningColor"] = warning_color
        settings["gridColor"] = grid_color
        settings["showNextTask"] = show_next_task_and_time
        settings["showPlayTaskButton"] = show_play_task

        with open(get_resource_path('json/settings.json'), 'w', encoding='utf-8') as file:
            json.dump(settings, file)

    def save_task_list(self, suite: str, tasks: dict):
        with open(get_resource_path('json/taskConfig.json'), 'r', encoding='utf-8') as file:
            data = json.load(file)
        data[suite]['tasks'] = tasks
        with open(get_resource_path('json/taskConfig.json'), 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4)
