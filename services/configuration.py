import json


class PsyTestProConfig:
    def __init__(self):
        self.experiments = None
        self.current_experiment = None
        self.current_tasks = None
        self.error_msg = ''

    def load_experiments(self):
        try:
            with open(f'json/experimentConfig.json', 'r', encoding='utf-8') as file:
                experiments = json.load(file)
                string = ','.join(str(e) for e in experiments)
                self.experiments = string.split(',')
        except FileNotFoundError:
            raise Exception(f'File Error: ./json/experimentConfig.json not found ')

    def load_experiment_tasks(self, experiment: str):
        self.error_msg = ''
        try:
            with open(f'json/taskConfig.json', 'r', encoding='utf-8') as file:
                tasks = json.load(file)
                if tasks.get(str(experiment) + '_schedule') is not None:
                    self.current_tasks = tasks.get(experiment + '_schedule').get('tasks')
                    self.current_experiment = str(experiment) + '_schedule'
                elif tasks.get(str(experiment) + '_list') is not None:
                    self.current_tasks = tasks.get(experiment + '_list').get('tasks')
                    self.current_experiment = str(experiment) + '_list'
                else:
                    self.error_msg = 'experimentNotFound'
        except FileNotFoundError:
            raise Exception(f'File Error: ./json/taskConfig.json not found')

    def save_experiment(self, experiment_name: str, schedule: bool):
        with open('json/experimentConfig.json', 'r') as file:
            original_experiments = json.load(file)

            if not experiment_name in original_experiments:
                # Add a new value to the array
                original_experiments.append(experiment_name)

        # Save the updated array back to the file
        with open('json/experimentConfig.json', 'w') as file:
            json.dump(original_experiments, file)

        # Load the original JSON from the file
        with open('json/taskConfig.json', 'r') as file:
            original_tasks = json.load(file)
        if schedule:
            experiment_name += '_schedule'
        else:
            experiment_name += '_list'

        if not experiment_name in original_tasks:
            # Add a new variable with an empty task object
            original_tasks[experiment_name] = {'tasks': {}}

        # Save the updated JSON back to the file
        with open('json/taskConfig.json', 'w') as file:
            json.dump(original_tasks, file, indent=4)

    def get_experiments(self):
        with open('json/taskConfig.json', 'r') as file:
            data = json.load(file)
        variable_names = data.keys()
        result = []
        for variable in variable_names:
            result.append(str(variable))

        return result

    def load_tasks_of_experiment(self, experiment: str):

        with open('json/taskConfig.json', 'r') as file:
            data = json.load(file)
        tasks = list(data[experiment]['tasks'].keys())

        return tasks

    def delete_task(self, experiment: str, task: str):
        if experiment == 'hab_variable_variable':
            experiment = 'hab_variable'

        with open('json/taskConfig.json', 'r') as file:
            data = json.load(file)
        del data[experiment]['tasks'][task]
        # Save the updated array back to the file
        with open('json/taskConfig.json', 'w') as file:
            json.dump(data, file, indent=4)

    def save_task(self, variable, name: str, time: str, type: str, value: str):

        # Load the JSON data from a file
        with open('json/taskConfig.json', 'r') as file:
            json_data = json.load(file)

        # Function to add a new task to a specific object
        def add_task_to_object(json_data: dict, object_name: str, task_name: str , time: str, type: str, value: str):
            new_task = {
                'time': time,
                'state': 'todo',
                'type': type,
                'value': value
            }
            json_data[object_name]['tasks'][task_name] = new_task
        name = name.replace(' ', '_')
        # Example usage
        add_task_to_object(json_data, variable, name, time, type, value)

        # Save the updated JSON data back to the file
        with open('json/taskConfig.json', 'w') as file:
            json.dump(json_data, file, indent=4)

    def load_custom_variables(self):
        with open('json/customVariables.json', 'r') as file:
            return json.load(file)

    def save_var(self, name: str):
        with open('json/customVariables.json', 'r') as file:
            data = json.load(file)
        if len(data) >= 3:
            return False
        else:
            data.append(name)
            with open('json/customVariables.json', 'w') as file:
                json.dump(data, file)
            return True

    def delete_var(self, name: str):
        with open('json/customVariables.json', 'r') as file:
            data = json.load(file)
        data.remove(name)
        with open('json/customVariables.json', 'w') as file:
            json.dump(data, file)

    def get_settings(self):
        with open(f'json/settings.json', 'r', encoding='utf-8') as file:
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
        with open(f'json/settings.json', 'r', encoding='utf-8') as file:
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

        with open('json/settings.json', 'w') as file:
            json.dump(settings, file)
