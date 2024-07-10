import json
import os
import webbrowser

import pandas as pd

from lib import text_screen

from .configuration import PsyTestProConfig
from .TranslateService import TranslateService
from .execute_command_service import execute_command
from .PathService import get_resource_path


class JSONToCSVConverter:
    def __init__(self, output_path: str):
        self.output_path = output_path
        self.suite_config_path = get_resource_path('./json/suiteConfig.json')
        self.task_config_path = get_resource_path('./json/taskConfig.json')
        self.settings_path = get_resource_path('./json/settings.json')
        self.custom_variables_path = get_resource_path('./json/customVariables.json')

    def read_json(self, file_path: str):
        with open(get_resource_path(file_path), 'r') as file:
            data = json.load(file)
        return data

    def export_to_csv(self):
        directory = self.output_path.split(os.path.basename(self.output_path))[0]
        if not os.path.exists(directory):
            os.makedirs(directory)
        suite_config_data = self.read_json(self.suite_config_path)
        task_config_data = self.read_json(self.task_config_path)
        settings = self.read_json(self.settings_path)
        custom_variables = self.read_json(self.custom_variables_path)

        setting_df = pd.DataFrame()
        setting_df['settings_keys'] = settings.keys()
        setting_df['settings_values'] = settings.values()

        custom_variables_df = pd.DataFrame()
        custom_variables_df['custom_variables'] = custom_variables

        suite_config_df = pd.DataFrame()
        suite_list = ['\'' + str(exp) for exp in suite_config_data]
        suite_config_df['suite_config'] = suite_list

        task_config_df = pd.DataFrame()
        tasks = []
        for suite_name, value in task_config_data.items():
            if len(value['tasks']) > 0:
                for task_name, task_settings in value['tasks'].items():
                    time = task_settings['time']
                    state = task_settings['state']
                    task_type = task_settings['type']
                    task_position = str(task_settings['position'])
                    value = task_settings['value'] + '|' if task_settings['type'] == 'command' or task_settings[
                        'type'] == 'url' \
                        else task_settings['value']['title'] + '|' + task_settings['value']['description']
                    tasks.append('|'.join([suite_name, task_name, time, state, task_type, value, task_position]))
            else:
                tasks.append('|'.join([suite_name, '', '', '', '', '', '', '']))
        task_config_df['task_config'] = tasks

        final_df = pd.concat([setting_df, custom_variables_df, suite_config_df, task_config_df], axis=1)
        final_df.to_excel(self.output_path, index=False)


class CSVToJSONConverter:
    def __init__(self, input_excel_path: str):
        self.input_excel_path = input_excel_path
        self.suite_config_path = get_resource_path('./json/suiteConfig.json')
        self.task_config_path = get_resource_path('./json/taskConfig.json')
        self.settings_path = get_resource_path('./json/settings.json')
        self.custom_variables_path = get_resource_path('./json/customVariables.json')

    def convert_to_json(self):
        df = pd.read_excel(self.input_excel_path)
        headers = ['settings_keys', 'settings_values', 'custom_variables', 'suite_config', 'task_config']
        if not all(header in df.keys() for header in headers):
            raise Exception('Invalid Excel file')

        settings = {}
        for setting_key, setting_value in zip(df['settings_keys'], df['settings_values']):
            if any(pd.isna(val) for val in [setting_key, setting_value]):
                break
            settings[setting_key] = setting_value

        with open(get_resource_path(self.settings_path), 'w') as file:
            json.dump(settings, file, indent=2)

        custom_variables = []
        for custom_variable in df['custom_variables']:
            if any(pd.isna(val) for val in [custom_variable]):
                break
            custom_variables.append(custom_variable)

        with open(get_resource_path(self.custom_variables_path), 'w') as file:
            json.dump(custom_variables, file)

        suites = []
        for suite in df['suite_config']:
            if any(pd.isna(val) for val in [suite]):
                break
            if suite.startswith('\''):
                suite = suite.replace('\'', '', 1)
            suites.append(suite)

        with open(get_resource_path(self.suite_config_path), 'w') as file:
            json.dump(suites, file)

        tasks = {}

        for task in df['task_config']:
            if pd.isna(task):
                break
            suite_name, task_name, time, state, task_type, value, desc, position = task.split('|')

            if suite_name not in tasks.keys():
                tasks[suite_name] = {'tasks': {}}
            if task_name == '':
                continue
            if task_type == 'command' or task_type == 'url':
                task_value = value
            else:
                task_value = {'title': value, 'description': desc}
            tasks[suite_name]['tasks'][task_name] = {'position': int(position), 'time': time, 'state': state,
                                                     'type': task_type, "value": task_value}

        with open(get_resource_path(self.task_config_path), 'w') as file:
            json.dump(tasks, file, indent=4)


class ImportTasksService:
    def __init__(self, translate_service: TranslateService):
        self.translate_service = translate_service

    def save_tasks(self, df, suite_name, show_preview):
        error = ''
        if show_preview:
            for _, row in df.iterrows():
                if not isinstance(row['command'], float):
                    result = self.preview_task(command=row['command'])
                    if not result:
                        error = row["task_name"]
                        break
                elif not isinstance(row['title'], float):
                    result = self.preview_task(title=row['title'], description=row['description'])
                    if not result:
                        error = row["task_name"]
                        break
                elif not isinstance(row['url'], float):
                    result = self.preview_task(url=row['url'])
                    if not result:
                        error = row["task_name"]
                        break
            if len(error) > 0:
                return False, 'importTaskFailed', error
        with open(get_resource_path('./json/taskConfig.json'), 'r') as file:
            data = json.load(file)
        if suite_name in data.keys():
            position = len(data[suite_name]['tasks']) + 1
            for _, row in df.iterrows():
                keys = data[suite_name]['tasks'].keys()
                numeric_keys = [eval(i) for i in keys]
                task_id = max(numeric_keys) + 1
                task_name = str(row["task_name"])
                minutes = row['duration in minutes']
                hours = minutes // 60
                minutes %= 60
                time = '{:02d}:{:02d}:00'.format(int(hours), int(minutes))
                if not isinstance(row['command'], float) or not isinstance(row['url'], float):
                    task_type = 'command' if not isinstance(row['command'], float) else 'url'
                    value = row['command'] if not isinstance(row['command'], float) else row['url']
                    data[suite_name]['tasks'][task_id] = {'is_group': False, 'name': task_name, 'time': time, 'state': 'todo',
                                                            'type': task_type, 'value': value, 'position': position}
                elif not isinstance(row['title'], float):
                    description = row['description'] if not isinstance(row['description'], float) else ''
                    data[suite_name]['tasks'][task_id] = {'is_group': False, 'name': task_name, 'time': time, 'state': 'todo',
                                                            'type': 'text', 'value': {'title': row['title'],
                                                                                      'description': description},
                                                            'position': position}
                position += 1
        else:
            return False, 'importTasksFailed'

        with open(get_resource_path('./json/taskConfig.json'), 'w') as file:
            json.dump(data, file, indent=4)
        return True, 'taskImportSuccessful'

    def preview_task(self, command=None, title=None, description=None, url=None):
        custom_variables = PsyTestProConfig().load_custom_variables()
        participant_info = {
            'participant_id': 'VARIABLE_ID',
            'suite': 'VARIABLE_SUITE',
            'start_time': 'VARIABLE_STARTTIME',
            'timestamp': 'VARIABLE_TIMESTAMP',
            'script_count': 0
        }

        variables = {}

        for value in custom_variables:
            variables[value] = 'CUSTOM_VARIABLE'
        if command:
            try:
                error, return_code = execute_command(command, participant_info, variables)
                if return_code != 0:
                    raise Exception(f"Command failed with return code {return_code}, Error: {error}")
                return True
            except Exception as e:
                print(e)
                return False
        elif url:
            try:
                url = url.format(id=participant_info['participant_id'],
                                 suite=participant_info['suite'],
                                 startTime=participant_info['start_time'],
                                 timestamp=participant_info['timestamp'],
                                 scriptCount='',
                                 **variables)

                webbrowser.open(url)

                return True
            except Exception as e:
                print(e)
                return False
        else:
            try:
                title = title.format(id=participant_info['participant_id'],
                                     suite=participant_info['suite'],
                                     startTime=participant_info['start_time'],
                                     timestamp=participant_info['timestamp'],
                                     scriptCount='',
                                     **variables)

                if isinstance(description, float):
                    description = ''

                description = description.format(id=participant_info['participant_id'],
                                                 suite=participant_info['suite'],
                                                 startTime=participant_info['start_time'],
                                                 timestamp=participant_info['timestamp'],
                                                 scriptCount='',
                                                 **variables)

                text_screen(title, description, self.translate_service.get_translation('escToReturn'))
                return True
            except Exception as e:
                print(e)
                return False

    def import_tasks(self, suite_name: str, file_path: str, show_preview: bool):
        try:
            file_name, file_extension = os.path.splitext(file_path)
            print(file_path)
            if file_extension == '.csv':
                df = pd.read_csv(file_path)
                result = self.save_tasks(df, suite_name, show_preview)
                return result
            elif file_extension == '.xlsx':
                df = pd.read_excel(file_path)
                result = self.save_tasks(df, suite_name, show_preview)
                return result
            else:
                print('Wrong file format. Only .csv and .xlsx files are supported.')
                return False, 'wrongFileFormatForTaskImport'

        except FileNotFoundError as e:
            print(e)
            return False, 'importTasksFailed'
