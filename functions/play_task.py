
from lib import text_screen
import subprocess
from datetime import datetime

def play_tasks(participant_info, upcoming_event, schedule):
    if schedule[upcoming_event]["type"] == "text":
        now = datetime.now()
        formatted_timestamp = now.strftime("%Y.%m.%d %H:%M:%S")
        title = schedule[upcoming_event]["value"]["title"]
        description = schedule[upcoming_event]["value"]["description"]

        title = title.format(id = participant_info["participant_id"], 
                     timeOfDay = participant_info["time_of_day"], 
                     experiment = participant_info["experiment"], 
                     weekNo = participant_info["week_no"], 
                     startTime = participant_info["start_time"], 
                     timestamp = formatted_timestamp)

        description= description.format(id = participant_info["participant_id"], 
                     timeOfDay = participant_info["time_of_day"], 
                     experiment = participant_info["experiment"], 
                     weekNo = participant_info["week_no"], 
                     startTime = participant_info["start_time"], 
                     timestamp = formatted_timestamp)   
        text_screen(title, description)
    elif schedule[upcoming_event]["type"] == "command":
        now = datetime.now()
        formatted_timestamp = now.strftime("%Y.%m.%d %H:%M:%S")
        command = schedule[upcoming_event]["value"] 
        command = command.format(id = participant_info["participant_id"], 
                     timeOfDay = participant_info["time_of_day"], 
                     experiment = participant_info["experiment"], 
                     weekNo = participant_info["week_no"], 
                     startTime = participant_info["start_time"], 
                     timestamp = formatted_timestamp)
        process = subprocess.Popen(command)
        process.communicate()