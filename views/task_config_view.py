import sys
import pygame
from components import Button
from services import PsyTestProConfig
from .manage_task_view import ManageTasksView
from .task_create_view import AddTaskView
from services import TranslateService


class TaskConfig:
	def __init__(self, translate_service: TranslateService):
		self.running = True
		self.adding = True
		self.selected_multiple = False
		self.page = 0
		self.error = ''
		self.translate_service = translate_service
		self.add_task = AddTaskView(self.translate_service)
		self.psy_test_pro_config = PsyTestProConfig()
		self.settings = self.psy_test_pro_config.get_settings()
		self.manage_tasks_view = ManageTasksView(translate_service)

	def backToConfig(self):
		self.running = False

	def split_dict(self, input_list: list, chunk_size: int):
		for i in range(0, len(input_list), chunk_size):
			yield input_list[i:i + chunk_size]

	def page_update(self, increment: bool, splitted_suites: list):
		if increment:
			self.page = (self.page + 1) % len(splitted_suites)
		else:
			self.page = (
				(self.page - 1) if self.page > 0 else len(splitted_suites) - 1
			)

	def add_task_config_display(self, psy_test_pro):
		self.page = 0
		self.running = True

		psy_test_pro_config = PsyTestProConfig()
		# Define colors
		background_color = pygame.Color(self.settings["backgroundColor"])
		primary_color = pygame.Color(self.settings["primaryColor"])

		# Store the screen width in a new variable
		screen = pygame.display.get_surface()

		# Setting the window caption
		pygame.display.set_caption('Add task')

		suite_and_day_of_times = (
			psy_test_pro_config.get_suites()
		)
		splitted_suite = list(self.split_dict(suite_and_day_of_times, 5))

		while self.running:
			screen.fill(background_color)  # Fill the screen with the background_color color

			buttons: list[Button] = []

			spacing = 0
			width, height = (
				pygame.display.Info().current_w,
				pygame.display.Info().current_h,
			)

			x = width // 2
			y = height // 2 - 150
			if len(splitted_suite) > 0:
				for suite in splitted_suite[self.page]:
					exp_button = Button(
						x,
						y + 60 + spacing,
						400,
						40,
						suite.split('_')[0],
						lambda suite_name=suite: self.manage_tasks_view.display(suite_name)
					)
					buttons.append(exp_button)
					spacing += 60
			else:
				font = pygame.font.Font(None, int(24))  # Create font object for header
				text_surface = font.render(
					self.translate_service.get_translation('noExperiments'), True, primary_color
				)
				text_rect = text_surface.get_rect()
				screen.blit(text_surface, (x - text_rect.width // 2, y + 60 + spacing))
				spacing += 60

			spacing = len(splitted_suite[0]) * 60 if len(splitted_suite) > 0 else 60
			spacing += 60
			back_button = Button(
				x,
				y + spacing + 100,
				100,
				40,
				'back',
				lambda: self.backToConfig(),
				self.translate_service,
			)
			buttons.append(back_button)

			if len(splitted_suite) > 1:
				page_font = pygame.font.Font(None, int(24))
				page_text_surface = page_font.render(
					str(self.page + 1) + '/' + str(len(splitted_suite)),
					True,
					primary_color,
				)
				page_rect = page_text_surface.get_rect()
				screen.blit(
					page_text_surface,
					(x - page_rect.width // 2, y + 100 + spacing - 60),
				)
				previous_page_button = Button(
					x - 40,
					y + 100 + spacing - 60,
					25,
					25,
					'<',
					lambda: self.page_update(False, splitted_suite),
					border_radius=90
				)
				next_page_back_button = Button(
					x + 40,
					y + 100 + spacing - 60,
					25,
					25,
					'>',
					lambda: self.page_update(True, splitted_suite),
					border_radius=90
				)
				buttons.append(previous_page_button)
				buttons.append(next_page_back_button)

			# This invokes the function draw_button

			# Display column headers with adjusted font size
			width, height = (
				pygame.display.Info().current_w,
				pygame.display.Info().current_h,
			)
			x = width // 2
			y = height // 2 - 150
			font = pygame.font.Font(
				None, int(32)
			)  # Create font object for header
			text_surface = font.render(
				self.translate_service.get_translation('chooseSuiteToConfigureTask'), True, primary_color
			)  # Render the text 'Task' with the font and color primary_color
			text_rect = text_surface.get_rect()
			screen.blit(text_surface, (x - text_rect.width // 2, y))

			for button in buttons:
				button.draw(screen)

			pygame.display.flip()  # Flip the display to update the screen
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()
				for button in buttons:
					button.handle_event(event)
