import pygame
import sys
import os
from pygame.locals import *
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import messagebox
import re
import time as pythonTime
from lib import GoNoGo_Real, GoNoGo_Real_Hab, start_real_nback, pvt, pvt_hab, saliva, waking_eeg, text_screen, start_hab_nback, leeds, moodscales
import webbrowser
import subprocess
from .create_time_picker import create_time_picker
from .create_date_picker import create_date_picker
from services import TranslateService, LanguageConfiguration

schedule_page = 0

def create_schedule_display(schedule, participant_info, teststarter, isHab = False):
    language_config = LanguageConfiguration()
    translate_service = TranslateService(language_config)

    # Open the pygame window at front of all windows open on screen
    os.environ['SDL_VIDEO_WINDOW_POS'] = '0,0'  # Set window position to top-left corner

    # Define colors
    black = (0, 0, 0)
    light_grey = (192, 192, 192)
    red = (255, 0, 0)
    
    # Initializing Pygame
    pygame.init() 
    
    # Get the screen width and height from the current device in use
    screen_info = pygame.display.Info()
    # Store the screen width in a new variable
    screen_width = screen_info.current_w
    # Store the screen height in a new variable
    screen_height = screen_info.current_h

    # Store the original screen dimensions used to design this program
    original_width = 1280
    original_height = 800
    
    # Calculate scaling factors for position and size adjustments (this is how we can make sure that the program adjusts to any screen it is executed on)
    width_scale_factor = screen_width / original_width
    height_scale_factor = screen_height / original_height
    
    # Creating a fullscreen display surface
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
    
    # Setting the window caption
    pygame.display.set_caption('Schedule Editor')

    # Creating a Pygame clock object
    clock = pygame.time.Clock()
    
    def draw_button(screen, message, x, y, w, h, ic, ac, action=None):
        global button_clicked

        # This is the function declaration, which includes the parameters: 
        # screen (the Pygame display surface), 
        # message (the text to be displayed on the button), 
        # x and y (the coordinates of the top left corner of the button), 
        # w and h (the width and height of the button)
        # ic is the inactive color (when the mouse is not hovering over the button)
        # ac is the active color (when the mouse is hovering over the button)
        mouse = pygame.mouse.get_pos() # This line gets the current position of the mouse
        click = pygame.mouse.get_pressed() # This line gets the state of the mouse buttons. click[0] will be 1 if the left mouse button is pressed, and 0 otherwise.
        if x+w > mouse[0] > x and y+h > mouse[1] > y: # This line checks if the mouse is currently hovering over the button
            pygame.draw.rect(screen, ac,(x, y, w, h)) # If the mouse is hovering over the button, this line draws the button with the active color.
            if click[0] == 1 and action != None:
                action() # If the mouse is hovering over the button and the left mouse button is clicked
        else:
            pygame.draw.rect(screen, ic,(x, y, w, h)) # If the mouse is not hovering over the button, this line draws the button with the inactive color
        small_text = pygame.font.Font(None, int(20 * width_scale_factor)) # This line creates a Pygame font object for the text on the button
        text_surf, text_rect = text_objects(message, small_text) # This line creates a text surface and a rectangle object for positioning the text
        text_rect.center = ( (x+(w/2)), (y+(h/2)) ) # This line centers the text rectangle in the middle of the button
        screen.blit(text_surf, text_rect) # This line draws the text surface on the screen at the position specified by the text rectangle

    def text_objects(text, font):
        text_surface = font.render(text, True, black)
        return text_surface, text_surface.get_rect()

    def button_back():

        # set the display mode to fullscreen
        screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
    
        # Setting the window caption
        pygame.display.set_caption('Schedule Processor')

        # set the color of the screen to black
        screen.fill(black)
        
        filtered_schedule = {key: value for key, value in schedule.items() if value["state"] == "todo"}
        # convert the schedule to a list of tuples and sort it by time
        sorted_schedule = sorted([(datetime.strptime(info["datetime"], '%d/%m/%Y %H:%M:%S'), event) for event, info in filtered_schedule.items()])
               
        running = True
        while running:
            pygame.mouse.set_visible(True)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            
            # get the current time
            now = datetime.now()
            # find the next event
            next_event = None
            for time, event in sorted_schedule:
                if time > now:
                    next_event = (time, event)
                    break
            # clear the screen before drawing the updated text
            screen.fill(black)
            next_event_in_seconds = -1
            if isHab:
                next_event_in_seconds = 0
            if next_event:
                next_event_in_seconds = (next_event[0] - now).total_seconds()
                # calculate the time until the next event
                if next_event is not None:
                    event_message = f' minutes until {next_event[1]}'
                else:
                    event_message = 'No more events today' 

                countdown = str(timedelta(seconds=round(next_event_in_seconds)))

            # Display the message on screen
            if isHab or not next_event: 
                font = pygame.font.Font(None, 35)
                text = font.render(translate_service.get_translation("allTasksCompleted"), True, light_grey)
            else: 
                font = pygame.font.Font(None, 35)
                text = font.render(countdown + event_message, True, light_grey)
            screen.blit(text, (50, 50)) # you can adjust the position as needed
            # Draw the "Edit Teststarter" button in the bottom right corner
            edit_button_x = screen_width - 250 * width_scale_factor
            edit_button_y = screen_height - 80 * height_scale_factor
            edit_button_width = 200 * width_scale_factor
            edit_button_height = 50  * height_scale_factor

            mouse = pygame.mouse.get_pos()
            click = pygame.mouse.get_pressed()

            if edit_button_x + edit_button_width > mouse[0] > edit_button_x and edit_button_y + edit_button_height > mouse[1] > edit_button_y:
                pygame.draw.rect(screen, light_grey, (edit_button_x, edit_button_y, edit_button_width, edit_button_height))
                if click[0] == 1:
                    create_schedule_display(schedule, participant_info, teststarter, isHab)  # Call create_schedule_display() when the button is clicked
            else:
                pygame.draw.rect(screen, light_grey, (edit_button_x, edit_button_y, edit_button_width, edit_button_height))

            # Draw the text on the button
            small_text = pygame.font.Font(None, 20)
            text_surf, text_rect = text_objects(translate_service.get_translation("editTeststarter"), small_text)
            text_rect.center = ((edit_button_x + (edit_button_width / 2)), (edit_button_y + (edit_button_height / 2)))
            screen.blit(text_surf, text_rect)

            # update the display
            pygame.display.flip()
            
            if not isHab or next_event_in_seconds == -1:
                if round(next_event_in_seconds) == 1:
                    upcoming_event = next_event[1]
                    pythonTime.sleep(1.1)
                    beep_sound = pygame.mixer.Sound("./lib/beep.wav")
                    beep_sound.play()
                    eventName = ''.join([i for i in upcoming_event if not i.isdigit()])
                    match eventName:
                        case "welcome":
                            #process = subprocess.Popen("py ./lib/wakingEeg.py")
                            #process.communicate()
                            text_screen("Willkommen zur Studie", "Vielen Dank fürs Mitmachen")
                        case "good_morn":
                            text_screen("Guten Morgen", "")
                        case "morn_sleep_diary" | "sleep_diary_expe":
                            text_screen("Schlaftagebuch", "Es ist Zeit für das Schlaftagebuch! Ein/e Forscher/in wird Ihnen helfen, das Schlaftagebuch zuführen.")
                        case "leeds":
                            leeds(participant_info["participant_id"], participant_info["week_no"])
                        case "break_morn" | "breaktime":
                            text_screen("Pause", "Es ist Zeit für eine Pause.")
                        case "waking_eeg_morn" | "waking_eeg":
                            waking_eeg()
                        case "pvt_morn" | "pvt":
                            # block = week number number = pvt number
                            pvtNumber = ''.join([i for i in upcoming_event if i.isdigit()])
                            pvt(participant_info["participant_id"], participant_info["week_no"], pvtNumber)
                        case "saliva_morn" | "saliva":
                            # kss = wie viele mal
                            salivaNumber = ''.join([i for i in upcoming_event if i.isdigit()])
                            saliva(participant_info["participant_id"], participant_info["experiment"], participant_info["week_no"], salivaNumber)
                        case "teethbrushing":
                            text_screen("Zähneputzen", "Sie können jetzt Ihre Zähne in Ihrem Zimmer putzen.")
                        case "mood_morn" | "mood":
                            moodscales(participant_info["participant_id"], participant_info["week_no"], participant_info["experiment"])
                        case "wof_morn" | "wof":
                            text_screen("Glücksrad", "Ein/e Forscher/in wird kommen und Ihnen helfen.")
                        case "task_payment":
                            text_screen("Zahlung", "Ein/e Forscher/in wird kommen und wird Sie bezahlen.")
                        case "gonogo_morn" | "gonogo":
                            # block = week number number = gonogo number
                            gonogo_number = ''.join([i for i in upcoming_event if i.isdigit()])
                            GoNoGo_Real(participant_info["participant_id"], participant_info["experiment"], participant_info["week_no"], gonogo_number)
                        case "nback_morn" | "nback":
                            # study night se sr
                            start_real_nback(participant_info["participant_id"], participant_info["week_no"], participant_info["experiment"])
                        case "eeg_removal":
                            text_screen("EEG entfernen", "Ein/e Forscher/in wird kommen und Ihnen helfen.")
                        case "breakfast_morn":
                            text_screen("Frühstück", "Es ist Zeit für das Frühstück.")
                        case "eeg_fitting":
                            text_screen("EEG", "Jemand wird mit Ihnen das EEG vorbereiten")
                        case "dinner":
                            text_screen("Abendessen", "Es ist Zeit für das Abendessen. Wir werden es Ihnen bringen")
                        case "capsule":
                            text_screen("Kapsel", "Jemand wird Ihnen die Kapsel bringen")
                        case "bed_prep": 
                            text_screen("Bettzeit", "Zeit, sich bettfertig zu machen")
                        case "in_bed": 
                            text_screen("Bettzeit", "Bitte begeben Sie sich ins Bett")
                        case "goodbye":
                            text_screen("Vielen Dank fürs Mitmachen. Tschüss!", "")
                        case _:
                            if schedule[upcoming_event]["type"] == "text":
                                title = schedule[upcoming_event]["value"]["title"]
                                description = schedule[upcoming_event]["value"]["description"]
                                text_screen(title, description)
                            elif schedule[upcoming_event]["type"] == "command":
                                command = schedule[upcoming_event]["value"]
                                process = subprocess.Popen(command)
                                process.communicate()
                    schedule[upcoming_event]["state"]= "done"
            elif len(sorted_schedule) > 0:
                if schedule["pvt_hab"]["state"] == "todo":
                    pvt_hab(participant_info["participant_id"], participant_info["week_no"], 1)
                    schedule["pvt_hab"]["state"] = "done"
                if schedule["gonogo_hab"]["state"] == "todo":
                    GoNoGo_Real_Hab(participant_info["participant_id"], participant_info["experiment"], participant_info["week_no"], 1)
                    schedule["gonogo_hab"]["state"] = "done"
                if schedule["n-back_hab"]["state"] == "todo":
                    start_hab_nback(participant_info["participant_id"], participant_info["week_no"], participant_info["experiment"])
                    schedule["n-back_hab"]["state"] = "done"
                for task in schedule.items():
                    if schedule[task[0]]['state'] == "todo":
                        if schedule[task[0]]["type"] == "text":
                            title = schedule[task[0]]["value"]["title"]
                            description = schedule[task[0]]["value"]["description"]
                            text_screen(title, description)
                            schedule[task[0]]['state'] = "done"
                        elif schedule[task[0]]["type"] == "command":
                            command = schedule[task[0]]["value"]
                            process = subprocess.Popen(command)
                            process.communicate()
                            schedule[task[0]]['state'] = "done"
                sorted_schedule = []

        pygame.quit()

    def is_valid_datetime_format(datetime_str):
        # This pattern strictly matches DD/MM/YYYY HH:MM:SS
        pattern = r"^\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}$"
        return re.match(pattern, datetime_str) is not None

    def change_night():
        global schedule_page
        schedule_page = 0

        time = str(participant_info["start_time"]).split(" ")[1]
        splittedTime = time.split(":")
        formattedTime = splittedTime[0] + ":" + splittedTime[1]
        teststarter(participant_info["participant_id"], participant_info["experiment"], participant_info["time_of_day"], participant_info["week_no"], formattedTime)
    
    def change_language(translateService, language_config, lang):
        translateService.set_language(lang)
        language_config.update_language_config(lang)

    def button_quit_teststarter():
        # Create a root window and hide it
        root = tk.Tk()
        root.withdraw()

        # Show a messagebox asking for confirmation
        response = messagebox.askyesno(translate_service.get_translation("confirmExit"), translate_service.get_translation("confirmExitText"))

        # If the user clicked 'Yes', then close the program
        if response == True:
            pygame.quit()
            quit()

        # Destroy the root window
        root.destroy()

        
    def button_help():
        root = tk.Tk()
        root.withdraw()

        # Show a messagebox asking for confirmation
        response = messagebox.askyesno(translate_service.get_translation("help"), translate_service.get_translation("helpText"))

        # If the user clicked 'Yes', then open browser
        if response == True:
            webbrowser.open("https://github.com/")    

        # Destroy the root window
        root.destroy()
    
    def split_dict(input_dict, chunk_size):
        dict_list = [{}]
        current_dict = 0

        for key, value in input_dict.items():
            dict_list[current_dict][key] = value
            if len(dict_list[current_dict]) >= chunk_size:
                dict_list.append({})
                current_dict += 1

        return dict_list
    

    splitted_schedule = split_dict(schedule, 30)

    def page_update(schedule, increment):
        pythonTime.sleep(0.125)
        global schedule_page
        if increment:
            schedule_page = (schedule_page + 1) % len(splitted_schedule)
        else:
            schedule_page = (schedule_page - 1) if schedule_page > 0 else len(splitted_schedule) - 1

    # Calculate column widths and row height based on screen size
    column_width = screen_width // 9
    column_start_x = screen_width - (column_width * 4) - 50  # Calculate column positions based on screen size (adjusted for right alignment)
    if isHab:
        column_start_x = screen_width - (column_width * 2) - 50 # Hab night Calculate column positions based on screen size (adjusted for right alignment)

    max_row_height = 75    
    row_height = screen_height // (len(schedule) + 1.5) if screen_height // (len(schedule) + 1.5) < max_row_height else max_row_height  # +1 for the header row
    
    
    # Padding for cell
    cellPadding = 10

    # Input box fonts
    todo_input_box_font = pygame.font.Font(None, int(16 * width_scale_factor))
    newtime_input_box_font = pygame.font.Font(None, int(16 * width_scale_factor))
    newdate_input_box_font = pygame.font.Font(None, int(16 * width_scale_factor))
   
    # Input text font and cursor settings
    todo_input_text_font = pygame.freetype.Font(None, int(10 * width_scale_factor))
    cursor_color = light_grey
    cursor_width = 2
    cursor_blink_interval = 500  # milliseconds

    # Create a dictionary to store the input values for each row
    newdate_input_values = {}
    newtime_input_values = {}
    todo_input_values = {}
    
    newdate_active_row = None  # Initialize the active row to None
    newtime_active_row = None  # Initialize the active row to None
    todo_active_row = None  # Initialize the active row to None
    active_column = None
    cursor_visible = True  # Initialize cursor visibility
    cursor_timer = 0  # Initialize cursor timer
    newdate_input_text = ""  # Initialize the input text variable
    newtime_input_text = ""  # Initialize the input text variable
    todo_input_text = ""  # Initialize the input text variable

    newdate_input_active = False  # Initialize the text input variable
    newtime_input_active = False  # Initialize the text input variable
    todo_input_active = False  # Initialize the text input variable
    state_iterator = {"todo": "skip", "skip": "done", "done": "todo"}
    todo_row_multiplicator = 3
    if isHab:
        todo_row_multiplicator = 1
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for row in range(1, len(splitted_schedule[schedule_page]) + 1):
                    if not isHab:
                        newdate_input_box_rect = pygame.Rect(
                            column_start_x + (column_width),
                            row * row_height,
                            column_width,
                            row_height
                        )
                        newtime_input_box_rect = pygame.Rect(
                            column_start_x + (2 * column_width),
                            row * row_height,
                            column_width,
                            row_height
                        )
                    todo_input_box_rect = pygame.Rect(
                        column_start_x + (todo_row_multiplicator * column_width),
                        row * row_height,
                        column_width,
                        row_height
                    )
                    if todo_input_box_rect.collidepoint(mouse_pos):
                        todo_active_row = row
                        todo_input_values[row] = state_iterator[splitted_schedule[schedule_page][list(splitted_schedule[schedule_page])[row-1]]["state"]]
                        active_column = "todo"  # Set the active column
                        todo_input_active = True
                        newtime_input_active = False
                        newtime_active_row = None
                        newtimedate_active_row = None  # Deactivate the other column
                        newtimedate_input_active = False
                    if not isHab:
                        if newdate_input_box_rect.collidepoint(mouse_pos) and not isHab:
                            newdate_active_row = row
                            newdate_input_values[row] = splitted_schedule[schedule_page][list(splitted_schedule[schedule_page])[row-1]]["datetime"].split(" ")[0]
                            active_column = "newdate"  # Set the active column
                            newtimedate_input_active = False
                            newdate_input_active = True
                            todo_active_row = None  # Deactivate the other column
                            todo_input_active = False
                            newtime_active_row = None
                            newtime_input_active = False
                            splitted_date = newdate_input_values[row].split("/")
                            day,month,year = splitted_date[0], splitted_date[1], splitted_date[2]
                            date = create_date_picker(int(year), int(month), int(day))
                            newdate_input_values[newdate_active_row] = date
                        elif newtime_input_box_rect.collidepoint(mouse_pos) and not isHab:
                            newtime_active_row = row
                            newtime_input_values[row] = ""
                            active_column = "newtime"  # Set the active column
                            newtimedate_input_active = False
                            newtime_input_active = True
                            todo_active_row = None  # Deactivate the other column
                            todo_input_active = False
                            newdate_active_row = None
                            newdate_input_active = False
                            current_time = splitted_schedule[schedule_page][list(splitted_schedule[schedule_page])[row-1]]["datetime"].split(" ")[1]
                            splitted_time = current_time.split(":")
                            time_picker = create_time_picker(splitted_time[0], splitted_time[1], translate_service)
                            formatted_time = str(time_picker.time()[0]).rjust(2, '0') + ":" + str(time_picker.time()[1]).rjust(2, '0') +":00"
                            if newtime_active_row in newtime_input_values:
                                newtime_input_values[newtime_active_row] = formatted_time
                            else: 
                                newtime_input_values[newtime_active_row] = formatted_time

        screen.fill(black) # Fill the screen with the black color
        
        # This invokes the function draw_button
        draw_button(screen, translate_service.get_translation("runTeststarter"), 50 * width_scale_factor, 100 * height_scale_factor, 200 * width_scale_factor, 50 * height_scale_factor, light_grey, light_grey, button_back)
        draw_button(screen, translate_service.get_translation("changNight"), 50 * width_scale_factor, 200 * height_scale_factor, 200 * width_scale_factor, 50 * height_scale_factor, light_grey, light_grey, change_night)
        draw_button(screen, translate_service.get_translation("quit"), 50 * width_scale_factor, 300 * height_scale_factor, 200 * width_scale_factor, 50 * height_scale_factor, light_grey, light_grey, button_quit_teststarter)
        draw_button(screen, translate_service.get_translation("help"), 50 * width_scale_factor, 400 * height_scale_factor, 200 * width_scale_factor, 50 * height_scale_factor, light_grey, light_grey, button_help)
        draw_button(screen, translate_service.get_translation("english"), 50 * width_scale_factor, 500 * height_scale_factor, 70 * width_scale_factor, 50 * height_scale_factor, light_grey, light_grey, lambda: change_language(translate_service, language_config, "en"))
        draw_button(screen, translate_service.get_translation("german"), 180 * width_scale_factor, 500 * height_scale_factor, 70 * width_scale_factor, 50 * height_scale_factor, light_grey, light_grey, lambda: change_language(translate_service, language_config, "de"))
        
        font = pygame.font.Font(None, int(20 * width_scale_factor)) # Create font object for header
        if len(splitted_schedule) > 1:
            page_number_surface = font.render(str(schedule_page + 1) + "/" + str(len(splitted_schedule)) , True, light_grey)
            screen.blit(page_number_surface, (column_start_x + 2 * column_width, 775 * height_scale_factor))
            draw_button(screen, "<", column_start_x + 1.5 * column_width, 760 * height_scale_factor, 40 * width_scale_factor, 40 * height_scale_factor, light_grey, light_grey, lambda: page_update(splitted_schedule, False))
            draw_button(screen, ">", column_start_x + 2.4 * column_width, 760 * height_scale_factor, 40 * width_scale_factor, 40 * height_scale_factor, light_grey, light_grey, lambda: page_update(splitted_schedule, True))

        # Display column headers with adjusted font size
        text_surface = font.render(' ' + translate_service.get_translation("task"), True, light_grey) # Render the text 'Task' with the font and color light_grey
        screen.blit(text_surface, (column_start_x, cellPadding)) # Blit the text surface to the screen at the specified position
        if not isHab:
            text_surface = font.render(' ' + translate_service.get_translation("date"), True, light_grey) # Render the text 'Time'
            screen.blit(text_surface, (column_start_x + column_width, cellPadding)) # Blit the text surface to the screen
            text_surface = font.render(' ' + translate_service.get_translation("time"), True, light_grey) # Render the text 'Time'
            screen.blit(text_surface, (column_start_x + (2 * column_width), cellPadding)) # Blit the text surface to the screen
        #text_surface = font.render('New Date and Time', True, light_grey) # Render the text 'New Date and Time'
        #screen.blit(text_surface, (column_start_x + (3 * column_width), cellPadding)) # Blit the text surface to the screen
        text_surface = font.render(' ' + translate_service.get_translation("skipDoneTodo"), True, light_grey)  # Render the text 'Skip/newtimedate'
        screen.blit(text_surface, (column_start_x + (todo_row_multiplicator * column_width), cellPadding))  # Adjusted blitting position

        # Display each task with adjusted font size
        font = pygame.font.Font(None, int(16 * width_scale_factor))
        row = 1  # Initialize the row counter
        # Loop through each task and datetime in the schedule dictionary
        
        for task, info in splitted_schedule[schedule_page].items():
            date = info["datetime"].split(" ")[0]
            time = info["datetime"].split(" ")[1]
            state = info["state"]
            # Replace underscores with spaces in the task name
            task_name = task.replace('_', ' ')
            task_name = ' ' + task_name

            # Format the task and datetime strings
            task_text = font.render(task_name, True, light_grey) # Render the task name text

            # Display the task details in each column with adjusted row height
            screen.blit(task_text, (column_start_x, row * row_height + cellPadding))  # Blit the task_text to the screen
            # Adjusted blitting position for the "Skip/newtimedate" column
            skip_newtimedate_text = font.render('To Do/Skip', True, light_grey) # Render the text 'To Do/Skip'
            
            # Render input boxes for "New Date" and " New Time" and "Skip/ToDo" columns
            if not isHab:
                newdate_input_box_rect = pygame.Rect(
                    column_start_x + (column_width),
                    row * row_height,
                    column_width,
                    row_height
                )

                newtime_input_box_rect = pygame.Rect(
                    column_start_x + (2 * column_width),
                    row * row_height,
                    column_width,
                    row_height
                )

            todo_input_box_rect = pygame.Rect(
                column_start_x + (todo_row_multiplicator * column_width),
                row * row_height,
                column_width,
                row_height
            )
            if not isHab:
                pygame.draw.rect(screen, light_grey, newdate_input_box_rect, 1)
                pygame.draw.rect(screen, light_grey, newtime_input_box_rect, 1)
            pygame.draw.rect(screen, light_grey, todo_input_box_rect, 1)

            # Render input value
            if not isHab:
                if row in newdate_input_values:
                    newdate_input_value = newdate_input_values[row]
                    newdate_input_text_surface = newdate_input_box_font.render(newdate_input_value, True, light_grey)
                    if not is_valid_datetime_format(newdate_input_value + " " + time):
                        newdate_input_text_surface = newdate_input_box_font.render(newdate_input_value, True, red)
                    else:
                        newdate_input_text_surface = newdate_input_box_font.render(newdate_input_value, True, light_grey)
                        splitted_schedule[schedule_page][list(splitted_schedule[schedule_page])[row-1]]["datetime"] = newdate_input_value + " " + time
                    screen.blit(newdate_input_text_surface, newdate_input_box_rect.move(5, 5))
                elif newdate_active_row == row:
                    newdate_input_text_surface = newdate_input_box_font.render(newdate_input_text, True, light_grey)
                    screen.blit(newdate_input_text_surface, newdate_input_box_rect.move(5, 5))
                elif newdate_active_row != row:
                    newdate_input_text_surface = newdate_input_box_font.render(date, True, light_grey)
                    screen.blit(newdate_input_text_surface, newdate_input_box_rect.move(5, 5))

                if row in newtime_input_values:
                    newtime_input_value = newtime_input_values[row]
                    newtime_input_text_surface = newtime_input_box_font.render(newtime_input_value, True, light_grey)
                    if not is_valid_datetime_format(date + " " + newtime_input_value):
                        newtime_input_text_surface = newtime_input_box_font.render(newtime_input_value, True, red)
                    else:
                        newtime_input_text_surface = newtime_input_box_font.render(newtime_input_value, True, light_grey)
                        splitted_schedule[schedule_page][list(splitted_schedule[schedule_page])[row-1]]["datetime"] = date + " " + newtime_input_value
                    screen.blit(newtime_input_text_surface, newtime_input_box_rect.move(5, 5))
                elif newtime_active_row == row:
                    newtime_input_text_surface = newtime_input_box_font.render(newtime_input_text, True, light_grey)
                    screen.blit(newtime_input_text_surface, newtime_input_box_rect.move(5, 5))
                elif newtime_active_row != row:
                    newtime_input_text_surface = newtime_input_box_font.render(time, True, light_grey)
                    screen.blit(newtime_input_text_surface, newtime_input_box_rect.move(5, 5))

            todo_color = {"todo": light_grey, "skip": (240, 230, 140), "done": (0, 179, 113)}
            if row in todo_input_values:
                todo_input_value = todo_input_values[row]
                todo_input_text_surface = todo_input_box_font.render(translate_service.get_translation(todo_input_value), True, todo_color[todo_input_value.lower()])

                if todo_input_value.lower() == "todo" or todo_input_value.lower() == "done" or todo_input_value.lower() == "skip":
                    splitted_schedule[schedule_page][list(splitted_schedule[schedule_page])[row-1]]["state"] = todo_input_value.lower()
                else:
                    todo_input_text_surface = todo_input_box_font.render(todo_input_value, True, red)
                screen.blit(todo_input_text_surface, todo_input_box_rect.move(5, 5))
            elif todo_active_row == row:
                todo_input_text_surface = todo_input_box_font.render(todo_input_text, True, todo_color[todo_input_values[row].lower()])
                screen.blit(todo_input_text_surface, todo_input_box_rect.move(5, 5))
            elif todo_active_row != row:
                todo_input_text_surface = todo_input_box_font.render(translate_service.get_translation(state), True, todo_color[splitted_schedule[schedule_page][list(splitted_schedule[schedule_page])[row-1]]["state"].lower()])
                screen.blit(todo_input_text_surface, todo_input_box_rect.move(5, 5))

            # Render the cursor
            if (active_column == "newdate" and newdate_active_row == row):
                cursor_x = 0
                cursor_y = 0
                cursor_height = 0
                input_text_surface = None

                if active_column == "newdate":
                    cursor_x = newdate_input_box_rect.left + newdate_input_text_surface.get_width() + 5
                    cursor_y = newdate_input_box_rect.top + 5
                    cursor_height = 14
                    input_text_surface = newdate_input_text_surface

                pygame.draw.line(screen, cursor_color, (cursor_x, cursor_y), (cursor_x, cursor_y + cursor_height), cursor_width)

        
            row += 1  # Increment the row counter
            
            max_grid_rows = 30 if len(schedule) > 30 else len(schedule)

            final_y = (max_grid_rows + 1) * row_height

            # Draw grid lines
            grid_range = 5 if not isHab else 3
            for i in range(grid_range):
                x = column_start_x + (i * column_width)
                pygame.draw.line(screen, light_grey, (x, 0), (x, final_y), 1)

            for i in range(1, max_grid_rows + 2):
                y = i * row_height
                pygame.draw.line(screen, light_grey, (column_start_x, y), (column_start_x + ((grid_range -1) * column_width), y), 1)

        # Update the cursor visibility
        current_time = pygame.time.get_ticks()
        if current_time - cursor_timer > cursor_blink_interval:
            cursor_visible = not cursor_visible
            cursor_timer = current_time
            
        pygame.display.flip()  # Flip the display to update the screen