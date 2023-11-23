# Add buttons to the left side of the screen

# Script updated to add input entry to relevant columns

import pygame
import sys
from pygame.locals import *
from datetime import datetime, timedelta
from components import InputBox, Button
from views import CreateScheduleDisplay, ExperimentConfig, SettingsView
import re
from services import TranslateService, LanguageConfiguration, TeststarterConfig


class Teststarter:
    def __init__(self, id='', experiment='', time='', custom_variables={}):
        self.screen = pygame.display.get_surface()
        if self.screen == None:
            pygame.init()
            self.screen = pygame.display.set_mode((0, 0))
            pygame.display.toggle_fullscreen()
        self.width, self.height = pygame.display.get_surface().get_rect().size
        pygame.display.set_caption('Teststarter')
        pygame.scrap.init()
        self.teststarterConfig = TeststarterConfig()
        self.teststarterConfig.load_experiments()
        self.lang = 'en'
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Arial', 24)
        self.input_boxes = {}
        self.buttons = []
        self.errors = []
        self.language_config = LanguageConfiguration()
        self.translateService = TranslateService(self.language_config)
        self.lang = self.load_config_lang()
        self.id = id
        self.experiment = experiment
        self.time = time
        self.custom_variables = []
        for key, value in custom_variables.items():
            self.custom_variables.append(value)
        self.experiment_config_display = ExperimentConfig(self.translateService)
        self.create_input_boxes()
        self.is_running = True
        self.start_time = None
        self.settings_view = SettingsView()
        self.settings = self.teststarterConfig.get_settings()
        self.background_color = pygame.Color(self.settings['backgroundColor'])
        self.primary_color = pygame.Color(self.settings['primaryColor'])
        self.inactive_button_color = pygame.Color(self.settings['inactiveButtonColor'])
        self.button_text_color = pygame.Color(self.settings["buttonTextColor"])
        self.button_color = pygame.Color(self.settings["buttonColor"])

        while self.is_running:
            self.update_text()
            self.handle_events()
            self.clear_screen()
            self.draw()
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()

    def is_valid_time_format(slef, datetime_str):
        # This pattern strictly matches DD/MM/YYYY HH:MM:SS
        pattern = r'^(?:[01]\d|2[0-3]):[0-5]\d$'
        return re.match(pattern, datetime_str) is not None

    def create_input_boxes(self):
        custom_variables = self.teststarterConfig.load_custom_variables()
        labels = ['participantId', 'experiment', 'startTime']
        experiments_string = ''
        for experiment in self.teststarterConfig.experiments:
            experiments_string = experiments_string + experiment + ', '
        if ',' in experiments_string:
            experiments_string = experiments_string[:-2]
        information = ['', '(' + experiments_string + ')', 'hh:mm']
        initial_text = [self.id, self.experiment, self.time]
        if len(self.custom_variables) == len(custom_variables):
            for value in custom_variables:
                labels.append(value)
                information.append('')
            for variable in self.custom_variables:
                initial_text.append(variable)
        else:
            for value in custom_variables:
                labels.append(value)
                information.append('')
                initial_text.append('')
        x = self.width // 2
        y = self.height // 2 - 100
        spacing = 60
        for label, text, info in zip(labels, initial_text, information):
            if len(self.input_boxes) > 2:
                input_box = InputBox(x, y, 400, 40, label, None, info, text)
                self.input_boxes[label] = input_box
            else:
                input_box = InputBox(x, y, 400, 40, label, self.translateService, info, text)
                self.input_boxes[label] = input_box
            y += spacing

        exit_button = Button(x - 75, y + 60, 100, 40, 'exit', self.exit, self.translateService)
        submit_button = Button(x + 75, y + 60, 100, 40, 'submit', self.save_details, self.translateService)
        settings_button = Button(self.width - 175, 100, 250, 40, 'settings', lambda: self.settings_view.display(Teststarter, self.translateService, self.language_config),
                               self.translateService)
        create_experiment_button = Button(self.width - 175, 150, 250, 40, 'configureExperiment',
                                          lambda: self.experiment_config_display.display(Teststarter),
                                          self.translateService)

        self.buttons.append(exit_button)
        self.buttons.append(settings_button)
        self.buttons.append(create_experiment_button)
        self.buttons.append(submit_button)

    def load_config_lang(self):
        self.language_config.read_language_config()
        language = self.language_config.get_language()
        if len(language) > 0:
            self.translateService.set_language(language)
            self.lang = language

    def change_language(self, lang):
        self.errors.clear()
        self.translateService.set_language(lang)
        self.language_config.update_language_config(lang)

    def update_text(self):
        for key, box in self.input_boxes.items():
            box.update_text()
        for button in self.buttons:
            button.update_text()

    def handle_events(self):
        def get_input_index(step):
            custom_variables = self.teststarterConfig.load_custom_variables()
            index_to_key = {0: 'participantId', 1: 'experiment', 2: 'startTime'}
            key_to_index = {'participantId': 0, 'experiment': 1, 'startTime': 2}
            count = 3
            for value in custom_variables:
                index_to_key[count] = value
                key_to_index[value] = count
                count += 1
            index = 0
            for key, input_box in self.input_boxes.items():
                if input_box.is_selected:
                    self.input_boxes[key].is_selected = False
                    index = key_to_index[key] + step
                    break
            if 0 <= index < len(self.input_boxes):
                return index_to_key[index]
            elif index < 0:
                return index_to_key[len(self.input_boxes) - 1]
            else:
                return index_to_key[0]

        for event in pygame.event.get():
            for key, box in self.input_boxes.items():
                box.handle_event(event)
            for button in self.buttons:
                button.handle_event(event)
            if event.type == KEYDOWN:
                mods = pygame.key.get_mods()
                if mods != 4160 and event.key == K_TAB:
                    index = get_input_index(1)
                    self.input_boxes[index].is_selected = True
                elif mods & mods == 4160:  # Check if Ctrl is pressed
                    if event.key == K_TAB:
                        index = get_input_index(-1)
                        self.input_boxes[index].is_selected = True
                elif event.key == K_BACKSPACE:
                    pass
                elif event.key == K_RETURN:
                    if self.buttons[3].is_active:
                        self.save_details()
            else:
                if len(self.input_boxes.get('startTime').text) == 1 and self.input_boxes.get(
                        'startTime').text.isnumeric() and 2 < int(self.input_boxes.get('startTime').text) < 10:
                    self.input_boxes.get('startTime').text = '0' + self.input_boxes.get('startTime').text
                if len(self.input_boxes.get('startTime').text) == 2 and self.input_boxes.get(
                        'startTime').text[1].isnumeric() and int(self.input_boxes.get(
                        'startTime').text) > 23:
                    self.input_boxes.get('startTime').text = self.input_boxes.get('startTime').text[0]
                if len(self.input_boxes.get('startTime').text) == 3:
                    if self.input_boxes.get('startTime').text[2] != ":":
                        self.input_boxes.get('startTime').text = self.input_boxes.get('startTime').text[
                                                                 :2] + ':' + self.input_boxes.get('startTime').text[
                                                                             2:3]
                if len(self.input_boxes.get('startTime').text) > 5:
                    self.input_boxes.get('startTime').text = self.input_boxes.get('startTime').text[:5]
                if len(self.input_boxes.get('startTime').text) == 4:
                    if self.input_boxes.get('startTime').text[3].isnumeric() and int(
                            self.input_boxes.get('startTime').text[3]) >= 6:
                        self.input_boxes.get('startTime').text = self.input_boxes.get('startTime').text[
                                                                 :3] + '0' + self.input_boxes.get('startTime').text[
                                                                             3:4]
                self.input_boxes.get('startTime').text = re.sub("[^0-9:]", "",
                                                                    self.input_boxes.get('startTime').text)

    def clear_screen(self):
        self.screen.fill(self.background_color)

    def draw(self):
        def validate_inputs(experiments):
            is_id_valid = len(self.input_boxes['participantId'].text) != 0
            is_experiment_valid = self.input_boxes['experiment'].text in experiments
            is_start_time_valid = self.is_valid_time_format(self.input_boxes['startTime'].text)

            # Define validation checks and corresponding error messages
            index_to_key = {0: 'participantId', 1: 'experiment', 2: 'startTime'}

            custom_variables = self.teststarterConfig.load_custom_variables()
            count = 3
            for value in custom_variables:
                index_to_key[count] = value
                count += 1
            if self.input_boxes['participantId'].text and self.input_boxes['experiment'].text and self.input_boxes[
                'startTime'].text:
                validation_checks = [
                    (lambda text: len(text) != 0, 'idError'),
                    (lambda text: text in experiments, 'experimentError'),
                    (self.is_valid_time_format, 'startTimeError')
                ]

                for validation_check, error_key in validation_checks:
                    is_valid = validation_check(
                        self.input_boxes[index_to_key[validation_checks.index((validation_check, error_key))]].text)

                    error_translation = self.translateService.get_translation(error_key)
                    if not is_valid and error_translation not in self.errors:
                        self.errors.append(error_translation)
                    elif is_valid and error_translation in self.errors:
                        self.errors.remove(error_translation)

            if is_id_valid and is_experiment_valid and is_start_time_valid:
                return True
            else:
                return False

        y = self.height // 2 - 200
        x = self.width // 2

        font = pygame.font.Font(
            None, int(64)
        )  # Create font object for header
        text_surface = font.render(
            self.translateService.get_translation('teststarter'), True, self.primary_color
        )
        text_rect = text_surface.get_rect()
        self.screen.blit(text_surface, (x - text_rect.width // 2, y))

        for key, box in self.input_boxes.items():
            box.draw(self.screen)
        is_input_valid = validate_inputs(self.teststarterConfig.experiments)

        for button in self.buttons:
            button.draw(self.screen)

        if is_input_valid:
            self.buttons[3].set_active(True)
            self.buttons[3].set_color(self.button_color)
        else:
            self.buttons[3].set_active(False)
            self.buttons[3].set_color(self.inactive_button_color)

        if self.teststarterConfig.error_msg == '':
            for item in self.errors:
                if self.translateService.get_translation('experimentNotFound') in item:
                    self.errors.remove(item)
        else:
            is_in_errors = False
            for item in self.errors:
                if self.translateService.get_translation('experimentNotFound') in item:
                    is_in_errors = True
            if not is_in_errors:
                self.errors.append(self.translateService.get_translation('experimentNotFound'))

        if len(self.errors) > 0:
            font = pygame.font.Font(None, 24)
            x = self.width // 2
            y = self.height - font.get_linesize() - font.get_linesize() * len(self.errors)

            for error in self.errors:
                text_surface = font.render(error, True, pygame.Color('red'))
                self.screen.blit(text_surface, (x - text_surface.get_rect().width // 2, y))
                y += font.get_linesize()

    def exit(self):
        self.is_running = False

    def custom_sort(self, item):
        return datetime.strptime(item[1]['datetime'], '%d/%m/%Y %H:%M:%S')

    def start_experiment(self, start_time, participant_info, custom_variables):
        global schedule
        print(self.teststarterConfig.current_experiment)
        isHab = '_list' in self.teststarterConfig.current_experiment
        print(isHab)
        schedule = {}
        current_tasks = self.teststarterConfig.current_tasks
        if len(self.teststarterConfig.error_msg) > 0:
            return
        tasks = []
        types = {}
        values = {}
        times = []
        states = {}

        for task, details in current_tasks.items():
            tasks.append(task)
            times.append(details['time'])
            states[task] = details['state']
            types[task] = details['type'] if 'type' in details else ''
            values[task] = details['value'] if 'value' in details else ''

        for i, time_delta in enumerate(times):
            exp_variable = tasks[i]
            if time_delta:
                activation_time = start_time + timedelta(hours=int(time_delta.split(':')[0]),
                                                         minutes=int(time_delta.split(':')[1]))
                # schedule[exp_variable] = str(activation_time)
                schedule[exp_variable] = activation_time.strftime('%d/%m/%Y %H:%M:%S')
        edited_schedule = {}
        for key, value in schedule.items():
            edited_schedule.update(
                {key: {'datetime': value, 'state': states[key], 'type': types[key], 'value': values[key]}})

        schedule = dict(sorted(edited_schedule.items(), key=self.custom_sort))
        print('ee = ', edited_schedule)
        CreateScheduleDisplay(schedule, participant_info, Teststarter, custom_variables, isHab).display()
        self.input_boxes = {}

    def save_details(self):
        participant_id = self.input_boxes['participantId'].text
        experiment = self.input_boxes['experiment'].text
        start_time = self.input_boxes['startTime'].text

        start_time = datetime.combine(datetime.now().date(), datetime.strptime(start_time, '%H:%M').time())

        participant_info = {'participant_id': participant_id, 'experiment': experiment, 'start_time': start_time}

        custom_variables = self.teststarterConfig.load_custom_variables()

        variables = {}

        for value in custom_variables:
            participant_info[value] = self.input_boxes[value].text
            variables[value] = self.input_boxes[value].text

        self.teststarterConfig.load_experiment_tasks(experiment)
        self.start_experiment(start_time, participant_info, variables)


Teststarter()
