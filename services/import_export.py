import pandas as pd
import json
import os

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
            for task_key, task_value in tasks.items():
                if "value" in task_value and isinstance(task_value['value'], dict):
                    row = [key, task_key, task_value['value'].get('title', ''), task_value['value'].get('description', '')]
                else:
                    row = [key, task_key, '', '']
                row += [task_value['time'], task_value['state'], task_value['type'], task_value['value']]
                file2_rows.append(row)

        file2_df = pd.DataFrame(file2_rows, columns=['Variable', "Task", 'Title', 'Description', 'Time', 'State', 'Type', 'Value'])

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
        file2_df = df[~df['Variable'].isna()]

        # Convert file2 DataFrame to dictionary
        file2_data = {}
        for _, row in file2_df.iterrows():
            variable = row['Variable']
            task_key = row.get('Task')

            time = row['Time']
            state = row['State']
            task_type = row['Type'] if not pd.isna(row['Type']) else ""
            title = row['Title']
            description = row['Description']
            value = row['Value'] if not pd.isna(row['Value']) else ""

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
                    task_info['value'] = ""

                file2_data[variable]['tasks'][task_key] = task_info

        # Remove empty 'tasks' entries
        for variable_data in file2_data.values():
            if not variable_data['tasks']:
                variable_data.pop('tasks')

        # Write to file1.json
        with open(self.output_file1_path, 'w') as file:
            json.dump(file1_data, file)

        # Write to file2.json
        with open(self.output_file2_path, 'w') as file:
            json.dump(file2_data, file, indent=4)


