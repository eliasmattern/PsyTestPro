# Add buttons to the left side of the screen

# Script updated to add input entry to relevant columns

import pygame
import sys
import os
from pygame.locals import *
import csv
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import messagebox
import re
import time as pythonTime
from lib import GoNoGo_Real, GoNoGo_Real_Hab, start_real_nback, pvt, pvt_hab, saliva, waking_eeg, text_screen, start_hab_nback, leeds, moodscales
from ctypes import windll
import webbrowser

def create_schedule_display(schedule, participant_info):
    
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
                text = font.render("Alle Aufgaben erledigt", True, light_grey)
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
                    create_schedule_display(schedule, participant_info)  # Call create_schedule_display() when the button is clicked
            else:
                pygame.draw.rect(screen, light_grey, (edit_button_x, edit_button_y, edit_button_width, edit_button_height))

            # Draw the text on the button
            small_text = pygame.font.Font(None, 20)
            text_surf, text_rect = text_objects("Edit Teststarter", small_text)
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
                            saliva(participant_info["participant_id"], participant_info["week_no"], salivaNumber)
                        case "teethbrushing":
                            text_screen("Zähneputzen", "Sie können jetzt Ihre Zähne in Ihrem Zimmer putzen.")
                        case "mood_morn" | "mood":
                            moodscales(participant_info["participant_id"], participant_info["week_no"])
                        case "wof_morn" | "wof":
                            text_screen("Glücksrad", "Ein/e Forscher/in wird kommen und Ihnen helfen.")
                        case "task_payment":
                            text_screen("Zahlung", "Ein/e Forscher/in wird kommen und wird Sie bezahlen.")
                        case "gonogo_morn" | "gonogo":
                            # block = week number number = gonogo number
                            gonogo_number = ''.join([i for i in upcoming_event if i.isdigit()])
                            GoNoGo_Real(participant_info["participant_id"], participant_info["week_no"], gonogo_number)
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
                            text_screen(eventName, "Task not found.")
                    schedule[upcoming_event]["state"]= "done"
            elif len(sorted_schedule) > 0:
                if schedule["pvt_hab"]["state"] == "todo":
                    pvt_hab(participant_info["participant_id"], participant_info["week_no"], 1)
                    schedule["pvt_hab"]["state"] = "done"
                if schedule["gonogo_hab"]["state"] == "todo":
                    GoNoGo_Real_Hab(participant_info["participant_id"], participant_info["week_no"], 1)
                    schedule["gonogo_hab"]["state"] = "done"
                if schedule["n-back_hab"]["state"] == "todo":
                    start_hab_nback(participant_info["participant_id"], participant_info["week_no"], participant_info["experiment"])
                    schedule["n-back_hab"]["state"] = "done"
                sorted_schedule = []

        # get the handle to the taskbar
        h = windll.user32.FindWindowA(b'Shell_TrayWnd', None)
        # hide the taskbar
        windll.user32.ShowWindow(h, 9)
        pygame.quit()

    def is_valid_datetime_format(datetime_str):
        # This pattern strictly matches DD/MM/YYYY HH:MM:SS
        pattern = r"^\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}$"
        return re.match(pattern, datetime_str) is not None


    
    def button_save_changes():
        global newtimedate_input_values, newtimedate_active_row

        if newtimedate_input_values:
            for row, value in newtimedate_input_values.items():
                if is_valid_datetime_format(value):
                    # Update the corresponding entry in the schedule dictionary
                    schedule_entry = list(schedule.items())[row - 1]  # Get the (task, datetime) tuple at the row index
                    task_name = schedule_entry[0]
                    schedule[task_name] = value  # Update the datetime value in the schedule dictionary

            # Clear the input values and active row for the newtimedate column
            newtimedate_input_values.clear()
            newtimedate_active_row = None

        if todo_input_values:
            for row, value in todo_input_values.items():
                if value:
                    # Perform any additional validation on the todo input, if needed
                    # (e.g., check if value is "ToDo", "Skip", etc.)

                    # Update the corresponding entry in the schedule dictionary
                    schedule_entry = list(schedule.items())[row - 1]  # Get the (task, datetime) tuple at the row index
                    task_name = schedule_entry[0]
                    schedule[task_name] = value  # Update the "ToDo/Skip" value in the schedule dictionary

            # Clear the input values and active row for the todo column
            todo_input_values.clear()
            todo_active_row = None

        # Call the button_back() function to go back to the main view
        button_back()

    def change_night():
        time = str(participant_info["start_time"]).split(" ")[1]
        splittedTime = time.split(":")
        formattedTime = splittedTime[0] + ":" + splittedTime[1]
        Teststarter(participant_info["participant_id"], participant_info["experiment"], participant_info["time_of_day"], participant_info["week_no"], formattedTime)
    
    def button_quit_teststarter():
        # Create a root window and hide it
        root = tk.Tk()
        root.withdraw()

        # Show a messagebox asking for confirmation
        response = messagebox.askyesno("Confirm Exit", "Are you sure you want to quit Teststarter?")

        # If the user clicked 'Yes', then close the program
        if response == True:
            # get the handle to the taskbar
            h = windll.user32.FindWindowA(b'Shell_TrayWnd', None)
            # hide the taskbar
            windll.user32.ShowWindow(h, 9)
            pygame.quit()
            quit()

        # Destroy the root window
        root.destroy()

        
    def button_help():
        root = tk.Tk()
        root.withdraw()

        # Show a messagebox asking for confirmation
        response = messagebox.askyesno("Help", "You will be redirected to GitHub?")

        # If the user clicked 'Yes', then open browser
        if response == True:
            webbrowser.open("https://github.com/")    

        # Destroy the root window
        root.destroy()
    
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
                # get the handle to the taskbar
                h = windll.user32.FindWindowA(b'Shell_TrayWnd', None)
                # hide the taskbar
                windll.user32.ShowWindow(h, 9)
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for row in range(1, len(schedule) + 1):
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
                        todo_input_values[row] = state_iterator[schedule[list(schedule)[row-1]]["state"]]
                        active_column = "todo"  # Set the active column
                        todo_input_active = True
                        newtime_input_active = False
                        newtime_active_row = None
                        newtimedate_active_row = None  # Deactivate the other column
                        newtimedate_input_active = False
                    if not isHab:
                        if newdate_input_box_rect.collidepoint(mouse_pos) and not isHab:
                            newdate_active_row = row
                            newdate_input_values[row] = schedule[list(schedule)[row-1]]["datetime"].split(" ")[0]
                            active_column = "newdate"  # Set the active column
                            newtimedate_input_active = False
                            newdate_input_active = True
                            todo_active_row = None  # Deactivate the other column
                            todo_input_active = False
                            newtime_active_row = None
                            newtime_input_active = False
                        elif newtime_input_box_rect.collidepoint(mouse_pos) and not isHab:
                            newtime_active_row = row
                            newtime_input_values[row] = schedule[list(schedule)[row-1]]["datetime"].split(" ")[1]
                            active_column = "newtime"  # Set the active column
                            newtimedate_input_active = False
                            newtime_input_active = True
                            todo_active_row = None  # Deactivate the other column
                            todo_input_active = False
                            newdate_active_row = None
                            newdate_input_active = False


            elif event.type == pygame.KEYDOWN:
                if newdate_active_row is not None and newdate_input_active:
                    if event.key == pygame.K_RETURN:
                        newdate_active_row += 1
                    elif event.key == pygame.K_BACKSPACE:
                        newdate_input_values[newdate_active_row] = newdate_input_values[newdate_active_row][:-1]
                    else:
                        newdate_input_values[newdate_active_row] += event.unicode
                if newtime_active_row is not None and newtime_input_active:
                    if event.key == pygame.K_RETURN:
                        newtime_active_row += 1
                    elif event.key == pygame.K_BACKSPACE:
                        newtime_input_values[newtime_active_row] = newtime_input_values[newtime_active_row][:-1]
                    else:
                        newtime_input_values[newtime_active_row] += event.unicode
            

        screen.fill(black) # Fill the screen with the black color
        
        # This invokes the function draw_button
        draw_button(screen, "Run Teststarter", 50 * width_scale_factor, 100 * height_scale_factor, 200 * width_scale_factor, 50 * height_scale_factor, light_grey, light_grey, button_back)
        draw_button(screen, "Change / Edit Night", 50 * width_scale_factor, 200 * height_scale_factor, 200 * width_scale_factor, 50 * height_scale_factor, light_grey, light_grey, change_night)
        draw_button(screen, "Quit Teststarter", 50 * width_scale_factor, 300 * height_scale_factor, 200 * width_scale_factor, 50 * height_scale_factor, light_grey, light_grey, button_quit_teststarter)
        draw_button(screen, "Help", 50 * width_scale_factor, 400 * height_scale_factor, 200 * width_scale_factor, 50 * height_scale_factor, light_grey, light_grey, button_help)

        # Display column headers with adjusted font size
        font = pygame.font.Font(None, int(20 * width_scale_factor)) # Create font object for header
        text_surface = font.render(' Task', True, light_grey) # Render the text 'Task' with the font and color light_grey
        screen.blit(text_surface, (column_start_x, cellPadding)) # Blit the text surface to the screen at the specified position
        if not isHab:
            text_surface = font.render(' Date', True, light_grey) # Render the text 'Time'
            screen.blit(text_surface, (column_start_x + column_width, cellPadding)) # Blit the text surface to the screen
            text_surface = font.render(' Time', True, light_grey) # Render the text 'Time'
            screen.blit(text_surface, (column_start_x + (2 * column_width), cellPadding)) # Blit the text surface to the screen
        #text_surface = font.render('New Date and Time', True, light_grey) # Render the text 'New Date and Time'
        #screen.blit(text_surface, (column_start_x + (3 * column_width), cellPadding)) # Blit the text surface to the screen
        text_surface = font.render(' Skip/Done/ToDo', True, light_grey)  # Render the text 'Skip/newtimedate'
        screen.blit(text_surface, (column_start_x + (todo_row_multiplicator * column_width), cellPadding))  # Adjusted blitting position

        # Display each task with adjusted font size
        font = pygame.font.Font(None, int(16 * width_scale_factor))
        row = 1  # Initialize the row counter
        # Loop through each task and datetime in the schedule dictionary
        for task, info in schedule.items():
            date = info["datetime"].split(" ")[0]
            time = info["datetime"].split(" ")[1]
            state = info["state"]
            # Replace underscores with spaces in the task name
            task_name = task.replace('_', ' ')

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
                        schedule[list(schedule)[row-1]]["datetime"] = newdate_input_value + " " + time
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
                        schedule[list(schedule)[row-1]]["datetime"] = date + " " + newtime_input_value
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
                todo_input_text_surface = todo_input_box_font.render(todo_input_value, True, todo_color[todo_input_value.lower()])

                if todo_input_value.lower() == "todo" or todo_input_value.lower() == "done" or todo_input_value.lower() == "skip":
                    schedule[list(schedule)[row-1]]["state"] = todo_input_value.lower()
                else:
                    todo_input_text_surface = todo_input_box_font.render(todo_input_value, True, red)
                screen.blit(todo_input_text_surface, todo_input_box_rect.move(5, 5))
            elif todo_active_row == row:
                todo_input_text_surface = todo_input_box_font.render(todo_input_text, True, todo_color[todo_input_values[row].lower()])
                screen.blit(todo_input_text_surface, todo_input_box_rect.move(5, 5))
            elif todo_active_row != row:
                todo_input_text_surface = todo_input_box_font.render(state, True, todo_color[schedule[list(schedule)[row-1]]["state"].lower()])
                screen.blit(todo_input_text_surface, todo_input_box_rect.move(5, 5))

            # Render the cursor
            if (active_column == "newdate" and newdate_active_row == row) or (active_column == "newtime" and newtime_active_row == row):
                cursor_x = 0
                cursor_y = 0
                cursor_height = 0
                input_text_surface = None

                if active_column == "newdate":
                    cursor_x = newdate_input_box_rect.left + newdate_input_text_surface.get_width() + 5
                    cursor_y = newdate_input_box_rect.top + 5
                    cursor_height = 14
                    input_text_surface = newdate_input_text_surface
                elif active_column == "newtime":
                    cursor_x = newtime_input_box_rect.left + newtime_input_text_surface.get_width() + 5
                    cursor_y = newtime_input_box_rect.top + 5
                    cursor_height = 14
                    input_text_surface = newtime_input_text_surface


                pygame.draw.line(screen, cursor_color, (cursor_x, cursor_y), (cursor_x, cursor_y + cursor_height), cursor_width)

        
            row += 1  # Increment the row counter
            
            final_y = (len(schedule) + 1) * row_height

            # Draw grid lines
            grid_range = 5 if not isHab else 3
            for i in range(grid_range):
                x = column_start_x + (i * column_width)
                pygame.draw.line(screen, light_grey, (x, 0), (x, final_y), 1)

            for i in range(1, len(schedule) + 2):
                y = i * row_height
                pygame.draw.line(screen, light_grey, (column_start_x, y), (column_start_x + ((grid_range -1) * column_width), y), 1)

        # Update the cursor visibility
        current_time = pygame.time.get_ticks()
        if current_time - cursor_timer > cursor_blink_interval:
            cursor_visible = not cursor_visible
            cursor_timer = current_time
            
        pygame.display.flip()  # Flip the display to update the screen

#######################################################################

class Button:
    def __init__(self, x, y, width, height, label, action):
        self.rect = pygame.Rect(x - width // 2, y, width, height)
        self.color = pygame.Color("gray")
        self.label = pygame.font.SysFont("Arial", 24).render(label, True, pygame.Color("black"))
        self.action = action

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONUP and self.rect.collidepoint(event.pos):
            self.action()

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        label_width, label_height = self.label.get_size()
        label_x = self.rect.x + (self.rect.width - label_width) // 2
        label_y = self.rect.y + (self.rect.height - label_height) // 2
        screen.blit(self.label, (label_x, label_y))

class Teststarter:
    def __init__(self, id="", experiment = "", time_of_day = "", week_number = "", time = ""):
        pygame.init()
        self.width, self.height = pygame.display.Info().current_w, pygame.display.Info().current_h
        self.screen = pygame.display.set_mode((self.width, self.height), FULLSCREEN)
        # get the handle to the taskbar
        h = windll.user32.FindWindowA(b'Shell_TrayWnd', None)
        # hide the taskbar
        windll.user32.ShowWindow(h, 0)
        pygame.display.set_caption("Teststarter")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 24)
        self.input_boxes = []
        self.id = id
        self.experiment = experiment
        self.time_of_day = time_of_day
        self.week_number = week_number
        self.time = time
        self.create_input_boxes()
        self.is_running = True
        self.start_time = None

        while self.is_running:
            self.handle_events()
            self.clear_screen()
            self.draw()
            pygame.display.flip()
            self.clock.tick(60)

        # get the handle to the taskbar
        h = windll.user32.FindWindowA(b'Shell_TrayWnd', None)
        # hide the taskbar
        windll.user32.ShowWindow(h, 9)
        pygame.quit()
        sys.exit()
        
    class TestBatteryConfiguration:
        def __init__(self, start_time):
            self.start_time = start_time
            self.config_data = {}

        def read_config_file(self, file_name):
            with open(file_name, 'r') as file:
                reader = csv.reader(file)
                header = next(reader)
                for row in reader:
                    for i, value in enumerate(row):
                        key = header[i]
                        if key not in self.config_data:
                            self.config_data[key] = []
                        self.config_data[key].append(value)

        def hab_night(self, participant_info):
            global schedule
            global isHab
            isHab = True
            schedule = {}
            exp_eve_times = self.config_data['hab']
            exp_eve_variables = self.config_data['hab_variable']
            for i, time_delta in enumerate(exp_eve_times):
                exp_variable = exp_eve_variables[i]
                if time_delta:
                    activation_time = self.start_time + timedelta(hours=int(time_delta.split(':')[0]), minutes=int(time_delta.split(':')[1]))
                    #schedule[exp_variable] = str(activation_time)
                    schedule[exp_variable] = activation_time.strftime('%d/%m/%Y %H:%M:%S')
            edited_schedule = {}
            for key, value in schedule.items():
                edited_schedule.update({key: {"datetime": value, "state": "todo"}})
            schedule = edited_schedule
            print("hab = ", edited_schedule)
            create_schedule_display(schedule, participant_info)

        def experiment_evening(self, participant_info):
            global schedule
            global isHab
            isHab = False
            schedule = {}
            exp_eve_times = self.config_data['exp_eve']
            exp_eve_variables = self.config_data['exp_eve_variable']
            for i, time_delta in enumerate(exp_eve_times):
                exp_variable = exp_eve_variables[i]
                if time_delta:
                    activation_time = self.start_time + timedelta(hours=int(time_delta.split(':')[0]), minutes=int(time_delta.split(':')[1]))
                    #schedule[exp_variable] = str(activation_time)
                    schedule[exp_variable] = activation_time.strftime('%d/%m/%Y %H:%M:%S')
            edited_schedule = {}
            for key, value in schedule.items():
                edited_schedule.update({key: {"datetime": value, "state": "todo"}})
            schedule = edited_schedule
            print("ee = ", edited_schedule)
            create_schedule_display(schedule, participant_info)
            
        def sleep_extension_morning(self, participant_info):
            global schedule
            global isHab
            isHab = False
            schedule = {}
            morn_se_times = self.config_data['morn_se']
            morn_se_variables = self.config_data['morn_se_variable']
            for i, time_delta in enumerate(morn_se_times):
                morn_variable = morn_se_variables[i]
                if time_delta:
                    activation_time = self.start_time + timedelta(hours=int(time_delta.split(':')[0]), minutes=int(time_delta.split(':')[1]))
                    schedule[morn_variable] = activation_time.strftime('%d/%m/%Y %H:%M:%S') #str(activation_time)
            edited_schedule = {}
            for key, value in schedule.items():
                edited_schedule.update({key: {"datetime": value, "state": "todo"}})
            schedule = edited_schedule
            print("sem = ", schedule)
            create_schedule_display(schedule, participant_info)
            
        def sleep_restriction_morning(self, participant_info):
            global schedule
            global isHab
            isHab = False
            schedule = {}
            morn_sr_times = self.config_data['morn_sr']
            morn_sr_variables = self.config_data['morn_sr_variable']
            for i, time_delta in enumerate(morn_sr_times):
                morn_variable = morn_sr_variables[i]
                if time_delta:
                    activation_time = self.start_time + timedelta(hours=int(time_delta.split(':')[0]), minutes=int(time_delta.split(':')[1]))
                    schedule[morn_variable] = activation_time.strftime('%d/%m/%Y %H:%M:%S') #str(activation_time)
            edited_schedule = {}
            for key, value in schedule.items():
                edited_schedule.update({key: {"datetime": value, "state": "todo"}})
            schedule = edited_schedule
            print("srm = ", schedule)
            create_schedule_display(edited_schedule, participant_info)
            
    def create_input_boxes(self):
        labels = ["Participant ID:", "Experiment (se/sr/hab):", "Time of Day (morn/eve):", "Week Number (1/2):", "Start Time (24-hour format):"]
        initial_text = [self.id, self.experiment, self.time_of_day, self.week_number, self.time]
        x = self.width // 2
        y = self.height // 2 - 100
        spacing = 60
        for label, text in zip(labels, initial_text):
            input_box = InputBox(x, y, 400, 40, label, text)
            self.input_boxes.append(input_box)
            y += spacing

        submit_button = Button(x - 75, y + 60, 150, 40, "Submit", self.save_details)
        self.input_boxes.append(submit_button)
        
    
    def handle_events(self):
        def get_input_index():
            index = 0 
            for input_box in self.input_boxes[:-1]:
                index += 1
                if input_box.is_selected:
                    self.input_boxes[index -1].is_selected = False
                    break
            if index < len(self.input_boxes[:-1]):
                return index
            else:
                return 0
        for event in pygame.event.get():
            if event.type == QUIT:
                self.is_running = False
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.is_running = False
                elif event.key == K_TAB:
                    index = get_input_index()
                    self.input_boxes[index].is_selected = True
            for box in self.input_boxes:
                box.handle_event(event)


    def clear_screen(self):
        self.screen.fill((0, 0, 0))

    def draw(self):
        for box in self.input_boxes:
            box.draw(self.screen)

    def save_details(self):
        participant_id = self.input_boxes[0].text
        experiment = self.input_boxes[1].text
        time_of_day = self.input_boxes[2].text
        week_no = self.input_boxes[3].text
        start_time = self.input_boxes[4].text

        with open("experiment_details.txt", "w") as file:
            file.write(f"Participant ID: {participant_id}\n")
            file.write(f"Experiment: {experiment}\n")
            file.write(f"Time of Day: {time_of_day}\n")
            file.write(f"Week No: {week_no}\n")
            file.write(f"Start Time: {start_time}\n")

        start_time = datetime.combine(datetime.now().date(), datetime.strptime(start_time, "%H:%M").time())

        participant_info={"participant_id": participant_id, "experiment": experiment, "time_of_day": time_of_day, "week_no": week_no, "start_time": start_time}

        if experiment == "hab":
            config = self.TestBatteryConfiguration(start_time)
            config.read_config_file('configuration.csv')
            config.hab_night(participant_info) 
        elif time_of_day == "eve":
            config = self.TestBatteryConfiguration(start_time)
            config.read_config_file('configuration.csv')
            config.experiment_evening(participant_info)
        elif time_of_day == "morn" and experiment == "se":
            config = self.TestBatteryConfiguration(start_time)
            config.read_config_file('configuration.csv')
            config.sleep_extension_morning(participant_info)
        elif time_of_day == "morn" and experiment == "sr":
            config = self.TestBatteryConfiguration(start_time)
            config.read_config_file('configuration.csv')
            config.sleep_restriction_morning(participant_info)
             
        
        self.input_boxes = []


class InputBox:
    def __init__(self, x, y, width, height, label, initial_text=""):
        self.rect = pygame.Rect(x - width // 2, y, width, height)
        self.color = pygame.Color("gray")
        self.active_color = pygame.Color("gray")
        self.text_color = pygame.Color("black")
        self.label_color = pygame.Color("gray")
        self.active_text_color = pygame.Color("black")
        self.text = initial_text
        self.font = pygame.font.SysFont("Arial", 24)
        self.label = self.font.render(label, True, self.label_color)
        self.is_selected = False
        self.cursor_visible = False
        self.cursor_timer = 0

    def handle_event(self, event):
        if event.type == MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.is_selected = True
            else:
                self.is_selected = False
        elif event.type == KEYDOWN:
            if self.is_selected:
                if event.key == K_BACKSPACE:
                    self.text = self.text[:-1]
                elif event.key == K_TAB:
                    pass
                else:
                    self.text += event.unicode
                self.cursor_visible = True
                self.cursor_timer = pygame.time.get_ticks() + 500

    def draw(self, screen):
        pygame.draw.rect(screen, self.active_color if self.is_selected else self.color, self.rect)
        text_surface = self.font.render(self.text, True, self.active_text_color if self.is_selected else self.text_color)
        screen.blit(text_surface, (self.rect.x + 5, self.rect.y + 5))
        screen.blit(self.label, (self.rect.x - self.label.get_width() - 10, self.rect.y + 5))
        if self.is_selected:
            pygame.draw.line(screen, pygame.Color("black"), (self.rect.x + text_surface.get_width() + 5, self.rect.y + 5),
                             (self.rect.x + text_surface.get_width() + 5, self.rect.y + self.rect.height - 5))
        if self.cursor_visible:
            if pygame.time.get_ticks() >= self.cursor_timer:
                self.cursor_visible = False
            else:
                pygame.draw.line(screen, pygame.Color("black"),
                                 (self.rect.x + text_surface.get_width() + 5, self.rect.y + 5),
                                 (self.rect.x + text_surface.get_width() + 5, self.rect.y + self.rect.height - 5))

Teststarter()
