import json
import os

import pandas as pd
import math
import subprocess

from lib import text_screen
from services import PsyTestProConfig
import shlex


class JSONToCSVConverter:
    def __init__(self, file1_path, file2_path, output_path):
        self.file1_path = file1_path
        self.file2_path = file2_path
        self.output_path = output_path

    def read_json(self, file_path):
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data

    def export_to_csv(self):
        directory = self.output_path.split(os.path.basename(self.output_path))[0]
        if not os.path.exists(directory):
            os.makedirs(directory)
        file1_data = self.read_json(self.file1_path)
        file2_data = self.read_json(self.file2_path)
        # Create DataFrame for file2
        file2_rows = []
        for key, value in file2_data.items():
            tasks = value.get('tasks', {})
            if len(tasks) == 0:
                file2_rows.append([key])
            for task_key, task_value in tasks.items():
                if 'value' in task_value and isinstance(task_value['value'], dict):
                    row = [key, task_key, task_value['value'].get('title', ''),
                           task_value['value'].get('description', '')]
                else:
                    row = [key, task_key, '', '']
                row += [task_value['time'], task_value['state'], task_value['type'], task_value['value']]
                file2_rows.append(row)
        file2_df = pd.DataFrame(file2_rows,
                                columns=['Variable', 'Task', 'Title', 'Description', 'Time', 'State', 'Type', 'Value'])
        # Create DataFrame for file1
        file1_df = pd.DataFrame({'File 1': file1_data})

        # Concatenate DataFrames
        result_df = pd.concat([file1_df, file2_df], ignore_index=True)

        # Write to CSV
        result_df.to_csv(self.output_path, index=False)


class CSVToJSONConverter:
    def __init__(self, input_csv_path, output_file1_path, output_file2_path):
        self.input_csv_path = input_csv_path
        self.output_file1_path = output_file1_path
        self.output_file2_path = output_file2_path

    def convert_to_json(self):
        df = pd.read_csv(self.input_csv_path)

        # Split DataFrames for file1 and file2
        file1_data = df[df['Variable'].isna()]['File 1'].tolist()
        file1_result = []
        for data in file1_data:
            if isinstance(data, float):
                if data.is_integer():
                    file1_result.append(str(int(data)))
                else:
                    file1_result.append(str(data))
            else:
                file1_result.append(str(data))
        file2_df = df[~df['Variable'].isna()]

        # Convert file2 DataFrame to dictionary
        file2_data = {}
        for _, row in file2_df.iterrows():
            variable = row['Variable']
            task_key = row.get('Task')

            time = row['Time']
            state = row['State']
            task_type = row['Type'] if not pd.isna(row['Type']) else ''
            title = row['Title']
            description = row['Description']
            value = row['Value'] if not pd.isna(row['Value']) else ''

            if variable not in file2_data:
                file2_data[variable] = {'tasks': {}}

            if task_key:  # Ensure task_key is not empty
                task_info = {
                    'time': time,
                    'state': state,
                    'type': task_type
                }

                if task_type == 'text':
                    task_info['value'] = {
                        'title': title,
                        'description': description
                    }
                elif task_type == 'command':
                    task_info['value'] = value
                else:
                    task_info['value'] = ''

                file2_data[variable]['tasks'][task_key] = task_info

        # Remove empty 'tasks' entries
        for variable_data in file2_data.values():
            if not variable_data['tasks']:
                variable_data.pop('tasks')
        for key, value in file2_data.items():
            experiment = file2_data.get(key, {})
            tasks = experiment.get('tasks')
            tasks_without_nan = {name: task for name, task in tasks.items() if
                                 isinstance(name, float) and not math.isnan(name) or isinstance(name, str)}
            file2_data[key]['tasks'] = tasks_without_nan

        # Write to file1.json
        with open(self.output_file1_path, 'w') as file:
            json.dump(file1_result, file)

        # Write to file2.json
        with open(self.output_file2_path, 'w') as file:
            json.dump(file2_data, file, indent=4)


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
                                                       'value': {'title': row['title'], 'description': description}}
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
