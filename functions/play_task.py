
from lib import GoNoGo_Real, start_real_nback, pvt, saliva, waking_eeg, text_screen, leeds, moodscales
import subprocess
import pandas as pd
from datetime import datetime

def save_task_info(filename, task_name, task_start_time, task_end_time, state):
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


def play_tasks(eventName, participant_info, upcoming_event, schedule, filename):
    result = True
    task_start_time = str(datetime.now())

    match eventName:
        case "welcome":
            try:
                text_screen("Willkommen zur Studie", "Vielen Dank fürs Mitmachen")
                task_end_time = str(datetime.now())
                save_task_info(filename, upcoming_event, task_start_time, task_end_time, 'Success')
            except Exception as e:
                task_end_time = str(datetime.now())
                save_task_info(filename, upcoming_event, task_start_time, task_end_time, e)
        case "good_morn":
            try:
                text_screen("Guten Morgen", "")
                task_end_time = str(datetime.now())
                save_task_info(filename, upcoming_event, task_start_time, task_end_time, 'Success')
            except Exception as e:
                task_end_time = str(datetime.now())
                save_task_info(filename, upcoming_event, task_start_time, task_end_time, e)
        case "morn_sleep_diary" | "sleep_diary_expe":
            try:
                text_screen("Schlaftagebuch", "Es ist Zeit für das Schlaftagebuch! Ein/e Versuchsleiter/in wird dir helfen, das Schlaftagebuch auszfüllen.")
                task_end_time = str(datetime.now())
                save_task_info(filename, upcoming_event, task_start_time, task_end_time, 'Success')
            except Exception as e:
                task_end_time = str(datetime.now())
                save_task_info(filename, upcoming_event, task_start_time, task_end_time, e)
        case "expectancy_questionnaire":
            try:
                text_screen("Erwartungsfrabogen", "Bitte fülle auch noch diesen Erwartungs-Fragebogen aus. Ein/e Versuchsleiter/in kommt gleich.")
                task_end_time = str(datetime.now())
                save_task_info(filename, upcoming_event, task_start_time, task_end_time, 'Success')
            except Exception as e:
                task_end_time = str(datetime.now())
                save_task_info(filename, upcoming_event, task_start_time, task_end_time, e)
        case "leeds":
            try:
                result = leeds(participant_info["participant_id"], participant_info["week_no"], participant_info["experiment"])
                if not result:
                    raise Exception('Task wurde abgebrochen')
                task_end_time = str(datetime.now())
                save_task_info(filename, upcoming_event, task_start_time, task_end_time, 'Success')
            except Exception as e:
                task_end_time = str(datetime.now())
                save_task_info(filename, upcoming_event, task_start_time, task_end_time, e)
        case "break_morn" | "breaktime":
            try:
                text_screen("Pause", "Es ist Zeit für eine Pause.")
                task_end_time = str(datetime.now())
                save_task_info(filename, upcoming_event, task_start_time, task_end_time, 'Success')
            except Exception as e:
                task_end_time = str(datetime.now())
                save_task_info(filename, upcoming_event, task_start_time, task_end_time, e)
        case "waking_eeg_morn" | "waking_eeg":
            try:
                waking_eeg()
                task_end_time = str(datetime.now())
                save_task_info(filename, upcoming_event, task_start_time, task_end_time, 'Success')
            except Exception as e:
                task_end_time = str(datetime.now())
                save_task_info(filename, upcoming_event, task_start_time, task_end_time, e)
        case "pvt_morn" | "pvt":
            try:
                # block = week number number = pvt number
                pvtNumber = ''.join([i for i in upcoming_event if i.isdigit()])
                result = pvt(participant_info["participant_id"], participant_info["experiment"], participant_info["week_no"], pvtNumber)
                if not result:
                    raise Exception('Task wurde abgebrochen')
                task_end_time = str(datetime.now())
                save_task_info(filename, upcoming_event, task_start_time, task_end_time, 'Success')
            except Exception as e:
                task_end_time = str(datetime.now())
                save_task_info(filename, upcoming_event, task_start_time, task_end_time, e)
        case "saliva_morn" | "saliva":
            try:
                # kss = wie viele mal
                salivaNumber = ''.join([i for i in upcoming_event if i.isdigit()])
                result = saliva(participant_info["participant_id"], participant_info["experiment"], participant_info["week_no"], salivaNumber)
                if not result:
                    raise Exception('KSS wurde abgebrochen ohne den Fragebogen auszufüllen')
                task_end_time = str(datetime.now())
                save_task_info(filename, upcoming_event, task_start_time, task_end_time, 'Success')
            except Exception as e:
                task_end_time = str(datetime.now())
                save_task_info(filename, upcoming_event, task_start_time, task_end_time, e)
        case "teethbrushing":
            try:
                text_screen("Zähneputzen", "Du kannst jetzt deine Zähne in deinem Zimmer putzen.")
                task_end_time = str(datetime.now())
                save_task_info(filename, upcoming_event, task_start_time, task_end_time, 'Success')
            except Exception as e:
                task_end_time = str(datetime.now())
                save_task_info(filename, upcoming_event, task_start_time, task_end_time, e)
        case "mood_morn" | "mood":
            try:
                moodscaleNumber = ''.join([i for i in upcoming_event if i.isdigit()])
                result = moodscales(participant_info["participant_id"], participant_info["week_no"], participant_info["experiment"], moodscaleNumber)
                if not result:
                    raise Exception('Task wurde abgebrochen')
                task_end_time = str(datetime.now())
                save_task_info(filename, upcoming_event, task_start_time, task_end_time, 'Success')
            except Exception as e:
                task_end_time = str(datetime.now())
                save_task_info(filename, upcoming_event, task_start_time, task_end_time, e)
        case "wof_morn" | "wof":
            try:
                text_screen("Glücksrad", "Ein/e Versuchsleiter/in wird kommen und dir helfen.")
                task_end_time = str(datetime.now())
                save_task_info(filename, upcoming_event, task_start_time, task_end_time, 'Success')
            except Exception as e:
                task_end_time = str(datetime.now())
                save_task_info(filename, upcoming_event, task_start_time, task_end_time, e)
        case "task_payment":
            try:
                text_screen("Zahlung", "Ein/e Versuchsleiter/in wird kommen und wird dich bezahlen.")
                task_end_time = str(datetime.now())
                save_task_info(filename, upcoming_event, task_start_time, task_end_time, 'Success')
            except Exception as e:
                task_end_time = str(datetime.now())
                save_task_info(filename, upcoming_event, task_start_time, task_end_time, e)
        case "gonogo_morn" | "gonogo":
            try:
                # block = week number number = gonogo number
                gonogo_number = ''.join([i for i in upcoming_event if i.isdigit()])
                result = GoNoGo_Real(participant_info["participant_id"], participant_info["experiment"], participant_info["week_no"], gonogo_number)
                if not result:
                    raise Exception('Task wurde abgebrochen')
                task_end_time = str(datetime.now())
                save_task_info(filename, upcoming_event, task_start_time, task_end_time, 'Success')
            except Exception as e:
                task_end_time = str(datetime.now())
                save_task_info(filename, upcoming_event, task_start_time, task_end_time, e)
        case "nback_morn" | "nback":
            try:
                # study night se sr
                result = start_real_nback(participant_info["participant_id"], participant_info["week_no"], participant_info["experiment"])
                if not result:
                    raise Exception('Task wurde abgebrochen')
                task_end_time = str(datetime.now())
                save_task_info(filename, upcoming_event, task_start_time, task_end_time, 'Success')
            except Exception as e:
                task_end_time = str(datetime.now())
                save_task_info(filename, upcoming_event, task_start_time, task_end_time, e)
        case "eeg_removal":
            try:
                text_screen("EEG entfernen", "Ein/e Versuchsleiter/in wird kommen und dir helfen.")
                task_end_time = str(datetime.now())
                save_task_info(filename, upcoming_event, task_start_time, task_end_time, 'Success')
            except Exception as e:
                task_end_time = str(datetime.now())
                save_task_info(filename, upcoming_event, task_start_time, task_end_time, e)
        case "breakfast_morn":
            try:
                text_screen("Frühstück", "Es ist Zeit für das Frühstück.")
                task_end_time = str(datetime.now())
                save_task_info(filename, upcoming_event, task_start_time, task_end_time, 'Success')
            except Exception as e:
                task_end_time = str(datetime.now())
                save_task_info(filename, upcoming_event, task_start_time, task_end_time, e)
        case "eeg_fitting":
            try:
                text_screen("EEG", "Jemand wird mit dir das EEG vorbereiten")
                task_end_time = str(datetime.now())
                save_task_info(filename, upcoming_event, task_start_time, task_end_time, 'Success')
            except Exception as e:
                task_end_time = str(datetime.now())
                save_task_info(filename, upcoming_event, task_start_time, task_end_time, e)
        case "dinner":
            try:
                text_screen("Abendessen", "Es ist Zeit für das Abendessen. Wir werden es dir bringen")
                task_end_time = str(datetime.now())
                save_task_info(filename, upcoming_event, task_start_time, task_end_time, 'Success')
            except Exception as e:
                task_end_time = str(datetime.now())
                save_task_info(filename, upcoming_event, task_start_time, task_end_time, e)
        case "capsule":
            try:
                text_screen("Kapsel", "Jemand wird dir die Kapsel bringen")
                task_end_time = str(datetime.now())
                save_task_info(filename, upcoming_event, task_start_time, task_end_time, 'Success')
            except Exception as e:
                task_end_time = str(datetime.now())
                save_task_info(filename, upcoming_event, task_start_time, task_end_time, e)
        case "bed_prep":
            try:
                text_screen("Bettzeit", "Zeit, sich bettfertig zu machen")
                task_end_time = str(datetime.now())
                save_task_info(filename, upcoming_event, task_start_time, task_end_time, 'Success')
            except Exception as e:
                task_end_time = str(datetime.now())
                save_task_info(filename, upcoming_event, task_start_time, task_end_time, e)
        case "in_bed":
            try:
                text_screen("Bettzeit", "Bitte begebe dich ins Bett")
                task_end_time = str(datetime.now())
                save_task_info(filename, upcoming_event, task_start_time, task_end_time, 'Success')
            except Exception as e:
                task_end_time = str(datetime.now())
                save_task_info(filename, upcoming_event, task_start_time, task_end_time, e)
        case "goodbye":
            try:
                text_screen("Vielen Dank fürs Mitmachen. Tschüss!", "")
                task_end_time = str(datetime.now())
                save_task_info(filename, upcoming_event, task_start_time, task_end_time, 'Success')
            except Exception as e:
                task_end_time = str(datetime.now())
                save_task_info(filename, upcoming_event, task_start_time, task_end_time, e)
        case _:
            if schedule[upcoming_event]["type"] == "text":
                try:
                    title = schedule[upcoming_event]["value"]["title"]
                    description = schedule[upcoming_event]["value"]["description"]
                    text_screen(title, description)
                    task_end_time = str(datetime.now())
                    save_task_info(filename, upcoming_event, task_start_time, task_end_time, 'Success')
                except Exception as e:
                    task_end_time = str(datetime.now())
                    save_task_info(filename, upcoming_event, task_start_time, task_end_time, e)

            elif schedule[upcoming_event]["type"] == "command":
                try:
                    command = schedule[upcoming_event]["value"]
                    process = subprocess.Popen(command)
                    process.communicate()
                    task_end_time = str(datetime.now())
                    save_task_info(filename, upcoming_event, task_start_time, task_end_time, 'Success')
                except Exception as e:
                    task_end_time = str(datetime.now())
                    save_task_info(filename, upcoming_event, task_start_time, task_end_time, e)
    return result