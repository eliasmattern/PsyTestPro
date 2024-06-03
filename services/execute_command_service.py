import shlex
import subprocess


def execute_command(command: str, participant_info: dict, variables: dict) -> tuple[bytes, int]:
    command = command.format(id=participant_info['participant_id'],
                                                            experiment=participant_info['experiment'],
                                                            startTime=participant_info['start_time'],
                                                            timestamp=participant_info['timestamp'],
                                                            scriptCount=str(participant_info['script_count']),
                                                            **variables)
    try:
        process = subprocess.Popen(shlex.split(command, posix=False), shell=False)
        output, error = process.communicate()
        return_code = process.wait()
        return error, return_code
    except Exception as _:
        process = subprocess.Popen(shlex.split(command, posix=False), shell=True)
        output, error = process.communicate()
        return_code = process.wait()
        return error, return_code