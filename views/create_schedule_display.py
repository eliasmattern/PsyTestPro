import os
import re
import sys
import time as pythonTime
import webbrowser
from datetime import datetime, timedelta

import pygame

from app_types import Task
from components import Button, DataTable, QuestionDialog, DatePickerComponent, TimePicker
from events import LANGUAGE_EVENT
from services import PsyTestProConfig, get_resource_path
from services import TranslateService, LanguageConfiguration, play_tasks


class CreateScheduleDisplay:
	def __init__(self, schedule: list[Task], participant_info: dict, psy_test_pro, custom_variables: dict,
				 isHab: bool = False, file_name: str = ''):
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
		self.show_task = self.settings["showNextTask"]
		self.show_play_next_task = self.settings["showPlayTaskButton"]
		self.todo_input_values = {}
		self.newdate_input_values = {}
		self.newtime_input_values = {}
		self.show_help_dialog = False
		self.show_quit_dialog = False
		self.show_date_picker = False
		self.show_time_picker = False
		# Get the screen width and height from the current device in use
		screen_info = pygame.display.Info()
		# Store the screen width in a new variable
		self.screen_width = screen_info.current_w
		# Store the screen height in a new variable
		self.screen_height = screen_info.current_h
		self.column_width = None
		self.splitted_schedule: list[list[Task]] = list(self.split_list(self.schedule, 15))
		self.headers = ['task', 'date', 'time', 'state']

		self.date_picker = None
		self.timepicker = None

		self.actions = [None,
						self.open_date_picker,
						self.open_timepicker,
						self.switch_state]
		self.play_next_task = False

		if self.isHab:
			self.headers = ['task', 'state']
			self.actions = [None, self.switch_state]
		self.data_table = DataTable(self.headers,
									(self.screen_width - (len(self.headers) + 0.5) * 150, self.screen_height / 15), 150,
									self.get_table_data(), self.actions, self.screen_height / 15 * 13,
									self.translate_service)

	def display(self):
		# Open the pygame window at front of all windows open on screen
		os.environ['SDL_VIDEO_WINDOW_POS'] = '0,0'  # Set window position to top-left corner

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

		buttons: list[Button] = []

		# Create buttons
		run_button = Button(150 * width_scale_factor, 100 * height_scale_factor, 200 * width_scale_factor,
							50 * height_scale_factor, 'runTestBattery', self.run_psy_test_pro, self.translate_service)
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
											   lambda: self.data_table.update_field((
												   '/'.join([str(self.date_picker.day), str(self.date_picker.month),
															 str(self.date_picker.year)])))
											   , action_key='save')
		self.timepicker = TimePicker(300, 200, 'timepicker', self.translate_service, time='12:34:21',
									 action=lambda: self.data_table.update_field(
										 str(self.timepicker.time)), action_key='save')

		while True:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()
				elif event.type == LANGUAGE_EVENT:
					help_dialog.handle_events(event)
					self.date_picker.handle_events(event)
					self.timepicker.handle_events(event)
					quit_dialog.handle_events(event)

				if self.show_help_dialog:
					help_dialog.handle_events(event)
				elif self.show_date_picker:
					self.date_picker.handle_events(event)
				elif self.show_time_picker:
					self.timepicker.handle_events(event)
				elif self.show_quit_dialog:
					quit_dialog.handle_events(event)
				else:
					for button in buttons:
						button.handle_event(event)

					self.data_table.handle_event(event)

			screen.fill(self.black)  # Fill the screen with the black color
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

			if self.show_time_picker:
				self.timepicker.draw(screen)
			if not self.timepicker.is_open:
				self.show_time_picker = False
				self.timepicker.is_open = True

			pygame.display.flip()  # Flip the display to update the screen

	def text_objects(self, text: str, font: pygame.font.Font):
		text_surface = font.render(text, True, self.button_text_color)
		return text_surface, text_surface.get_rect()

	def run_psy_test_pro(self):
		self.save_data(self.data_table.get_data())
		# set the display mode to fullscreen
		screen = pygame.display.get_surface()

		# Setting the window caption
		pygame.display.set_caption('PsyTestPro running')

		# set the color of the screen to black
		screen.fill(self.black)
		filtered_schedule: list[Task] = [task for task in self.schedule if task.state == 'todo']
		# convert the schedule to a list of tuples and sort it by time
		sorted_schedule = sorted(filtered_schedule, key=lambda task: (task.duration, task.position))
		sorted_schedule = [(datetime.strptime(task.duration, '%d/%m/%Y %H:%M:%S'), task) for task in
						   sorted_schedule]
		past_todo_tasks = [task for task in self.schedule if
						   task.state == 'todo' and datetime.strptime(task.duration,
																	  '%d/%m/%Y %H:%M:%S') < datetime.now()]
		for task in past_todo_tasks:
			state = play_tasks(self.file_name, self.participant_info, task, self.schedule,
							   self.translate_service,
							   self.custom_variables)
			pygame.mouse.set_visible(True)
			if state:
				task.state = 'done'
			else:
				task.state = 'error'

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
			audio_path = get_resource_path(
				self.settings['audioPath'] if self.settings['audioPath'].startswith('.') else self.settings[
					'audioPath'], )

			if check_for_old_tasks:
				filtered_list = [
					task for task in self.schedule
					if task.state == 'todo' and start_time < datetime.strptime(task.duration,
																			   '%d/%m/%Y %H:%M:%S') < datetime.now()
				]
				for item in filtered_list:
					upcoming_event = item
					try:
						beep_sound = pygame.mixer.Sound(audio_path)
						beep_sound.play()
					except Exception as e:
						print(e)

					state = play_tasks(self.file_name, self.participant_info, upcoming_event, self.schedule,
									   self.translate_service,
									   self.custom_variables)
					pygame.mouse.set_visible(True)
					if state:
						upcoming_event.state = 'done'
					else:
						upcoming_event.state = 'error'
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
			if next_event and self.show_play_next_task:
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
					if self.show_task:
						event_message = ' ' + self.translate_service.get_translation('until') + f' {next_event[1].name}'
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
				try:
					beep_sound = pygame.mixer.Sound(audio_path)
					beep_sound.play()
				except Exception as e:
					print(e)
				state = play_tasks(self.file_name, self.participant_info, upcoming_event, self.schedule,
								   self.translate_service,
								   self.custom_variables)
				pygame.mouse.set_visible(True)
				if state:
					upcoming_event.state = 'done'
				else:
					upcoming_event.state = 'error'
				sorted_schedule = [(dt, desc) for dt, desc in sorted_schedule if desc != upcoming_event]
				self.play_next_task = False

			if not self.isHab or next_event_in_seconds == -1:
				if round(next_event_in_seconds) == 1:
					check_for_old_tasks = True
					upcoming_event = next_event[1]
					pythonTime.sleep(1.1)
					try:
						beep_sound = pygame.mixer.Sound(audio_path)
						beep_sound.play()
					except Exception as e:
						print(e)
					state = play_tasks(self.file_name, self.participant_info, upcoming_event, self.schedule,
									   self.translate_service,
									   self.custom_variables)
					pygame.mouse.set_visible(True)
					if state:
						upcoming_event.state = 'done'
					else:
						upcoming_event.state = 'error'
			elif len(sorted_schedule) > 0:
				filtered_schedule: list[Task] = [task for task in self.schedule if task.state == 'todo']
				sorted_schedule = sorted(filtered_schedule, key=lambda task: task.position)
				for task in sorted_schedule:
					if task.state == 'todo':
						state = play_tasks(self.file_name, self.participant_info, task, self.schedule,
										   self.translate_service,
										   self.custom_variables)
						if state:
							task.state = 'done'
						else:
							task.state = 'error'
				sorted_schedule = []

		pygame.quit()

	def is_valid_datetime_format(self, datetime_str: str):
		# This pattern strictly matches DD/MM/YYYY HH:MM:SS
		pattern = r'^\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}$'
		return re.match(pattern, datetime_str) is not None

	def change_settings(self):
		self.schedule_page = 0

		time = str(self.participant_info['start_time']).split(' ')[1]
		splittedTime = time.split(':')
		formattedTime = splittedTime[0] + ':' + splittedTime[1]
		self.psy_test_pro(self.participant_info['participant_id'], self.participant_info['suite'], formattedTime,
						  self.custom_variables)

	def change_language(self, translateService: TranslateService, language_config: LanguageConfiguration, lang: str):
		translateService.set_language(lang)
		language_config.update_language_config(lang)

	def quit_psy_test_pro(self):
		self.show_quit_dialog = True

	def quit_action(self):
		pygame.quit()
		sys.exit()

	def button_help(self):
		self.show_help_dialog = True

	def help_action(self):
		webbrowser.open('https://github.com/eliasmattern/PsyTestPro')

	def split_list(self, input_list: list, chunk_size: int):
		for i in range(0, len(input_list), chunk_size):
			yield input_list[i:i + chunk_size]

	def open_date_picker(self, date: str):
		self.show_date_picker = True
		self.date_picker.day, self.date_picker.month, self.date_picker.year = date.split('/')
		self.date_picker.create_calendar(int(self.date_picker.year), int(self.date_picker.month),
										 int(self.date_picker.day))

	def open_timepicker(self, time: str):
		self.show_time_picker = True
		self.timepicker.set_time(time)

	def switch_state(self, state: dict):
		state_iterator = {'todo': {'value': 'skip', 'color': self.warning, 'key': 'skip'},
						  'skip': {'value': 'done', 'color': self.success, 'key': 'done'},
						  'done': {'value': 'todo', 'color': self.light_grey, 'key': 'todo'},
						  'error': {'value': 'todo', 'color': self.light_grey, 'key': 'todo'}}
		self.data_table.update_field(state_iterator[state['value']])

	def save_data(self, data: list):
		for task, new_task in zip(self.schedule, data):
			if not self.isHab:
				task.duration = new_task[1] + ' ' + new_task[2]
				task.state = new_task[3]['value']
			else:
				task.state = new_task[1]['value']

	def get_table_data(self):
		states = {'todo': {'value': 'todo', 'color': self.light_grey, 'key': 'todo'},
				  'skip': {'value': 'skip', 'color': self.warning, 'key': 'skip'},
				  'done': {'value': 'done', 'color': self.success, 'key': 'done'},
				  'error': {'value': 'error', 'color': self.red, 'key': 'error'}}
		data = []
		for task in self.schedule:
			date, time = task.duration.split(' ')
			if self.isHab:
				data.append(
					[task.name, {'value': task.state, 'color': states[task.state]['color'],
								 'key': states[task.state]['key']}])
			else:
				data.append(
					[task.name, date, time,
					 {'value': task.state, 'color': states[task.state]['color'],
					  'key': states[task.state]['key']}])
		return data

	def edit_schedule(self):
		self.play_next_task = False
		self.data_table.set_data(self.get_table_data())
		self.display()

	def play_task(self):
		self.play_next_task = True
