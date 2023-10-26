# Add buttons to the left side of the screen

# Script updated to add input entry to relevant columns

import pygame
import sys
from pygame.locals import *
import csv
from datetime import datetime, timedelta
from classes import InputBox, Button
from functions import create_schedule_display, experiment_config_display
from ctypes import windll
import re
from services import TranslateService, LanguageConfiguration, TeststarterConfig

class Teststarter:
    def __init__(self, id="", experiment = "", time_of_day = "", week_number = "", time = ""):
        pygame.init()
        self.width, self.height = pygame.display.Info().current_w, pygame.display.Info().current_h
        self.screen = pygame.display.set_mode((self.width, self.height), FULLSCREEN)
        pygame.display.set_caption("Teststarter")
        pygame.scrap.init()
        self.teststarterConfig = TeststarterConfig()
        self.teststarterConfig.load_experiments()
        self.lang = "en"
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 24)
        self.input_boxes = []
        self.buttons = []
        self.errors = []
        self.language_config = LanguageConfiguration()
        self.translateService = TranslateService(self.language_config)
        self.lang = self.load_config_lang()
        self.id = id
        self.experiment = experiment
        self.time_of_day = time_of_day
        self.week_number = week_number
        self.time = time
        self.create_input_boxes()
        self.is_running = True
        self.start_time = None

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
        pattern = r"^(?:[01]\d|2[0-3]):[0-5]\d$"
        return re.match(pattern, datetime_str) is not None

    def create_input_boxes(self):
        labels = ["participantId", "experiment", "timeOfDay", "weekNumber", "startTime"]
        experiments_string = ""
        for experiment in self.teststarterConfig.experiments:
            experiments_string = experiments_string + experiment + ", "
        if "," in experiments_string:
            experiments_string = experiments_string[:-2]
        inforomation = ["", "(" + experiments_string + ")", "", "", ""]
        initial_text = [self.id, self.experiment, self.time_of_day, self.week_number, self.time]
        x = self.width // 2
        y = self.height // 2 - 100
        spacing = 60
        for label, text, info in zip(labels, initial_text, inforomation):
            input_box = InputBox(x, y, 400, 40, label, self.translateService, info, text)
            self.input_boxes.append(input_box)
            y += spacing

        exit_button = Button(x - 75, y + 60, 100, 40, "exit", self.exit, self.translateService)
        submit_button = Button(x + 75, y + 60, 100, 40, "submit", self.save_details, self.translateService)
        english_button = Button(self.width-250, 100, 100, 40, "english", lambda: self.change_language("en"), self.translateService)
        german_button = Button(self.width-100, 100, 100, 40, "german", lambda: self.change_language("de"), self.translateService)
        create_experiment_button = Button(self.width-175, 150, 250, 40, "configureExperiment", lambda: experiment_config_display(Teststarter, self.translateService), self.translateService)

        self.buttons.append(english_button)
        self.buttons.append(german_button)
        self.buttons.append(exit_button)
        self.buttons.append(submit_button)
        self.buttons.append(create_experiment_button)
    
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
        for box in self.input_boxes:
            box.update_text()
        for button in self.buttons:
            button.update_text()

    def handle_events(self):
        def get_input_index():
            index = 0 
            for input_box in self.input_boxes:
                index += 1
                if input_box.is_selected:
                    self.input_boxes[index -1].is_selected = False
                    break
            if index < len(self.input_boxes):
                return index
            else:
                return 0
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_TAB:
                    index = get_input_index()
                    self.input_boxes[index].is_selected = True
            for box in self.input_boxes:
                box.handle_event(event)
            for button in self.buttons:
                button.handle_event(event)


    def clear_screen(self):
        self.screen.fill((0, 0, 0))

    
    def draw(self):
        def validate_inputs(experiments):
            is_id_valid = len(self.input_boxes[0].text) != 0
            is_experiment_valid = self.input_boxes[1].text in experiments
            is_time_of_day_valid = self.input_boxes[2].text == "morn" or self.input_boxes[2].text == "eve" or self.input_boxes[2].text == "full"
            is_week_no_valid = self.input_boxes[3].text.isnumeric()
            is_start_time_valid = self.is_valid_time_format(self.input_boxes[4].text)

            # Define validation checks and corresponding error messages

            if self.input_boxes[0].text and self.input_boxes[1].text and self.input_boxes[2].text and self.input_boxes[3].text and self.input_boxes[4].text:
                validation_checks = [
                    (lambda text: len(text) != 0, "idError"),
                    (lambda text: text in experiments, "experimentError"),
                    (lambda text: text in ["morn", "eve", "full"], "timeOfDayError"),
                    (lambda text: text.isnumeric(), "weekNoError"),
                    (self.is_valid_time_format, "startTimeError")
                ]

                for validation_check, error_key in validation_checks:
                    is_valid = validation_check(self.input_boxes[validation_checks.index((validation_check, error_key))].text)

                    error_translation = self.translateService.get_translation(error_key)
                    if not is_valid and error_translation not in self.errors:
                        self.errors.append(error_translation)
                    elif is_valid and error_translation in self.errors:
                        self.errors.remove(error_translation)

            if is_id_valid and is_experiment_valid and is_time_of_day_valid and is_week_no_valid and is_start_time_valid:
                return True
            else:
                return False
            
        for box in self.input_boxes:
            box.draw(self.screen)
        is_input_valid = validate_inputs(self.teststarterConfig.experiments)

        for button in self.buttons:
            button.draw(self.screen)

        if is_input_valid:
            self.buttons[3].set_active(True)
            self.buttons[3].set_color("gray")
        else:
            self.buttons[3].set_active(False)
            self.buttons[3].set_color((100, 100, 100))
        
        if self.teststarterConfig.error_msg == "":
            for item in self.errors:
                if self.translateService.get_translation("experimentNotFound") in item:
                    self.errors.remove(item)
        else:
            is_in_errors = False
            for item in self.errors:
                if self.translateService.get_translation("experimentNotFound") in item:
                    is_in_errors = True
            if not is_in_errors:
                self.errors.append(self.translateService.get_translation("experimentNotFound"))


        if len(self.errors) > 0:
            error_msg = ""

            for error in self.errors:
                error_msg = error_msg + error
            x = self.width // 2
            y = self.height // 2
            font = pygame.font.Font(None, 24) 
            text_surface = font.render(' ' + error_msg, True, pygame.Color("gray")) 
            self.screen.blit(text_surface, (x-150, y + 400)) 
        
        
   
    def exit(self):
        self.is_running = False

    def custom_sort(self, item):
        return datetime.strptime(item[1]['datetime'], '%d/%m/%Y %H:%M:%S')
        
    def start_experiment(self, start_time, participant_info):
        global schedule
        isHab = self.teststarterConfig.current_experiment == "hab"
        schedule = {}
        current_tasks = self.teststarterConfig.current_tasks
        print(self.teststarterConfig.error_msg)
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
            types[task] = details['type'] if 'type' in details else ""
            values[task] = details['value'] if 'value' in details else ""

        for i, time_delta in enumerate(times):
            exp_variable = tasks[i]
            if time_delta:
                activation_time = start_time + timedelta(hours=int(time_delta.split(':')[0]), minutes=int(time_delta.split(':')[1]))
                #schedule[exp_variable] = str(activation_time)
                schedule[exp_variable] = activation_time.strftime('%d/%m/%Y %H:%M:%S')
        edited_schedule = {}
        for key, value in schedule.items():
            edited_schedule.update({key: {"datetime": value, "state": states[key], "type": types[key], "value": values[key]}})
        schedule = dict(sorted(edited_schedule.items(), key=self.custom_sort))
        print("ee = ", edited_schedule)
        create_schedule_display(schedule, participant_info, Teststarter)
        self.input_boxes = []

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
    
        self.teststarterConfig.load_experiment_tasks(experiment, time_of_day)
        self.start_experiment(start_time, participant_info)
       



Teststarter()
