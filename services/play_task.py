import subprocess
from datetime import datetime
from lib import text_screen
import pandas as pd
import shlex
from services import TranslateService, execute_command


def save_task_info(filename: str, task_name: str, task_start_time: str, task_end_time: str, state: str):
        df = pd.read_excel('./experiments/' + filename)
        new_df = {}

        if 'task' in df:
            info_df = pd.DataFrame(data=df['info'])
            info_df.insert(1, 'value', df['value'])

            task_df = pd.DataFrame(data=df['task'])
            task_df.insert(1, 'start_time', df['start_time'])
            task_df.insert(2, 'end_time', df['end_time'])
            task_df.insert(3, 'state', df['state'])
            task_df = task_df.dropna(how='all', )
            task_df = task_df.reset_index()
            task_df = task_df.drop(columns=['index'], axis=1)
            task_df.loc[len(task_df)] = [task_name, task_start_time, task_end_time, state]
            final_df = pd.concat([info_df, task_df], axis=1)
        else:
            new_df['task'] = [task_name]
            new_df['start_time'] = [task_start_time]
            new_df['end_time'] = [task_end_time]
            new_df['state'] = [state]
            new_df = pd.DataFrame(data=new_df)
            final_df = pd.concat([df, new_df], axis=1)
        final_df.to_excel('./experiments/' + filename, index=False)


def play_tasks(filename: str, participant_info: dict, upcoming_event: str, schedule: dict, translate_service: TranslateService, custom_variables: dict):
    task_start_time = str(datetime.now())
    if not custom_variables:
        custom_variables = {}
    if schedule[upcoming_event]['type'] == 'text':
        try:
            now = datetime.now()
            formatted_timestamp = now.strftime('%Y.%m.%d %H:%M:%S')
            title = schedule[upcoming_event]['value']['title']
            description = schedule[upcoming_event]['value']['description']

            title = title.format(id=participant_info['participant_id'],
                                 experiment=participant_info['experiment'],
                                 startTime=participant_info['start_time'],
                                 timestamp=formatted_timestamp,
                                 scriptCount='',
                                 **custom_variables)

            description = description.format(id=participant_info['participant_id'],
                                             experiment=participant_info['experiment'],
                                             startTime=participant_info['start_time'],
                                             timestamp=formatted_timestamp,
                                             scriptCount='',
                                             **custom_variables)
            text_screen(title, description, translate_service.get_translation('escToReturn'))
            task_end_time = str(datetime.now())

            save_task_info(filename, upcoming_event, task_start_time, task_end_time, 'Success')
            return True
        except Exception as e:
            task_end_time = str(datetime.now())
            save_task_info(filename, upcoming_event, task_start_time, task_end_time, e)
            return False

    elif schedule[upcoming_event]['type'] == 'command':
        try:
            now = datetime.now()
            formatted_timestamp = now.strftime('%Y.%m.%d %H:%M:%S')
            command = schedule[upcoming_event]['value']
            script_count = 0

            if '{scriptCount}' in command:
                task_command_pairs = [(task_name, task_info['value']) for task_name, task_info in schedule.items() if task_info['type'] == 'command' and  task_info['value'] == schedule[upcoming_event]['value']]

                for task, _ in task_command_pairs:
                    script_count += 1
                    if task == upcoming_event:
                        break
            error, return_code = execute_command(command, participant_info, custom_variables)
            
            if return_code != 0:
                raise Exception(f"Command failed with return code {return_code}, Error: {error}")
            task_end_time = str(datetime.now())

            save_task_info(filename, upcoming_event, task_start_time, task_end_time, 'Success')
            return True
        except Exception as e:
            task_end_time = str(datetime.now())
            save_task_info(filename, upcoming_event, task_start_time, task_end_time, e)
            return False
