import shlex
import subprocess

import pygame.event


def execute_command(command: str, participant_info: dict, variables: dict) -> tuple[int, int]:
    command = command.format(id=participant_info['participant_id'],
                             suite=participant_info['suite'],
                             startTime=participant_info['start_time'],
                             timestamp=participant_info['timestamp'],
                             scriptCount=str(participant_info['script_count']),
                             **variables)
    try:
        process = subprocess.Popen(shlex.split(command, posix=False), shell=False)
        error = 0
        is_focused = True
        clock = pygame.time.Clock()
        while process.poll() is None or not is_focused:
            clock.tick(15)
            if process.stderr:
                error += 1
            for event in pygame.event.get():
                if event.type == pygame.WINDOWFOCUSLOST:
                    is_focused = False
                elif event.type == pygame.WINDOWFOCUSGAINED:
                    is_focused = True
        return_code = process.wait()
        return error, return_code
    except Exception as _:
        process = subprocess.Popen(shlex.split(command, posix=False), shell=True)
        error = 0
        is_focused = True
        while process.poll() is None or not is_focused:
            if process.stderr:
                error += 1
            for event in pygame.event.get():
                if event.type == pygame.WINDOWFOCUSLOST:
                    is_focused = False
                elif event.type == pygame.WINDOWFOCUSGAINED:
                    is_focused = True
        return_code = process.wait()
        return error, return_code
