import os
import re
import subprocess
import sys
import time as pythonTime
import webbrowser
from datetime import datetime, timedelta, date as python_date
import pygame
from components import Button, DataTable, QuestionDialog, DatePickerComponent
from lib import text_screen
from services import TranslateService, LanguageConfiguration, play_tasks
from .create_time_picker import create_time_picker
from services import PsyTestProConfig


class CreateScheduleDisplay:
    def __init__(self, schedule, participant_info, psy_test_pro, custom_variables, isHab=False, file_name=''):
        self.schedule = schedule
        self.participant_info = participant_info
        self.psy_test_pro = psy_test_pro
        self.custom_variables = custom_variables
        self.isHab = isHab
        self.file_name = file_name
        self.schedule_page = 0
        self.language_config = LanguageConfiguration()
        self.translate_service = TranslateService(self.language_config)
        self.psy_test_pro_config = PsyTestProConfig()
        self.settings = self.psy_test_pro_config.get_settings()
        self.black = pygame.Color(self.settings["backgroundColor"])
        self.light_grey = pygame.Color(self.settings["primaryColor"])
        self.red = pygame.Color(self.settings["dangerColor"])
        self.warning = pygame.Color(self.settings["warningColor"])
        self.success = pygame.Color(self.settings["successColor"])
        self.button_color = pygame.Color(self.settings["buttonColor"])
        self.button_text_color = pygame.Color(self.settings["buttonTextColor"])
        self.grid_color = pygame.Color(self.settings["gridColor"])
        self.showTasks = self.settings["showNextTask"]
        self.todo_input_values = {}
        self.newdate_input_values = {}
        self.newtime_input_values = {}
        self.show_help_dialog = False
        self.show_quit_dialog = False
        self.show_date_picker = False
        self.screen_width = None
        self.screen_height = None
        self.column_width = None
        self.splitted_schedule = self.split_dict(self.schedule, 15)
        self.headers = [self.translate_service.get_translation('task'),
                        self.translate_service.get_translation('date'),
                        self.translate_service.get_translation('time'),
                        self.translate_service.get_translation('skipDoneTodo')]
        self.date_picker = None

        self.actions = [None,
                        lambda: self.open_date_picker(self.data_table.action_data["data"]),
                        lambda: self.data_table.set_action_data(
                            self.open_time_picker(self.data_table.action_data["data"])),
                        lambda: self.data_table.set_action_data(self.switch_state(self.data_table.action_data["data"]))]
        self.play_next_task = False

        if self.isHab:
            self.headers = [self.translate_service.get_translation('task'),
                            self.translate_service.get_translation('skipDoneTodo')]
            self.actions = [None,
                            lambda: self.data_table.set_action_data(
                                self.switch_state(self.data_table.action_data["data"]))]
        self.data_table = None

    def display(self):
        # Open the pygame window at front of all windows open on screen
        os.environ['SDL_VIDEO_WINDOW_POS'] = '0,0'  # Set window position to top-left corner

        # Initializing Pygame
        pygame.init()

        # Get the screen width and height from the current device in use
        screen_info = pygame.display.Info()
        # Store the screen width in a new variable
        self.screen_width = screen_info.current_w
        # Store the screen height in a new variable
        self.screen_height = screen_info.current_h

        # Store the original screen dimensions used to design this program
        original_width = 1280
        original_height = 800

        # Calculate scaling factors for position and size adjustments (this is how we can make sure that the program adjusts to any screen it is executed on)
        width_scale_factor = self.screen_width / original_width
        height_scale_factor = self.screen_height / original_height

        # Creating a fullscreen display surface
        screen = pygame.display.get_surface()

        # Setting the window caption
        pygame.display.set_caption('Schedule Editor')

        # Calculate column widths and row height based on screen size
        self.column_width = self.screen_width // 9

        max_rows = 30

        self.data_table = DataTable(self.headers, max_rows,
                                    (self.screen_width - len(self.headers) * self.column_width - 50,
                                     self.screen_height / 100 * 5),
                                    data=self.get_table_data(),
                                    max_cell_width=self.column_width, actions=self.actions,
                                    translate_service=self.translate_service,
                                    max_height=self.screen_height // 100 * 80)

        buttons = []

        # Create buttons
        run_button = Button(150 * width_scale_factor, 100 * height_scale_factor, 200 * width_scale_factor,
                            50 * height_scale_factor, 'runExperiment', self.run_psy_test_pro, self.translate_service)
        settings_button = Button(150 * width_scale_factor, 200 * height_scale_factor, 200 * width_scale_factor,
                                 50 * height_scale_factor, 'changeSettings', self.change_settings,
                                 self.translate_service)
        quit_button = Button(150 * width_scale_factor, 300 * height_scale_factor, 200 * width_scale_factor,
                             50 * height_scale_factor, 'quit', self.quit_psy_test_pro, self.translate_service)
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

        help_dialog = QuestionDialog(500, 200, 'help', 'help', 'helpText', self.translate_service,
                                     lambda: self.help_action(), action_key='github')

        quit_dialog = QuestionDialog(500, 200, 'confirmExit', 'confirmExit', 'confirmExitText', self.translate_service,
                                     lambda: self.quit_action(), action_key='quit')

        self.date_picker = DatePickerComponent('26/12/2023', 'datepicker', self.translate_service,
                                               lambda: self.data_table.set_action_data(
                                                   '/'.join([str(self.date_picker.day), str(self.date_picker.month),
                                                             str(self.date_picker.year)]))
                                               , action_key='save')

        def update_text():
            for button in buttons:
                button.update_text()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if self.show_help_dialog:
                    help_dialog.handle_events(event)
                elif self.show_date_picker:
                    self.date_picker.handle_events(event)
                elif self.show_quit_dialog:
                    quit_dialog.handle_events(event)
                else:
                    for button in buttons:
                        button.handle_event(event)

                    self.data_table.handle_events(event)

            screen.fill(self.black)  # Fill the screen with the black color
            update_text()
            for button in buttons:
                button.draw(screen)

            self.data_table.draw(screen)
            if self.show_help_dialog:
                help_dialog.draw(screen)
            if not help_dialog.is_open:
                self.show_help_dialog = False
                help_dialog.is_open = True

            if self.show_quit_dialog:
                quit_dialog.draw(screen)
            if not quit_dialog.is_open:
                self.show_quit_dialog = False
                quit_dialog.is_open = True

            if self.show_date_picker:
                self.date_picker.draw(screen)
            if not self.date_picker.is_open:
                self.show_date_picker = False
                self.date_picker.is_open = True

            pygame.display.flip()  # Flip the display to update the screen

    def text_objects(self, text, font):
        text_surface = font.render(text, True, self.button_text_color)
        return text_surface, text_surface.get_rect()

    def run_psy_test_pro(self):
        self.save_data(self.data_table.data)
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
        self.play_next_task = False
        start_time = datetime.now()
        # Store the original screen dimensions used to design this program
        original_width = 1280
        original_height = 800

        # Calculate scaling factors for position and size adjustments (this is how we can make sure that the program adjusts to any screen it is executed on)
        width_scale_factor = self.screen_width / original_width
        height_scale_factor = self.screen_height / original_height
        edit_button_x = self.screen_width - 250 * width_scale_factor
        edit_button_y = self.screen_height - 80 * height_scale_factor
        edit_button_width = 200 * width_scale_factor
        edit_button_height = 50 * height_scale_factor
        next_button = Button(75 + (edit_button_width / 2), edit_button_y + (edit_button_height / 2), 300, 50,
                             'nextTask', lambda: self.play_task(), translate_service=self.translate_service)
        edit_button = Button(edit_button_x + (edit_button_width / 2), edit_button_y + (edit_button_height / 2), 300, 50,
                             'editSchedule', lambda: self.edit_schedule(),
                             translate_service=self.translate_service)
        running = True
        while running:
            for event in pygame.event.get():
                next_button.handle_event(event)
                edit_button.handle_event(event)
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
                for item in filtered_dict:
                    upcoming_event = item

                    state = play_tasks(self.file_name, self.participant_info, upcoming_event, self.schedule,
                                       self.translate_service,
                                       self.custom_variables)
                    pygame.mouse.set_visible(True)
                    if state:
                        self.schedule[upcoming_event]['state'] = 'done'
                    else:
                        self.schedule[upcoming_event]['state'] = 'error'
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
            if next_event:
                next_button.set_hidden(False)
                next_button.set_active(True)
                next_button.draw(screen)
            else:
                next_button.set_hidden(True)
                next_button.set_active(False)
                next_button.draw(screen)
            edit_button.draw(screen)

            next_event_in_seconds = -1
            if self.isHab:
                next_event_in_seconds = 0
            if next_event:
                next_event_in_seconds = (next_event[0] - now).total_seconds()
                # calculate the time until the next event
                if next_event is not None:
                    if self.showTasks:
                        event_message = ' ' + self.translate_service.get_translation('until') + f' {next_event[1]}'
                        countdown = str(timedelta(seconds=round(next_event_in_seconds)))
                    else:
                        event_message = ''
                        countdown = ''

                else:
                    event_message = 'No more events today'


            # Display the message on screen
            if self.isHab or not next_event:
                font = pygame.font.Font(None, 35)
                text = font.render(self.translate_service.get_translation('allTasksCompleted'), True, self.light_grey)
            else:
                font = pygame.font.Font(None, 35)
                text = font.render(countdown + event_message, True, self.light_grey)
            screen.blit(text, (50, 50))  # you can adjust the position as needed

            screen_info = pygame.display.Info()

            # Draw the 'Edit Schedule' button in the bottom right corner
            self.screen_width = screen_info.current_w
            # Store the screen height in a new variable
            self.screen_height = screen_info.current_h

            # update the display
            pygame.display.flip()
            if self.play_next_task:
                check_for_old_tasks = True
                upcoming_event = next_event[1]
                beep_sound = pygame.mixer.Sound('./lib/beep.wav')
                beep_sound.play()
                state = play_tasks(self.file_name, self.participant_info, upcoming_event, self.schedule,
                                   self.translate_service,
                                   self.custom_variables)
                pygame.mouse.set_visible(True)
                if state:
                    self.schedule[upcoming_event]['state'] = 'done'
                else:
                    self.schedule[upcoming_event]['state'] = 'error'
                sorted_schedule = [(dt, desc) for dt, desc in sorted_schedule if desc != upcoming_event]
                print(sorted_schedule)
                self.play_next_task = False

            if not self.isHab or next_event_in_seconds == -1:
                if round(next_event_in_seconds) == 1:
                    check_for_old_tasks = True
                    upcoming_event = next_event[1]
                    pythonTime.sleep(1.1)
                    beep_sound = pygame.mixer.Sound('./lib/beep.wav')
                    beep_sound.play()
                    state = play_tasks(self.file_name, self.participant_info, upcoming_event, self.schedule,
                                       self.translate_service,
                                       self.custom_variables)
                    pygame.mouse.set_visible(True)
                    if state:
                        self.schedule[upcoming_event]['state'] = 'done'
                    else:
                        self.schedule[upcoming_event]['state'] = 'error'
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
        self.psy_test_pro(self.participant_info['participant_id'], self.participant_info['experiment'], formattedTime,
                          self.custom_variables)

    def change_language(self, translateService, language_config, lang):
        translateService.set_language(lang)
        language_config.update_language_config(lang)
        if not self.isHab:
            self.headers = [self.translate_service.get_translation('task'),
                            self.translate_service.get_translation('date'),
                            self.translate_service.get_translation('time'),
                            self.translate_service.get_translation('skipDoneTodo')]
        else:
            self.headers = [self.translate_service.get_translation('task'),
                            self.translate_service.get_translation('skipDoneTodo')]
        self.data_table.columns = self.headers
        if len(self.data_table.data) > 0:
            self.data_table.table_width, self.data_table.table_height, self.data_table.row_width, self.data_table.row_height, self.data_table.header_heigth = self.data_table.get_table_proportions()

    def quit_psy_test_pro(self):
        self.show_quit_dialog = True

    def quit_action(self):
        pygame.quit()
        quit()

    def button_help(self):
        self.show_help_dialog = True

    def help_action(self):
        webbrowser.open('https://github.com/eliasmattern/PsyTestPro')

    def split_dict(self, input_dict, chunk_size):
        dict_list = [{}]
        current_dict = 0

        for key, value in input_dict.items():
            dict_list[current_dict][key] = value
            if len(dict_list[current_dict]) >= chunk_size:
                dict_list.append({})
                current_dict += 1

        return dict_list

    def page_update(self, schedule, increment, data):
        self.save_data(data)
        self.todo_input_values = {}
        self.newdate_input_values = {}
        self.newtime_input_values = {}

        if increment:
            self.schedule_page = (self.schedule_page + 1) % len(schedule)
        else:
            self.schedule_page = (self.schedule_page - 1) if self.schedule_page > 0 else len(schedule) - 1

    def open_date_picker(self, date):
        self.show_date_picker = True
        self.date_picker.day, self.date_picker.month, self.date_picker.year = date.split('/')
        self.date_picker.create_calendar(int(self.date_picker.year), int(self.date_picker.month),
                                         int(self.date_picker.day))
        # split_date = date.split('/')
        # day, month, year = split_date[0], split_date[1], split_date[2]
        # date = create_date_picker(int(year), int(month), int(day))
        # return date

    def open_time_picker(self, time):
        split_time = time.split(':')
        time_picker = create_time_picker(split_time[0], split_time[1],
                                         self.translate_service)
        formatted_time = str(time_picker.time()[0]).rjust(2, '0') + ':' + str(
            time_picker.time()[1]).rjust(2, '0') + ':00'
        return formatted_time

    def switch_state(self, state):
        state_iterator = {'todo': {'value': 'skip', 'color': self.warning, 'key': 'skip'},
                          'skip': {'value': 'done', 'color': self.success, 'key': 'done'},
                          'done': {'value': 'todo', 'color': self.light_grey, 'key': 'todo'},
                          'error': {'value': 'todo', 'color': self.light_grey, 'key': 'todo'}}
        return state_iterator[state['value']]

    def save_data(self, data):
        for task in data:
            if not self.isHab:
                self.schedule[task[0].replace(' ', '_')]['datetime'] = task[1] + ' ' + task[2]
                self.schedule[task[0].replace(' ', '_')]['state'] = task[3]['value']
            else:
                self.schedule[task[0].replace(' ', '_')]['state'] = task[1]['value']

    def get_table_data(self):
        states = {'todo': {'value': 'todo', 'color': self.light_grey, 'key': 'todo'},
                  'skip': {'value': 'skip', 'color': self.warning, 'key': 'skip'},
                  'done': {'value': 'done', 'color': self.success, 'key': 'done'},
                  'error': {'value': 'error', 'color': self.red, 'key': 'error'}}
        data = []
        for key, value in self.schedule.items():
            date, time = value['datetime'].split(' ')
            if self.isHab:
                data.append(
                    [key.replace('_', ' '), {'value': value['state'], 'color': states[value['state']]['color'],
                                             'key': states[value['state']]['key']}])
            else:
                data.append(
                    [key.replace('_', ' '), date, time,
                     {'value': value['state'], 'color': states[value['state']]['color'],
                      'key': states[value['state']]['key']}])
        return data

    def edit_schedule(self):
        self.play_next_task = False
        self.schedule_page = 0
        self.display()

    def play_task(self):
        self.play_next_task = True
