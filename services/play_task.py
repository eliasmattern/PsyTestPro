
from lib import text_screen
import subprocess
from datetime import datetime

def play_tasks(participant_info, upcoming_event, schedule, translate_service, custom_variables):
    if not custom_variables:
        custom_variables = {}
    if schedule[upcoming_event]["type"] == "text":
        now = datetime.now()
        formatted_timestamp = now.strftime("%Y.%m.%d %H:%M:%S")
        title = schedule[upcoming_event]["value"]["title"]
        description = schedule[upcoming_event]["value"]["description"]
        
        title = title.format(id = participant_info["participant_id"], 
                     experiment = participant_info["experiment"], 
                     startTime = participant_info["start_time"], 
                     timestamp = formatted_timestamp,
                     **custom_variables)

        description= description.format(id = participant_info["participant_id"], 
                     experiment = participant_info["experiment"], 
                     startTime = participant_info["start_time"], 
                     timestamp = formatted_timestamp,
                     **custom_variables)   
        text_screen(title, description, translate_service.get_translation("escToReturn"))
    elif schedule[upcoming_event]["type"] == "command":
        now = datetime.now()
        formatted_timestamp = now.strftime("%Y.%m.%d %H:%M:%S")
        command = schedule[upcoming_event]["value"] 
        command = command.format(id = participant_info["participant_id"], 
                     experiment = participant_info["experiment"], 
                     startTime = participant_info["start_time"], 
                     timestamp = formatted_timestamp,
                     **custom_variables)
        process = subprocess.Popen(command)
        process.communicate()