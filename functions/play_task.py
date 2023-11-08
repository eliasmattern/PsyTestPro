
from lib import GoNoGo_Real, start_real_nback, pvt, saliva, waking_eeg, text_screen, leeds, moodscales
import subprocess
from datetime import datetime

def play_tasks(eventName, participant_info, upcoming_event, schedule):
    match eventName:
        case "welcome":
            #process = subprocess.Popen("py ./lib/wakingEeg.py")
            #process.communicate()
            text_screen("Willkommen zur Studie", "Vielen Dank fürs Mitmachen")
        case "good_morn":
            text_screen("Guten Morgen", "")
        case "morn_sleep_diary" | "sleep_diary_expe":
            text_screen("Schlaftagebuch", "Es ist Zeit für das Schlaftagebuch! Ein/e Forscher/in wird dir helfen, das Schlaftagebuch zuführen.")
        case "leeds":
            leeds(participant_info["participant_id"], participant_info["week_no"], participant_info["experiment"])
        case "break_morn" | "breaktime":
            text_screen("Pause", "Es ist Zeit für eine Pause.")
        case "waking_eeg_morn" | "waking_eeg":
            waking_eeg()
        case "pvt_morn" | "pvt":
            # block = week number number = pvt number
            pvtNumber = ''.join([i for i in upcoming_event if i.isdigit()])
            pvt(participant_info["participant_id"], participant_info["experiment"], participant_info["week_no"], pvtNumber)
        case "saliva_morn" | "saliva":
            # kss = wie viele mal
            salivaNumber = ''.join([i for i in upcoming_event if i.isdigit()])
            saliva(participant_info["participant_id"], participant_info["experiment"], participant_info["week_no"], salivaNumber)
        case "teethbrushing":
            text_screen("Zähneputzen", "Du kannst jetzt deine Zähne in deinem Zimmer putzen.")
        case "mood_morn" | "mood":
            moodscales(participant_info["participant_id"], participant_info["week_no"], participant_info["experiment"])
        case "wof_morn" | "wof":
            text_screen("Glücksrad", "Ein/e Forscher/in wird kommen und dir helfen.")
        case "task_payment":
            text_screen("Zahlung", "Ein/e Forscher/in wird kommen und wird dich bezahlen.")
        case "gonogo_morn" | "gonogo":
            # block = week number number = gonogo number
            gonogo_number = ''.join([i for i in upcoming_event if i.isdigit()])
            GoNoGo_Real(participant_info["participant_id"], participant_info["experiment"], participant_info["week_no"], gonogo_number)
        case "nback_morn" | "nback":
            # study night se sr
            start_real_nback(participant_info["participant_id"], participant_info["experiment"], participant_info["week_no"], participant_info["experiment"])
        case "eeg_removal":
            text_screen("EEG entfernen", "Ein/e Forscher/in wird kommen und dir helfen.")
        case "breakfast_morn":
            text_screen("Frühstück", "Es ist Zeit für das Frühstück.")
        case "eeg_fitting":
            text_screen("EEG", "Jemand wird mit dir das EEG vorbereiten")
        case "dinner":
            text_screen("Abendessen", "Es ist Zeit für das Abendessen. Wir werden es dir bringen")
        case "capsule":
            text_screen("Kapsel", "Jemand wird dir die Kapsel bringen")
        case "bed_prep": 
            text_screen("Bettzeit", "Zeit, sich bettfertig zu machen")
        case "in_bed": 
            text_screen("Bettzeit", "Bitte begebe dich ins Bett")
        case "goodbye":
            text_screen("Vielen Dank fürs Mitmachen. Tschüss!", "")
        case _:
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