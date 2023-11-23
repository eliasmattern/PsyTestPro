import os
import re
import subprocess
import sys
import time as pythonTime
import tkinter as tk
import webbrowser
from datetime import datetime, timedelta
from tkinter import messagebox
import pygame
from components import Button
from lib import text_screen
from services import TranslateService, LanguageConfiguration, play_tasks
from .create_date_picker import create_date_picker
from .create_time_picker import create_time_picker
from services import TeststarterConfig


class CreateScheduleDisplay:
    def __init__(self, schedule, participant_info, teststarter, custom_variables, isHab=False):
        self.schedule = schedule
        self.participant_info = participant_info
        self.teststarter = teststarter
        self.custom_variables = custom_variables
        self.isHab = isHab
        self.schedule_page = 0
        self.language_config = LanguageConfiguration()
        self.translate_service = TranslateService(self.language_config)
        self.teststarter_config = TeststarterConfig()
        self.settings = self.teststarter_config.get_settings()
        self.black = pygame.Color(self.settings["backgroundColor"])
        self.light_grey = pygame.Color(self.settings["primaryColor"])
        self.red = pygame.Color(self.settings["dangerColor"])
        self.warning = pygame.Color(self.settings["warningColor"])
        self.success = pygame.Color(self.settings["successColor"])
        self.button_color = pygame.Color(self.settings["buttonColor"])
        self.button_text_color = pygame.Color(self.settings["buttonTextColor"])

    def display(self):

        # Open the pygame window at front of all windows open on screen
        os.environ['SDL_VIDEO_WINDOW_POS'] = '0,0'  # Set window position to top-left corner

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

        # Calculate column widths and row height based on screen size
        column_width = screen_width // 9
        column_start_x = screen_width - (
                column_width * 4) - 50  # Calculate column positions based on screen size (adjusted for right alignment)
        if self.isHab:
            column_start_x = screen_width - (
                    column_width * 2) - 50  # Hab night Calculate column positions based on screen size (adjusted for right alignment)

        max_row_height = 75
        splitted_schedule = self.split_dict(self.schedule, 20)

        row_height = screen_height // (len(splitted_schedule[self.schedule_page]) + 3) if screen_height // (
                len(splitted_schedule[
                        self.schedule_page]) + 3) < max_row_height else max_row_height  # +1 for the header row

        # Padding for cell
        cellPadding = 10

        # Input box fonts
        todo_input_box_font = pygame.font.Font(None, int(16 * width_scale_factor))
        newtime_input_box_font = pygame.font.Font(None, int(16 * width_scale_factor))
        newdate_input_box_font = pygame.font.Font(None, int(16 * width_scale_factor))

        # Input text font and cursor settings
        todo_input_text_font = pygame.freetype.Font(None, int(10 * width_scale_factor))
        cursor_color = self.light_grey
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
        newdate_input_text = ''  # Initialize the input text variable
        newtime_input_text = ''  # Initialize the input text variable
        todo_input_text = ''  # Initialize the input text variable

        newdate_input_active = False  # Initialize the text input variable
        newtime_input_active = False  # Initialize the text input variable
        todo_input_active = False  # Initialize the text input variable
        state_iterator = {'todo': 'skip', 'skip': 'done', 'done': 'todo'}
        todo_row_multiplicator = 3
        if self.isHab:
            todo_row_multiplicator = 1

        buttons = []
        page_butons = []

        # Create buttons
        run_button = Button(150 * width_scale_factor, 100 * height_scale_factor, 200 * width_scale_factor,
                            50 * height_scale_factor, 'runTeststarter', self.button_back, self.translate_service)
        settings_button = Button(150 * width_scale_factor, 200 * height_scale_factor, 200 * width_scale_factor,
                                 50 * height_scale_factor, 'changeSettings', self.change_settings,
                                 self.translate_service)
        quit_button = Button(150 * width_scale_factor, 300 * height_scale_factor, 200 * width_scale_factor,
                             50 * height_scale_factor, 'quit', self.button_quit_teststarter, self.translate_service)
        help_button = Button(150 * width_scale_factor, 400 * height_scale_factor, 200 * width_scale_factor,
                             50 * height_scale_factor, 'help', self.button_help, self.translate_service)
        english_button = Button(85 * width_scale_factor, 500 * height_scale_factor, 70 * width_scale_factor,
                                50 * height_scale_factor, 'english',
                                lambda: self.change_language(self.translate_service, self.language_config, 'en'),
                                self.translate_service)
        german_button = Button(215 * width_scale_factor, 500 * height_scale_factor, 70 * width_scale_factor,
                               50 * height_scale_factor, 'german',
                               lambda: self.change_language(self.translate_service, self.language_config, 'de'),
                               self.translate_service)

        buttons.append(run_button)
        buttons.append(settings_button)
        buttons.append(quit_button)
        buttons.append(help_button)
        buttons.append(english_button)
        buttons.append(german_button)

        left_button = Button(column_start_x + 1.5 * column_width, 760 * height_scale_factor, 40 * width_scale_factor,
                             40 * height_scale_factor, '<', lambda: self.page_update(splitted_schedule, False),
                             border_radius=90)
        right_button = Button(column_start_x + 2.5 * column_width, 760 * height_scale_factor, 40 * width_scale_factor,
                              40 * height_scale_factor, '>', lambda: self.page_update(splitted_schedule, True),
                              border_radius=90)

        page_butons.append(left_button)
        page_butons.append(right_button)

        def update_text():
            for button in buttons:
                button.update_text()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_pos = pygame.mouse.get_pos()
                    for row in range(1, len(splitted_schedule[self.schedule_page]) + 1):
                        if not self.isHab:
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
                            todo_input_values[row] = state_iterator[
                                splitted_schedule[self.schedule_page][
                                    list(splitted_schedule[self.schedule_page])[row - 1]][
                                    'state']]
                            active_column = 'todo'  # Set the active column
                            todo_input_active = True
                            newtime_input_active = False
                            newtime_active_row = None
                            newtimedate_active_row = None  # Deactivate the other column
                            newtimedate_input_active = False
                        if not self.isHab:
                            if newdate_input_box_rect.collidepoint(mouse_pos) and not self.isHab:
                                newdate_active_row = row
                                newdate_input_values[row] = \
                                    splitted_schedule[self.schedule_page][
                                        list(splitted_schedule[self.schedule_page])[row - 1]][
                                        'datetime'].split(' ')[0]
                                active_column = 'newdate'  # Set the active column
                                newtimedate_input_active = False
                                newdate_input_active = True
                                todo_active_row = None  # Deactivate the other column
                                todo_input_active = False
                                newtime_active_row = None
                                newtime_input_active = False
                                splitted_date = newdate_input_values[row].split('/')
                                day, month, year = splitted_date[0], splitted_date[1], splitted_date[2]
                                date = create_date_picker(int(year), int(month), int(day))
                                newdate_input_values[newdate_active_row] = date
                            elif newtime_input_box_rect.collidepoint(mouse_pos) and not self.isHab:
                                newtime_active_row = row
                                newtime_input_values[row] = ''
                                active_column = 'newtime'  # Set the active column
                                newtimedate_input_active = False
                                newtime_input_active = True
                                todo_active_row = None  # Deactivate the other column
                                todo_input_active = False
                                newdate_active_row = None
                                newdate_input_active = False
                                current_time = \
                                    splitted_schedule[self.schedule_page][
                                        list(splitted_schedule[self.schedule_page])[row - 1]][
                                        'datetime'].split(' ')[1]
                                splitted_time = current_time.split(':')
                                time_picker = create_time_picker(splitted_time[0], splitted_time[1],
                                                                 self.translate_service)
                                formatted_time = str(time_picker.time()[0]).rjust(2, '0') + ':' + str(
                                    time_picker.time()[1]).rjust(2, '0') + ':00'
                                if newtime_active_row in newtime_input_values:
                                    newtime_input_values[newtime_active_row] = formatted_time
                                else:
                                    newtime_input_values[newtime_active_row] = formatted_time
                for button in buttons:
                    button.handle_event(event)

                if len(splitted_schedule) > 1:
                    for button in page_butons:
                        button.handle_event(event)

            screen.fill(self.black)  # Fill the screen with the black color
            update_text()
            for button in buttons:
                button.draw(screen)

            font = pygame.font.Font(None, int(20 * width_scale_factor))  # Create font object for header
            if len(splitted_schedule) > 1:
                page_number_surface = font.render(str(self.schedule_page + 1) + '/' + str(len(splitted_schedule)), True,
                                                  self.light_grey)
                screen.blit(page_number_surface, (column_start_x + 2 * column_width, 775 * height_scale_factor))
                for button in page_butons:
                    button.draw(screen)

            # Display column headers with adjusted font size
            text_surface = font.render(' ' + self.translate_service.get_translation('task'), True,
                                       self.light_grey)  # Render the text 'Task' with the font and color light_grey
            screen.blit(text_surface,
                        (column_start_x, cellPadding))  # Blit the text surface to the screen at the specified position
            if not self.isHab:
                text_surface = font.render(' ' + self.translate_service.get_translation('date'), True,
                                           self.light_grey)  # Render the text 'Time'
                screen.blit(text_surface,
                            (column_start_x + column_width, cellPadding))  # Blit the text surface to the screen
                text_surface = font.render(' ' + self.translate_service.get_translation('time'), True,
                                           self.light_grey)  # Render the text 'Time'
                screen.blit(text_surface,
                            (column_start_x + (2 * column_width), cellPadding))  # Blit the text surface to the screen
            # text_surface = font.render('New Date and Time', True, light_grey) # Render the text 'New Date and Time'
            # screen.blit(text_surface, (column_start_x + (3 * column_width), cellPadding)) # Blit the text surface to the screen
            text_surface = font.render(' ' + self.translate_service.get_translation('skipDoneTodo'), True,
                                       self.light_grey)  # Render the text 'Skip/newtimedate'
            screen.blit(text_surface, (
                column_start_x + (todo_row_multiplicator * column_width), cellPadding))  # Adjusted blitting position

            # Display each task with adjusted font size
            font = pygame.font.Font(None, int(16 * width_scale_factor))
            row = 1  # Initialize the row counter
            # Loop through each task and datetime in the schedule dictionary

            for task, info in splitted_schedule[self.schedule_page].items():
                date = info['datetime'].split(' ')[0]
                time = info['datetime'].split(' ')[1]
                state = info['state']
                # Replace underscores with spaces in the task name
                task_name = task.replace('_', ' ')
                task_name = ' ' + task_name

                # Format the task and datetime strings
                task_text = font.render(task_name, True, self.light_grey)  # Render the task name text

                # Display the task details in each column with adjusted row height
                screen.blit(task_text,
                            (column_start_x, row * row_height + cellPadding))  # Blit the task_text to the screen
                # Adjusted blitting position for the 'Skip/newtimedate' column
                skip_newtimedate_text = font.render('To Do/Skip', True, self.light_grey)  # Render the text 'To Do/Skip'

                # Render input boxes for 'New Date' and ' New Time' and 'Skip/ToDo' columns
                if not self.isHab:
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
                if not self.isHab:
                    pygame.draw.rect(screen, self.light_grey, newdate_input_box_rect, 1)
                    pygame.draw.rect(screen, self.light_grey, newtime_input_box_rect, 1)
                pygame.draw.rect(screen, self.light_grey, todo_input_box_rect, 1)

                # Render input value
                if not self.isHab:
                    if row in newdate_input_values:
                        newdate_input_value = newdate_input_values[row]
                        newdate_input_text_surface = newdate_input_box_font.render(newdate_input_value, True,
                                                                                   self.light_grey)
                        if not self.is_valid_datetime_format(newdate_input_value + ' ' + time):
                            newdate_input_text_surface = newdate_input_box_font.render(newdate_input_value, True,
                                                                                       self.red)
                        else:
                            newdate_input_text_surface = newdate_input_box_font.render(newdate_input_value, True,
                                                                                       self.light_grey)
                            splitted_schedule[self.schedule_page][list(splitted_schedule[self.schedule_page])[row - 1]][
                                'datetime'] = newdate_input_value + ' ' + time
                        screen.blit(newdate_input_text_surface, newdate_input_box_rect.move(5, 5))
                    elif newdate_active_row == row:
                        newdate_input_text_surface = newdate_input_box_font.render(newdate_input_text, True,
                                                                                   self.light_grey)
                        screen.blit(newdate_input_text_surface, newdate_input_box_rect.move(5, 5))
                    elif newdate_active_row != row:
                        newdate_input_text_surface = newdate_input_box_font.render(date, True, self.light_grey)
                        screen.blit(newdate_input_text_surface, newdate_input_box_rect.move(5, 5))

                    if row in newtime_input_values:
                        newtime_input_value = newtime_input_values[row]
                        newtime_input_text_surface = newtime_input_box_font.render(newtime_input_value, True,
                                                                                   self.light_grey)
                        if not self.is_valid_datetime_format(date + ' ' + newtime_input_value):
                            newtime_input_text_surface = newtime_input_box_font.render(newtime_input_value, True,
                                                                                       self.red)
                        else:
                            newtime_input_text_surface = newtime_input_box_font.render(newtime_input_value, True,
                                                                                       self.light_grey)
                            splitted_schedule[self.schedule_page][list(splitted_schedule[self.schedule_page])[row - 1]][
                                'datetime'] = date + ' ' + newtime_input_value
                        screen.blit(newtime_input_text_surface, newtime_input_box_rect.move(5, 5))
                    elif newtime_active_row == row:
                        newtime_input_text_surface = newtime_input_box_font.render(newtime_input_text, True,
                                                                                   self.light_grey)
                        screen.blit(newtime_input_text_surface, newtime_input_box_rect.move(5, 5))
                    elif newtime_active_row != row:
                        newtime_input_text_surface = newtime_input_box_font.render(time, True, self.light_grey)
                        screen.blit(newtime_input_text_surface, newtime_input_box_rect.move(5, 5))

                todo_color = {'todo': self.light_grey, 'skip': self.warning, 'done': self.success}
                if row in todo_input_values:
                    todo_input_value = todo_input_values[row]
                    todo_input_text_surface = todo_input_box_font.render(
                        self.translate_service.get_translation(todo_input_value), True,
                        todo_color[todo_input_value.lower()])

                    if todo_input_value.lower() == 'todo' or todo_input_value.lower() == 'done' or todo_input_value.lower() == 'skip':
                        splitted_schedule[self.schedule_page][list(splitted_schedule[self.schedule_page])[row - 1]][
                            'state'] = todo_input_value.lower()
                    else:
                        todo_input_text_surface = todo_input_box_font.render(todo_input_value, True, self.red)
                    screen.blit(todo_input_text_surface, todo_input_box_rect.move(5, 5))
                elif todo_active_row == row:
                    todo_input_text_surface = todo_input_box_font.render(todo_input_text, True,
                                                                         todo_color[todo_input_values[row].lower()])
                    screen.blit(todo_input_text_surface, todo_input_box_rect.move(5, 5))
                elif todo_active_row != row:
                    todo_input_text_surface = todo_input_box_font.render(self.translate_service.get_translation(state),
                                                                         True,
                                                                         todo_color[
                                                                             splitted_schedule[self.schedule_page][
                                                                                 list(splitted_schedule[
                                                                                          self.schedule_page])[
                                                                                     row - 1]]['state'].lower()])
                    screen.blit(todo_input_text_surface, todo_input_box_rect.move(5, 5))

                # Render the cursor
                if (active_column == 'newdate' and newdate_active_row == row):
                    cursor_x = 0
                    cursor_y = 0
                    cursor_height = 0
                    input_text_surface = None

                    if active_column == 'newdate':
                        cursor_x = newdate_input_box_rect.left + newdate_input_text_surface.get_width() + 5
                        cursor_y = newdate_input_box_rect.top + 5
                        cursor_height = 14
                        input_text_surface = newdate_input_text_surface

                    pygame.draw.line(screen, cursor_color, (cursor_x, cursor_y), (cursor_x, cursor_y + cursor_height),
                                     cursor_width)

                row += 1  # Increment the row counter

                max_grid_rows = len(splitted_schedule[self.schedule_page])

                final_y = (max_grid_rows + 1) * row_height

                # Draw grid lines
                grid_range = 5 if not self.isHab else 3
                for i in range(grid_range):
                    x = column_start_x + (i * column_width)
                    pygame.draw.line(screen, self.light_grey, (x, 0), (x, final_y), 1)

                for i in range(1, max_grid_rows + 2):
                    y = i * row_height
                    pygame.draw.line(screen, self.light_grey, (column_start_x, y),
                                     (column_start_x + ((grid_range - 1) * column_width), y), 1)

            # Update the cursor visibility
            current_time = pygame.time.get_ticks()
            if current_time - cursor_timer > cursor_blink_interval:
                cursor_visible = not cursor_visible
                cursor_timer = current_time

            pygame.display.flip()  # Flip the display to update the screen

    def text_objects(self, text, font):
        text_surface = font.render(text, True, self.button_text_color)
        return text_surface, text_surface.get_rect()

    def button_back(self):

        # set the display mode to fullscreen
        screen = pygame.display.get_surface()

        # Setting the window caption
        pygame.display.set_caption('Schedule Processor')

        # set the color of the screen to black
        screen.fill(self.black)

        filtered_schedule = {key: value for key, value in self.schedule.items() if value['state'] == 'todo'}
        # convert the schedule to a list of tuples and sort it by time
        sorted_schedule = sorted(
            [(datetime.strptime(info['datetime'], '%d/%m/%Y %H:%M:%S'), event) for event, info in
             filtered_schedule.items()])
        check_for_old_tasks = True
        play_next_task = False
        start_time = datetime.now()
        running = True
        while running:
            pygame.mouse.set_visible(True)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            if check_for_old_tasks:
                filtered_dict = {
                    key: value for key, value in self.schedule.items()
                    if value['state'] == 'todo'
                       and start_time < datetime.strptime(value['datetime'], '%d/%m/%Y %H:%M:%S') < datetime.now()
                }
                # Print the filtered list
                for item in filtered_dict:
                    upcoming_event = item

                    play_tasks(self.participant_info, upcoming_event, self.schedule, self.translate_service,
                               self.custom_variables)
                    pygame.mouse.set_visible(True)
                    self.schedule[upcoming_event]['state'] = 'done'
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
            screen.fill(self.black)
            next_event_in_seconds = -1
            if self.isHab:
                next_event_in_seconds = 0
            if next_event:
                next_event_in_seconds = (next_event[0] - now).total_seconds()
                # calculate the time until the next event
                if next_event is not None:
                    event_message = ' ' + self.translate_service.get_translation('until') + f' {next_event[1]}'
                else:
                    event_message = 'No more events today'

                countdown = str(timedelta(seconds=round(next_event_in_seconds)))

            # Display the message on screen
            if self.isHab or not next_event:
                font = pygame.font.Font(None, 35)
                text = font.render(self.translate_service.get_translation('allTasksCompleted'), True, self.light_grey)
            else:
                font = pygame.font.Font(None, 35)
                text = font.render(countdown + event_message, True, self.light_grey)
            screen.blit(text, (50, 50))  # you can adjust the position as needed

            screen_info = pygame.display.Info()

            # Draw the 'Edit Teststarter' button in the bottom right corner
            screen_width = screen_info.current_w
            # Store the screen height in a new variable
            screen_height = screen_info.current_h

            # Store the original screen dimensions used to design this program
            original_width = 1280
            original_height = 800

            # Calculate scaling factors for position and size adjustments (this is how we can make sure that the program adjusts to any screen it is executed on)
            width_scale_factor = screen_width / original_width
            height_scale_factor = screen_height / original_height

            edit_button_x = screen_width - 250 * width_scale_factor
            edit_button_y = screen_height - 80 * height_scale_factor
            edit_button_width = 200 * width_scale_factor
            edit_button_height = 50 * height_scale_factor

            mouse = pygame.mouse.get_pos()
            click = pygame.mouse.get_pressed()

            if edit_button_x + edit_button_width > mouse[0] > edit_button_x and edit_button_y + edit_button_height > \
                    mouse[1] > edit_button_y:
                pygame.draw.rect(screen, self.button_color,
                                 (edit_button_x, edit_button_y, edit_button_width, edit_button_height))
                if click[0] == 1:
                    self.display()  # Call display() when the button is clicked
            else:
                pygame.draw.rect(screen, self.button_color,
                                 (edit_button_x, edit_button_y, edit_button_width, edit_button_height))
            if next_event:
                if 75 + edit_button_width > mouse[0] > 75 and edit_button_y + edit_button_height > mouse[
                    1] > edit_button_y:
                    pygame.draw.rect(screen, self.button_color,
                                     (75, edit_button_y, edit_button_width, edit_button_height))
                    if click[0] == 1:
                        play_next_task = True
                else:
                    pygame.draw.rect(screen, self.button_color,
                                     (75, edit_button_y, edit_button_width, edit_button_height))

            # Draw the text on the button
            small_text = pygame.font.Font(None, 20)
            text_surf, text_rect = self.text_objects(self.translate_service.get_translation('editTeststarter'),
                                                     small_text)
            text_rect.center = (
                (edit_button_x + (edit_button_width / 2)), (edit_button_y + (edit_button_height / 2)))
            screen.blit(text_surf, text_rect)

            next_surf, next_rect = self.text_objects(self.translate_service.get_translation('nextTask'), small_text)
            next_rect.center = ((75 + (edit_button_width / 2)), (edit_button_y + (edit_button_height / 2)))
            if next_event:
                screen.blit(next_surf, next_rect)
            # update the display
            pygame.display.flip()
            if play_next_task:
                check_for_old_tasks = True
                upcoming_event = next_event[1]
                beep_sound = pygame.mixer.Sound('./lib/beep.wav')
                beep_sound.play()
                play_tasks(self.participant_info, upcoming_event, self.schedule, self.translate_service,
                           self.custom_variables)
                pygame.mouse.set_visible(True)
                self.schedule[upcoming_event]['state'] = 'done'
                sorted_schedule = [(dt, desc) for dt, desc in sorted_schedule if desc != upcoming_event]
                print(sorted_schedule)
                play_next_task = False

            if not self.isHab or next_event_in_seconds == -1:
                if round(next_event_in_seconds) == 1:
                    check_for_old_tasks = True
                    upcoming_event = next_event[1]
                    pythonTime.sleep(1.1)
                    beep_sound = pygame.mixer.Sound('./lib/beep.wav')
                    beep_sound.play()
                    play_tasks(self.participant_info, upcoming_event, self.schedule, self.translate_service,
                               self.custom_variables)
                    pygame.mouse.set_visible(True)
                    self.schedule[upcoming_event]['state'] = 'done'
            elif len(sorted_schedule) > 0:
                for task in self.schedule.items():
                    if self.schedule[task[0]]['state'] == 'todo':
                        if self.schedule[task[0]]['type'] == 'text':
                            title = self.schedule[task[0]]['value']['title']
                            now = datetime.now()
                            formatted_timestamp = now.strftime('%Y.%m.%d %H:%M:%S')
                            title = title.format(id=self.participant_info['participant_id'],
                                                 experiment=self.participant_info['experiment'],
                                                 startTime=self.participant_info['start_time'],
                                                 timestamp=formatted_timestamp)

                            description = self.schedule[task[0]]['value']['description']
                            description = description.format(id=self.participant_info['participant_id'],
                                                             experiment=self.participant_info['experiment'],
                                                             startTime=self.participant_info['start_time'],
                                                             timestamp=formatted_timestamp)

                            text_screen(title, description, self.translate_service.get_translation('escToReturn'))
                            self.schedule[task[0]]['state'] = 'done'
                        elif self.schedule[task[0]]['type'] == 'command':
                            now = datetime.now()
                            formatted_timestamp = now.strftime('%Y.%m.%d %H:%M:%S')
                            command = self.schedule[task[0]]['value']
                            command = command.format(id=self.participant_info['participant_id'],
                                                     experiment=self.participant_info['experiment'],
                                                     startTime=self.participant_info['start_time'],
                                                     timestamp=formatted_timestamp)
                            process = subprocess.Popen(command)
                            process.communicate()
                            self.schedule[task[0]]['state'] = 'done'
                sorted_schedule = []

        pygame.quit()

    def is_valid_datetime_format(self, datetime_str):
        # This pattern strictly matches DD/MM/YYYY HH:MM:SS
        pattern = r'^\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}$'
        return re.match(pattern, datetime_str) is not None

    def change_settings(self):
        self.schedule_page = 0

        time = str(self.participant_info['start_time']).split(' ')[1]
        splittedTime = time.split(':')
        formattedTime = splittedTime[0] + ':' + splittedTime[1]
        self.teststarter(self.participant_info['participant_id'], self.participant_info['experiment'], formattedTime,
                         self.custom_variables)

    def change_language(self, translateService, language_config, lang):
        translateService.set_language(lang)
        language_config.update_language_config(lang)

    def button_quit_teststarter(self):
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
        root.geometry('+' + str(posX) + '+' + str(posY))
        # Show a messagebox asking for confirmation
        response = messagebox.askyesno(self.translate_service.get_translation('confirmExit'),
                                       self.translate_service.get_translation('confirmExitText'))

        # If the user clicked 'Yes', then close the program
        if response == True:
            pygame.quit()
            quit()

        # Destroy the root window
        root.destroy()

    def button_help(self):
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
        root.geometry('+' + str(posX) + '+' + str(posY))
        # Show a messagebox asking for confirmation
        response = messagebox.askyesno(self.translate_service.get_translation('help'),
                                       self.translate_service.get_translation('helpText'))

        # If the user clicked 'Yes', then open browser
        if response == True:
            webbrowser.open('https://github.com/eliasmattern/teststarter')

            # Destroy the root window
        root.destroy()

    def split_dict(self, input_dict, chunk_size):
        dict_list = [{}]
        current_dict = 0

        for key, value in input_dict.items():
            dict_list[current_dict][key] = value
            if len(dict_list[current_dict]) >= chunk_size:
                dict_list.append({})
                current_dict += 1

        return dict_list

    def page_update(self, schedule, increment):
        if increment:
            self.schedule_page = (self.schedule_page + 1) % len(schedule)
        else:
            self.schedule_page = (self.schedule_page - 1) if self.schedule_page > 0 else len(schedule) - 1
