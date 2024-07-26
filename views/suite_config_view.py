import os
import sys
from datetime import datetime
from tkinter import filedialog

import pygame

from components import Button
from services import CSVToJSONConverter, JSONToCSVConverter, get_resource_path
from services import PsyTestProConfig
from services import TranslateService
from .manage_task_view import ManageTasksView
from .suite_create_view import CreateSuiteView
from .suite_delete_view import DeleteSuiteView
from .task_config_view import TaskConfig
from .variable_create_view import CreateVariablesView
from .variable_delete_view import DeleteVariableView


class SuiteConfig:
	def __init__(self, translate_service: TranslateService):
		self.info_text = ''
		self.translate_service = translate_service
		self.psy_test_pro_config = PsyTestProConfig()
		self.settings = self.psy_test_pro_config.get_settings()
		self.running = True
		self.config_button_running = True
		self.manage_tasks_view = ManageTasksView(translate_service)

	def back_to_psy_test_pro(self):
		self.running = False

	def back_to_config(self):
		self.config_button_running = False

	def back(self, psy_test_pro):
		self.display(psy_test_pro, self.translate_service)

	def import_config(self):
		try:
			if sys.platform == "darwin":
				filepath = filedialog.askopenfilename(initialdir=get_resource_path('./'),
													  title=self.translate_service.get_translation('selectFile'))
			else:
				filepath = filedialog.askopenfilename(
					initialdir=get_resource_path('./'),  # The initial directory (you can change this)
					title=self.translate_service.get_translation('selectFile'),
					filetypes=(('Excel files', '*.xlsx'), ('All files', '*.*'))  # Add more file types if needed
				)
			if filepath:
				converter = CSVToJSONConverter(filepath)
				converter.convert_to_json()
				self.info_text = 'importSuccessfully'
		except Exception as e:
			self.info_text = 'importFailed'
			print(f'An error occurred: {e}')

	def export_config(self):
		try:
			# Get current timestamp
			current_time = datetime.now()

			# Format the timestamp as yyyy-mm-ddThhmmss
			formatted_time = current_time.strftime('%Y-%m-%dT%H%M%S')

			# Usage
			file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.xlsx"),
																						 ("All files", "*.*")])
			if file_path:
				converter = JSONToCSVConverter(get_resource_path(file_path))
				converter.export_to_csv()
				self.info_text = 'exportSuccessfully'

		except Exception as e:
			self.info_text = 'exportFailed'
			print(f'An error occurred: {e}')

	def display(self, psy_test_pro, create_continously=False):
		self.info_text = ''
		# Open the pygame window at front of all windows open on screen
		os.environ['SDL_VIDEO_WINDOW_POS'] = '0,0'  # Set window position to top-left corner

		# Define colors
		black = pygame.Color(self.settings["backgroundColor"])
		light_grey = pygame.Color(self.settings["primaryColor"])

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

		# Calculate scaling factors for position and size adjustments (this is how we can make sure that the program adjusts to any screen it is executed on)
		width_scale_factor = screen_width / original_width

		# Creating a fullscreen display surface
		screen = pygame.display.get_surface()

		# Setting the window caption
		pygame.display.set_caption('Configure Suite')
		create_suite_config = CreateSuiteView(self.translate_service)
		delete_suite_config = DeleteSuiteView(self.translate_service)
		task_config = TaskConfig(self.translate_service)
		create_variables_config = CreateVariablesView(self.translate_service)
		delete_variables_config = DeleteVariableView(self.translate_service)

		buttons: list[Button] = []
		suite_buttons = []
		import_export_buttons = []
		var_buttons = []
		spacing = 60
		width, height = pygame.display.Info().current_w, pygame.display.Info().current_h

		x = width // 2
		y = height // 2 - 150

		create_suite_button = Button(
			x,
			y + spacing,
			400,
			40,
			'createSuite',
			lambda: create_suite_config.create_suite_config_display(
				psy_test_pro, create_continously
			),
			self.translate_service,
		)
		configure_suite_task_button = Button(
			x,
			y + spacing * 2,
			400,
			40,
			'manageTasksForSuite',
			lambda: task_config.add_task_config_display(psy_test_pro),
			self.translate_service,
		)

		delete_button = Button(
			x,
			y + spacing * 3,
			400,
			40,
			'deleteSuite',
			lambda: delete_suite_config.delete_suite_config_display(
				psy_test_pro
			),
			self.translate_service,
		)

		export_button = Button(
			x,
			y + spacing * 2,
			400,
			40,
			'exportExperiments',
			lambda: self.export_config(),
			self.translate_service,
		)

		import_task_button = Button(
			x,
			y + spacing * 3,
			400,
			40,
			'importTasks',
			lambda: task_config.add_task_config_display(psy_test_pro),
			self.translate_service,
		)

		import_button = Button(
			x,
			y + spacing,
			400,
			40,
			'importExperiments',
			lambda: self.import_config(),
			self.translate_service,
		)

		create_var_button = Button(
			x,
			y + spacing,
			400,
			40,
			'createVar',
			lambda: create_variables_config.display(psy_test_pro, self.translate_service),
			self.translate_service,
		)

		delete_var_button = Button(
			x,
			y + spacing * 2,
			400,
			40,
			'deleteVar',
			lambda: delete_variables_config.display(),
			self.translate_service,
		)

		back_to_config_button = Button(
			x,
			y + 60 + 3 * spacing,
			100,
			40,
			'back',
			self.back_to_config,
			self.translate_service,
		)

		suite_buttons.append(create_suite_button)
		suite_buttons.append(configure_suite_task_button)
		suite_buttons.append(delete_button)
		suite_buttons.append(back_to_config_button)
		import_export_buttons.append(import_button)
		import_export_buttons.append(export_button)
		import_export_buttons.append(import_task_button)
		import_export_buttons.append(back_to_config_button)
		var_buttons.append(create_var_button)
		var_buttons.append(delete_var_button)
		var_buttons.append(back_to_config_button)

		suite_config_button = Button(
			x,
			y + 60,
			400,
			40,
			'configureSuites',
			lambda: self.show_setting_buttons(screen, suite_buttons, 'configureSuites'),
			self.translate_service,
		)
		y += spacing

		task_config_button = Button(
			x,
			y + 60,
			400,
			40,
			'configureTasks',
			lambda: self.manage_tasks_view.display('globalTasks'),
			self.translate_service,
		)
		y += spacing
		variable_config_button = Button(
			x,
			y + 60,
			400,
			40,
			'configureVariable',
			lambda: self.show_setting_buttons(screen, var_buttons, 'configureVariable'),
			self.translate_service,
		)
		y += spacing
		import_export_config_button = Button(
			x,
			y + 60,
			400,
			40,
			'importExport',
			lambda: self.show_setting_buttons(screen, import_export_buttons, 'importExport'),
			self.translate_service,
		)

		y += spacing
		back_button = Button(
			x,
			y + 60,
			100,
			40,
			'back',
			lambda: self.back_to_psy_test_pro(),
			self.translate_service,
		)
		buttons.append(suite_config_button)
		buttons.append(variable_config_button)
		buttons.append(import_export_config_button)
		buttons.append(task_config_button)
		buttons.append(back_button)

		while self.running:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()
				for button in buttons:
					button.handle_event(event)
			screen.fill(black)  # Fill the screen with the black color

			for button in buttons:
				button.draw(screen)

			font = pygame.font.Font(
				None, int(30 * width_scale_factor)
			)  # Create font object for header
			text_surface = font.render(
				self.translate_service.get_translation('configureTestBattery'), True, light_grey
			)  # Render the text 'Task' with the font and color light_grey
			text_rect = text_surface.get_rect()
			screen.blit(text_surface, (x - text_rect.width // 2, height // 2 - 150))

			font = pygame.font.Font(
				None, int(18 * width_scale_factor)
			)

			info_surface = font.render(
				self.translate_service.get_translation(self.info_text), True, light_grey
			)  # Render the text 'Task' with the font and color light_grey
			info_rect = text_surface.get_rect()
			screen.blit(info_surface, (x - info_rect.width // 2, screen_height - 90))

			pygame.display.flip()  # Flip the display to update the screen

		self.running = True

	def show_setting_buttons(self, screen: pygame.Surface, buttons: list[Button], label: str):
		black = pygame.Color(self.settings["backgroundColor"])
		light_grey = pygame.Color(self.settings["primaryColor"])

		# Get the screen width and height from the current device in use
		screen_info = pygame.display.Info()
		# Store the screen width in a new variable
		screen_width = screen_info.current_w
		# Store the screen height in a new variable
		screen_height = screen_info.current_h

		# Store the original screen dimensions used to design this program
		original_width = 1280

		# Calculate scaling factors for position and size adjustments (this is how we can make sure that the program adjusts to any screen it is executed on)
		width_scale_factor = screen_width / original_width

		width, height = pygame.display.get_surface().get_rect().size

		x = width // 2
		y = height // 3

		while self.config_button_running:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()
				for button in buttons:
					button.handle_event(event)
			screen.fill(black)  # Fill the screen with the black color

			for button in buttons:
				button.draw(screen)

			font = pygame.font.Font(
				None, int(30 * width_scale_factor)
			)  # Create font object for header
			text_surface = font.render(
				self.translate_service.get_translation(label), True, light_grey
			)  # Render the text 'Task' with the font and color light_grey
			text_rect = text_surface.get_rect()
			screen.blit(text_surface, (x - text_rect.width // 2, y))

			font = pygame.font.Font(
				None, int(18 * width_scale_factor)
			)

			info_surface = font.render(
				self.translate_service.get_translation(self.info_text), True, light_grey
			)  # Render the text 'Task' with the font and color light_grey
			info_rect = text_surface.get_rect()
			screen.blit(info_surface, (x - info_rect.width // 2, screen_height - 90))

			pygame.display.flip()  # Flip the display to update the screen
		self.config_button_running = True
