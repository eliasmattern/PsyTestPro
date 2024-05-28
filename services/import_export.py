import json
import os
import shlex
import subprocess

import pandas as pd

from lib import text_screen
from services import PsyTestProConfig


class JSONToCSVConverter:
    def __init__(self, output_path):
        self.output_path = output_path
        self.experiment_config_path = './json/experimentConfig.json'
        self.task_config_path = './json/taskConfig.json'
        self.settings_path = './json/settings.json'
        self.custom_variables_path = './json/customVariables.json'

    def read_json(self, file_path):
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data

    def export_to_csv(self):
        directory = self.output_path.split(os.path.basename(self.output_path))[0]
        if not os.path.exists(directory):
            os.makedirs(directory)
        experiment_config_data = self.read_json(self.experiment_config_path)
        task_config_data = self.read_json(self.task_config_path)
        settings = self.read_json(self.settings_path)
        custom_variables = self.read_json(self.custom_variables_path)

        setting_df = pd.DataFrame()
        setting_df['settings_keys'] = settings.keys()
        setting_df['settings_values'] = settings.values()

        custom_variables_df = pd.DataFrame()
        custom_variables_df['custom_variables'] = custom_variables

        experiment_config_df = pd.DataFrame()
        experiment_config_df['experiment_config'] = experiment_config_data

        task_config_df = pd.DataFrame()
        tasks = []
        for experiment_name, value in task_config_data.items():
            for task_name, task_settings in value['tasks'].items():
                time = task_settings['time']
                state = task_settings['state']
                task_type = task_settings['type']
                value = task_settings['value'] + '|' if task_settings['type'] == 'command' \
                    else task_settings['value']['title'] + '|' + task_settings['value']['description']
                tasks.append('|'.join([experiment_name, task_name, time, state, task_type, value]))

        task_config_df['task_config'] = tasks

        final_df = pd.concat([setting_df, custom_variables_df, experiment_config_df, task_config_df], axis=1)
        final_df.to_excel(self.output_path, index=False)


class CSVToJSONConverter:
    def __init__(self, input_excel_path):
        self.input_excel_path = input_excel_path
        self.experiment_config_path = './json/experimentConfig.json'
        self.task_config_path = './json/taskConfig.json'
        self.settings_path = './json/settings.json'
        self.custom_variables_path = './json/customVariables.json'

    def convert_to_json(self):
        df = pd.read_excel(self.input_excel_path)
        headers = ['settings_keys', 'settings_values', 'custom_variables', 'experiment_config', 'task_config']
        if not all(header in df.keys() for header in headers):
            raise Exception('Invalid Excel file')

        settings = {}
        for setting_key, setting_value in zip(df['settings_keys'], df['settings_values']):
            if any(pd.isna(val) for val in [setting_key, setting_value]):
                break
            settings[setting_key] = setting_value

        with open(self.settings_path, 'w') as file:
            json.dump(settings, file, indent=2)

        custom_variables = []
        for custom_variable in df['custom_variables']:
            if any(pd.isna(val) for val in [custom_variable]):
                break
            custom_variables.append(custom_variable)

        with open(self.custom_variables_path, 'w') as file:
            json.dump(custom_variables, file)

        experiments = []
        for experiment in df['experiment_config']:
            if any(pd.isna(val) for val in [experiment]):
                break
            experiments.append(experiment)

        with open(self.experiment_config_path, 'w') as file:
            json.dump(experiments, file)

        tasks = {}

        for task in df['task_config']:
            if pd.isna(task):
                break
            experiment_name, task_name, time, state, task_type, value, desc = task.split('|')

            if experiment_name not in tasks.keys():
                tasks[experiment_name] = {'tasks': {}}

            if task_type == 'command':
                task_value = value
            else:
                task_value = {'title': value, 'description': desc}
            tasks[experiment_name]['tasks'][task_name] = {'time': time, 'state': state, 'type': task_type,
                                                          "value": task_value}

        with open(self.task_config_path, 'w') as file:
            json.dump(tasks, file, indent=4)


class ImportTasksService:
    def __init__(self, translate_service):
        self.translate_service = translate_service

    def save_tasks(self, df, experiment_name, show_preview):
        errors = []
        if show_preview:
            for index, row in df.iterrows():
                if not isinstance(row['command'], float):
                    result = self.preview_task(command=row['command'])
                    if not result:
                        errors.append(row["task_name"])
                elif not isinstance(row['title'], float):
                    result = self.preview_task(title=row['title'], description=row['description'])
                    if not result:
                        errors.append(row["task_name"])
            if len(errors) > 0:
                return errors
        with open('./json/taskConfig.json', 'r') as file:
            data = json.load(file)
        if experiment_name in data.keys():
            last_minute = None
            for index, row in df.iterrows():
                task_name = str(row["task_name"]).replace(' ', '_')
                minutes = row['minutes'] + last_minute if last_minute is not None else 0
                print(minutes)
                last_minute = last_minute + row['minutes'] if last_minute is not None else minutes
                hours = minutes // 60
                minutes %= 60
                time = '{:02d}:{:02d}:00'.format(int(hours), int(minutes))
                if not isinstance(row['command'], float):
                    data[experiment_name]['tasks'][task_name] = {'time': time, 'state': 'todo', 'type': 'command',
                                                                 'value': row['command']}
                elif not isinstance(row['title'], float):
                    description = row['description'] if not isinstance(row['description'], float) else ''
                    data[experiment_name]['tasks'][task_name] = {'time': time, 'state': 'todo', 'type': 'text',
                                                                 'value': {'title': row['title'],
                                                                           'description': description}}
        else:
            return errors

        with open('./json/taskConfig.json', 'w') as file:
            json.dump(data, file, indent=4)

    def preview_task(self, command=None, title=None, description=None):
        custom_variables = PsyTestProConfig().load_custom_variables()
        participant_info = {
            'participant_id': 'VARIABLE_ID',
            'experiment': 'VARIABLE_EXPERMENT',
            'start_time': 'VARIABLE_STARTTIME',
            'timestamp': 'VARIABLE_TIMESTAMP'
        }

        variables = {}

        for value in custom_variables:
            variables[value] = 'CUSTOM_VARIABLE'
        if command:
            try:
                formatted_command = command.format(id=participant_info['participant_id'],
                                                   experiment=participant_info['experiment'],
                                                   startTime=participant_info['start_time'],
                                                   timestamp=participant_info['timestamp'],
                                                   **variables)
                process = subprocess.Popen(shlex.split(formatted_command))
                output, error = process.communicate()
                return_code = process.wait()
                print(return_code)
                if return_code != 0:
                    raise Exception(f"Command failed with return code {return_code}, Error: {error}")
                return True
            except Exception as e:
                print(e)
                return False
        else:
            try:
                title = title.format(id=participant_info['participant_id'],
                                     experiment=participant_info['experiment'],
                                     startTime=participant_info['start_time'],
                                     timestamp=participant_info['timestamp'],
                                     **variables)

                if isinstance(description, float):
                    description = ''

                description = description.format(id=participant_info['participant_id'],
                                                 experiment=participant_info['experiment'],
                                                 startTime=participant_info['start_time'],
                                                 timestamp=participant_info['timestamp'],
                                                 **variables)

                text_screen(title, description, self.translate_service.get_translation('escToReturn'))
                return True
            except Exception as e:
                print(e)
                return False

    def import_tasks(self, experiment_name, file_path, show_preview):
        try:
            file_name, file_extension = os.path.splitext(file_path)
            print(file_path)
            if file_extension == '.csv':
                df = pd.read_csv(file_path)
                self.save_tasks(df, experiment_name, show_preview)
            elif file_extension == '.xlsx':
                df = pd.read_excel(file_path)
                self.save_tasks(df, experiment_name, show_preview)
            else:
                raise Exception('Wrong file format. Only .csv and .xlsx files are supported.')
        except FileNotFoundError as e:
            print(e)
