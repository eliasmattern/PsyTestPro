# Add buttons to the left side of the screen

# Script updated to add input entry to relevant columns

import pygame
import sys
from pygame.locals import *
import csv
from datetime import datetime, timedelta
from classes import InputBox, Button
from functions import create_schedule_display
from ctypes import windll

class Teststarter:
    def __init__(self, id="", experiment = "", time_of_day = "", week_number = "", time = ""):
        pygame.init()
        self.width, self.height = pygame.display.Info().current_w, pygame.display.Info().current_h
        self.screen = pygame.display.set_mode((self.width, self.height), FULLSCREEN)
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
            create_schedule_display(schedule, participant_info, Teststarter, isHab)

        def experiment_evening(self, participant_info):
            global schedule
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
            create_schedule_display(schedule, participant_info, Teststarter)
            
        def sleep_extension_morning(self, participant_info):
            global schedule
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
            create_schedule_display(schedule, participant_info, Teststarter)
            
        def sleep_restriction_morning(self, participant_info):
            global schedule
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
            create_schedule_display(edited_schedule, participant_info, Teststarter)
            
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

        exit_button = Button(x - 75, y + 60, 100, 40, "Exit", self.exit)
        submit_button = Button(x + 75, y + 60, 100, 40, "Submit", self.save_details)
        self.input_boxes.append(exit_button)
        self.input_boxes.append(submit_button)
        
    
    def handle_events(self):
        def get_input_index():
            index = 0 
            for input_box in self.input_boxes[:-2]:
                index += 1
                if input_box.is_selected:
                    self.input_boxes[index -1].is_selected = False
                    break
            if index < len(self.input_boxes[:-2]):
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


    def clear_screen(self):
        self.screen.fill((0, 0, 0))

    def draw(self):
        for box in self.input_boxes:
            box.draw(self.screen)
    
    def exit(self):
        self.is_running = False

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


Teststarter()
