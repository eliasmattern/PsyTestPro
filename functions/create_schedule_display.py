import pygame
import sys
import os
from pygame.locals import *
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import messagebox
import re
import time as pythonTime
from lib import text_screen
import webbrowser
import subprocess
from .create_time_picker import create_time_picker
from .create_date_picker import create_date_picker
from services import TranslateService, LanguageConfiguration
from .play_task import play_tasks
from classes import Button

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
    screen = pygame.display.get_surface()
    
    # Setting the window caption
    pygame.display.set_caption('Schedule Editor')

    # Creating a Pygame clock object
    clock = pygame.time.Clock()
    
    def text_objects(text, font):
        text_surface = font.render(text, True, black)
        return text_surface, text_surface.get_rect()

    def button_back():

        # set the display mode to fullscreen
        screen = pygame.display.get_surface()
    
        # Setting the window caption
        pygame.display.set_caption('Schedule Processor')

        # set the color of the screen to black
        screen.fill(black)
        
        filtered_schedule = {key: value for key, value in schedule.items() if value["state"] == "todo"}
        # convert the schedule to a list of tuples and sort it by time
        sorted_schedule = sorted([(datetime.strptime(info["datetime"], '%d/%m/%Y %H:%M:%S'), event) for event, info in filtered_schedule.items()])
        check_for_old_tasks = True    
        play_next_task = False

        running = True
        while running:
            pygame.mouse.set_visible(True)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            if check_for_old_tasks:
                filtered_dict = {
                    key: value for key, value in schedule.items()
                    if value['state'] == 'todo'
                    and datetime.strptime(value['datetime'], '%d/%m/%Y %H:%M:%S') < datetime.now()
                }
                # Print the filtered list
                for item in filtered_dict:
                    upcoming_event = item
                    play_tasks(participant_info, upcoming_event, schedule)
                    pygame.mouse.set_visible(True)
                    schedule[upcoming_event]["state"]= "done"
                check_for_old_tasks = False
            
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
                    event_message = ' ' + translate_service.get_translation('until') + f' {next_event[1]}'
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
            if 75 + edit_button_width > mouse[0] > 75 and edit_button_y + edit_button_height > mouse[1] > edit_button_y:
                pygame.draw.rect(screen, light_grey, (75, edit_button_y, edit_button_width, edit_button_height))
                if click[0] == 1:
                    play_next_task = True
            else:
                pygame.draw.rect(screen, light_grey, (75, edit_button_y, edit_button_width, edit_button_height))

            # Draw the text on the button
            small_text = pygame.font.Font(None, 20)
            text_surf, text_rect = text_objects(translate_service.get_translation("editTeststarter"), small_text)
            text_rect.center = ((edit_button_x + (edit_button_width / 2)), (edit_button_y + (edit_button_height / 2)))
            screen.blit(text_surf, text_rect)
            
            next_surf, next_rect = text_objects(translate_service.get_translation("nextTask"), small_text)
            next_rect.center = ((75 + (edit_button_width / 2)), (edit_button_y + (edit_button_height / 2)))
            screen.blit(next_surf, next_rect)
            # update the display
            pygame.display.flip()
            if play_next_task:
                check_for_old_tasks = True
                upcoming_event = next_event[1]
                beep_sound = pygame.mixer.Sound("./lib/beep.wav")
                beep_sound.play()
                play_tasks(participant_info, upcoming_event, schedule)
                pygame.mouse.set_visible(True)
                schedule[upcoming_event]["state"]= "done"
                sorted_schedule = [(dt, desc) for dt, desc in sorted_schedule if desc != upcoming_event]
                print(sorted_schedule)
                play_next_task = False
            
            if not isHab or next_event_in_seconds == -1:
                if round(next_event_in_seconds) == 1:
                    check_for_old_tasks = True
                    upcoming_event = next_event[1]
                    pythonTime.sleep(1.1)
                    beep_sound = pygame.mixer.Sound("./lib/beep.wav")
                    beep_sound.play()
                    play_tasks(participant_info, upcoming_event, schedule)
                    pygame.mouse.set_visible(True)
                    schedule[upcoming_event]["state"]= "done"
            elif len(sorted_schedule) > 0:
                for task in schedule.items():
                    if schedule[task[0]]['state'] == "todo":
                        if schedule[task[0]]["type"] == "text":
                            title = schedule[task[0]]["value"]["title"]
                            now = datetime.now()
                            formatted_timestamp = now.strftime("%Y.%m.%d %H:%M:%S")
                            title = title.format(id = participant_info["participant_id"], 
                                         experiment = participant_info["experiment"], 
                                         startTime = participant_info["start_time"], 
                                         timestamp = formatted_timestamp)
                            
                            description = schedule[task[0]]["value"]["description"]
                            description= description.format(id = participant_info["participant_id"], 
                                         experiment = participant_info["experiment"], 
                                         startTime = participant_info["start_time"], 
                                         timestamp = formatted_timestamp)  
                            
                            text_screen(title, description)
                            schedule[task[0]]['state'] = "done"
                        elif schedule[task[0]]["type"] == "command":
                            now = datetime.now()
                            formatted_timestamp = now.strftime("%Y.%m.%d %H:%M:%S")
                            command = schedule[task[0]]["value"]
                            command = command.format(id = participant_info["participant_id"], 
                                                     experiment = participant_info["experiment"], 
                                                     startTime = participant_info["start_time"], 
                                                     timestamp = formatted_timestamp)   
                            process = subprocess.Popen(command)
                            process.communicate()
                            schedule[task[0]]['state'] = "done"
                sorted_schedule = []

        pygame.quit()

    def is_valid_datetime_format(datetime_str):
        # This pattern strictly matches DD/MM/YYYY HH:MM:SS
        pattern = r"^\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}$"
        return re.match(pattern, datetime_str) is not None

    def change_settings():
        global schedule_page
        schedule_page = 0

        time = str(participant_info["start_time"]).split(" ")[1]
        splittedTime = time.split(":")
        formattedTime = splittedTime[0] + ":" + splittedTime[1]
        teststarter(participant_info["participant_id"], participant_info["experiment"], formattedTime)
    
    def change_language(translateService, language_config, lang):
        translateService.set_language(lang)
        language_config.update_language_config(lang)

    def button_quit_teststarter():
        # Create a root window and hide it
        root = tk.Tk()
        root.withdraw()
        screenIndex = pygame.display.get_desktop_sizes().index(pygame.display.get_surface().get_size())
        count = 0
        posX, posY = pygame.mouse.get_pos() 
        posX -= 150
        posY -= 150
        for display in pygame.display.get_desktop_sizes():
            if count == screenIndex:
                break
            posX += display[0]
            count += 1
        root.geometry('+'+ str(posX) +'+'+ str(posY))
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
        screenIndex = pygame.display.get_desktop_sizes().index(pygame.display.get_surface().get_size())
        count = 0
        posX, posY = pygame.mouse.get_pos() 
        posX -= 150
        for display in pygame.display.get_desktop_sizes():
            if count == screenIndex:
                break
            posX += display[0]
            count += 1
        root.geometry('+'+ str(posX) +'+'+ str(posY))
        # Show a messagebox asking for confirmation
        response = messagebox.askyesno(translate_service.get_translation("help"), translate_service.get_translation("helpText"))

        # If the user clicked 'Yes', then open browser
        if response == True:
            webbrowser.open("https://github.com/eliasmattern/teststarter")    

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
    

    splitted_schedule = split_dict(schedule, 20)

    def page_update(schedule, increment):
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
    row_height = screen_height // (len(splitted_schedule[schedule_page]) + 3) if screen_height // (len(splitted_schedule[schedule_page]) + 3) < max_row_height else max_row_height  # +1 for the header row
    
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

    buttons = []
    page_butons = []

    # Create buttons
    run_button = Button(150 * width_scale_factor, 100 * height_scale_factor, 200 * width_scale_factor, 50 * height_scale_factor, "runTeststarter", button_back, translate_service)
    settings_button = Button(150 * width_scale_factor, 200 * height_scale_factor, 200 * width_scale_factor, 50 * height_scale_factor, "changeSettings", change_settings, translate_service)
    quit_button = Button(150 * width_scale_factor, 300 * height_scale_factor, 200 * width_scale_factor, 50 * height_scale_factor, "quit", button_quit_teststarter, translate_service)
    help_button = Button(150 * width_scale_factor, 400 * height_scale_factor, 200 * width_scale_factor, 50 * height_scale_factor, "help", button_help, translate_service)
    english_button = Button(85 * width_scale_factor, 500 * height_scale_factor, 70 * width_scale_factor, 50 * height_scale_factor, "english", lambda: change_language(translate_service, language_config, "en"), translate_service)
    german_button = Button(215 * width_scale_factor, 500 * height_scale_factor, 70 * width_scale_factor, 50 * height_scale_factor, "german", lambda: change_language(translate_service, language_config, "de"), translate_service)
   
    buttons.append(run_button)
    buttons.append(settings_button)
    buttons.append(quit_button)
    buttons.append(help_button)
    buttons.append(english_button)
    buttons.append(german_button)

    left_button = Button(column_start_x + 1.5 * column_width , 760 * height_scale_factor, 40 * width_scale_factor, 40 * height_scale_factor, "<", lambda: page_update(splitted_schedule, False))
    right_button = Button(column_start_x + 2.5 * column_width, 760 * height_scale_factor, 40 * width_scale_factor, 40 * height_scale_factor, ">", lambda: page_update(splitted_schedule, True))

    page_butons.append(left_button)
    page_butons.append(right_button)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
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
            for button in buttons:
                button.handle_event(event)
            
            if len(splitted_schedule) > 1:
                for button in page_butons:
                    button.handle_event(event)

        screen.fill(black) # Fill the screen with the black color
        
        for button in buttons:
            button.draw(screen)

        font = pygame.font.Font(None, int(20 * width_scale_factor)) # Create font object for header
        if len(splitted_schedule) > 1:
            page_number_surface = font.render(str(schedule_page + 1) + "/" + str(len(splitted_schedule)) , True, light_grey)
            screen.blit(page_number_surface, (column_start_x + 2 * column_width, 775 * height_scale_factor))
            for button in page_butons:
                button.draw(screen)

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
            
            max_grid_rows = len(splitted_schedule[schedule_page]) 

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