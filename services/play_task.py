import webbrowser
from datetime import datetime, timedelta

import pandas as pd
import pygame

from app_types import Task
from lib import text_screen
from .PathService import get_resource_path
from .TranslateService import TranslateService
from .execute_command_service import execute_command


def save_task_info(filename: str, task_name: str, task_start_time: str, task_end_time: str, state: str):
    df = pd.read_excel(get_resource_path('./logs/' + filename, True))
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
    final_df.to_excel(get_resource_path('./logs/' + filename, True), index=False)


def play_tasks(filename: str, participant_info: dict, upcoming_event: Task, schedule: list[Task],
               translate_service: TranslateService, custom_variables: dict):
    task_start_time = str(datetime.now())
    if not custom_variables:
        custom_variables = {}
    if upcoming_event.task_type == 'text':
        try:
            now = datetime.now()
            formatted_timestamp = now.strftime('%Y.%m.%d %H:%M:%S')
            title = upcoming_event.value['title']
            description = upcoming_event.value['description']

            title = title.format(id=participant_info['participant_id'],
                                 suite=participant_info['suite'],
                                 startTime=participant_info['start_time'],
                                 timestamp=formatted_timestamp,
                                 scriptCount='',
                                 **custom_variables)

            description = description.format(id=participant_info['participant_id'],
                                             suite=participant_info['suite'],
                                             startTime=participant_info['start_time'],
                                             timestamp=formatted_timestamp,
                                             scriptCount='',
                                             **custom_variables)
            text_screen(title, description, translate_service.get_translation('escToReturn'))
            task_end_time = str(datetime.now())

            save_task_info(filename, upcoming_event.name, task_start_time, task_end_time, 'Success')
            return True
        except Exception as e:
            task_end_time = str(datetime.now())
            save_task_info(filename, upcoming_event.name, task_start_time, task_end_time, e)
            return False

    elif upcoming_event.task_type == 'command':
        try:
            command = upcoming_event.value
            script_count = 0
            if '{scriptCount}' in command:
                schedule = sorted(schedule, key=lambda task: task.position)
                task_command_pairs = [(task.id, task.value) for task in schedule if
                                      task.task_type == 'command' and task.value == upcoming_event.value]
                for task, _ in task_command_pairs:
                    script_count += 1
                    if task == upcoming_event.id:
                        break
            participant_info['script_count'] = script_count
            error, return_code = execute_command(command, participant_info, custom_variables)

            if return_code != 0:
                raise Exception(f"Command failed with return code {return_code}, Error: {error}")
            task_end_time = str(datetime.now())

            save_task_info(filename, upcoming_event.name, task_start_time, task_end_time, 'Success')
            return True
        except Exception as e:
            task_end_time = str(datetime.now())
            save_task_info(filename, upcoming_event.name, task_start_time, task_end_time, e)
            return False

    elif upcoming_event.task_type == 'url':
        try:
            url = upcoming_event.value
            script_count = 0

            if '{scriptCount}' in url:
                task_url_pairs = [(task.name, task.value) for task in schedule if
                                  task.task_type == 'command' and task.value == upcoming_event.value]

                for task, _ in task_url_pairs:
                    script_count += 1
                    if task == upcoming_event:
                        break
            participant_info['script_count'] = script_count
            url = url.format(id=participant_info['participant_id'],
                             suite=participant_info['suite'],
                             startTime=participant_info['start_time'],
                             timestamp=participant_info['timestamp'],
                             scriptCount=str(participant_info['script_count']),
                             **custom_variables)
            is_focused = pygame.display.get_active()
            clock = pygame.time.Clock()
            start = datetime.now()
            webbrowser.open(url)
            while not is_focused or datetime.now() < start + timedelta(seconds=2):
                clock.tick(15)
                for event in pygame.event.get():
                    if event.type == pygame.WINDOWFOCUSLOST:
                        is_focused = False
                    elif event.type == pygame.WINDOWFOCUSGAINED:
                        is_focused = True
            task_end_time = str(datetime.now())

            save_task_info(filename, upcoming_event.name, task_start_time, task_end_time, 'Success')
            return True
        except Exception as e:
            task_end_time = str(datetime.now())
            save_task_info(filename, upcoming_event.name, task_start_time, task_end_time, e)
            return False
