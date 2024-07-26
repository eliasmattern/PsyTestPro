import sys
from typing import Union

import pygame

from app_types import Task, TaskGroup
from components import Button, InputBox, QuestionDialog
from services import PsyTestProConfig, TranslateService


class AddExistingTaskView:
	def __init__(self, translate_service: TranslateService):
		self.screen = pygame.display.get_surface()
		self.translate_service = translate_service
		self.is_running = True
		self.psy_test_pro_config = PsyTestProConfig()
		self.settings = self.psy_test_pro_config.get_settings()
		self.primary_color = pygame.Color(self.settings["primaryColor"])
		self.background_color = pygame.Color(self.settings["backgroundColor"])
		self.group_button_color = pygame.Color(self.settings["groupButtonColor"])
		self.tasks: list[list[Task]] = []
		self.buttons: dict[str, Button] = {}
		self.refresh = False
		self.suite = ''
		self.page = 0
		self.font = pygame.font.Font(None, 24)
		self.title_font = pygame.font.Font(None, 30)
		self.task_length = 0
		self.title = ''
		self.formatted_suite_name = ''
		self.current_task: Union[Task, TaskGroup, None] = None
		self.add_dialog = QuestionDialog(500, 200, 'addTask', 'addTaskMsg', '', self.translate_service,
										 lambda: self.add_task(), action_key='add')
		self.add_dialog.is_open = False
		self.search_input = InputBox(self.screen.get_width() / 2, 50, 500, 40, 'search', self.translate_service,
									 icon=False)

	def display(self, suite_name: str):
		self.suite = suite_name
		self.title = self.translate_service.get_translation('addTaskFor') + self.formatted_suite_name
		tasks: list[Task] = self.psy_test_pro_config.load_task_of_suite('globalTasks')
		self.task_length = len(tasks)
		if len(self.search_input.text) > 0:
			tasks = self.search_tasks(tasks, self.search_input.text)
		current_tasks = list(self.split_list(tasks, 32))
		self.tasks = current_tasks
		self.create_buttons()
		while self.is_running:
			if self.refresh:
				self.refresh = False
				tasks = self.psy_test_pro_config.load_task_of_suite('globalTasks')
				if len(self.search_input.text) > 0:
					tasks = self.search_tasks(tasks, self.search_input.text)
				self.task_length = len(tasks)
				current_tasks = list(self.split_list(tasks, 32))
				self.tasks = current_tasks
				self.create_buttons()
			self.draw()
			self.handle_events()
		self.is_running = True

	def draw(self):
		self.screen.fill(self.background_color)
		for button in self.buttons.values():
			button.draw(self.screen)
		if len(self.tasks) > 1:
			page_text = f'{self.page + 1}/{len(self.tasks)}'
			page_surface = self.font.render(page_text, True, self.primary_color)
			page_rect = page_surface.get_rect()
			page_rect.center = (self.screen.get_width() / 2, self.screen.get_height() / 8 + 8 * 80 + 12.5)
			self.screen.blit(page_surface, page_rect)

		title_surface = self.title_font.render(self.title, True, self.primary_color)
		title_rect = title_surface.get_rect()
		title_rect.center = (
			self.screen.get_width() / 2, self.screen.get_height() / 6 - (self.title_font.get_height() * 2))

		self.screen.blit(title_surface, title_rect)

		self.search_input.draw(self.screen)

		if self.add_dialog.is_open:
			self.add_dialog.draw(self.screen)

		pygame.display.flip()

	def handle_events(self):
		search_term = self.search_input.text
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()
			if self.add_dialog.is_open:
				self.add_dialog.handle_events(event)
			else:
				self.search_input.handle_event(event)
				for button in self.buttons.values():
					button.handle_event(event)

		if search_term != self.search_input.text:
			self.refresh = True

	def create_buttons(self):
		self.buttons: dict[str, Button] = {}
		x = self.screen.get_width() / 5
		y = self.screen.get_height() / 6
		row_spacing = 80
		column_spacing = (self.screen.get_width() - self.screen.get_width() / 5) / 4
		row, column = 0, 0
		if not len(self.tasks) == 0:
			for task in self.tasks[self.page]:
				task_x, task_y = x + column * column_spacing, y + row * row_spacing
				button_color = self.primary_color if isinstance(task, Task) else self.group_button_color
				active_color = pygame.Color(min(button_color.r + 10, 255), min(button_color.g + 10, 255),
											min(button_color.b + 10, 255)) if isinstance(task, TaskGroup) else None
				button = Button(
					task_x,
					task_y,
					250,
					40,
					task.name,
					lambda t=task: self.set_current_task(t),
					color=button_color,
					active_button_color=active_color
				)

				self.buttons[task.id + str(row)] = button

				if row < 7:
					row += 1
				else:
					column += 1
					row = 0
		left_button = Button(
			self.screen.get_width() / 2 - 50,
			y + 8 * row_spacing,
			25,
			25,
			'<',
			lambda: self.page_update(False, self.tasks),
			border_radius=90
		)
		right_button = Button(
			self.screen.get_width() / 2 + 50,
			y + 8 * row_spacing,
			25,
			25,
			'>',
			lambda: self.page_update(True, self.tasks),
			border_radius=90
		)
		back_button = Button(
			self.screen.get_width() / 2,
			self.screen.get_height() - 50,
			150,
			40,
			'back',
			self.back,
			self.translate_service
		)

		self.buttons['back_button'] = back_button
		if len(self.tasks) > 1:
			self.buttons['left_button'] = left_button
			self.buttons['right_button'] = right_button

	def back(self):
		self.is_running = False

	def split_list(self, input_list: list, chunk_size: int):
		for i in range(0, len(input_list), chunk_size):
			yield input_list[i:i + chunk_size]

	def page_update(self, increment: bool, splitted_tasks: list):
		if increment:
			self.page = (self.page + 1) % len(splitted_tasks)
		else:
			self.page = (self.page - 1) if self.page > 0 else len(splitted_tasks) - 1
		self.refresh = True

	def add_task(self):
		if isinstance(self.current_task, Task):
			name, time, task_type, value = (
				self.current_task.name, self.current_task.duration, self.current_task.task_type,
				self.current_task.value)

			self.psy_test_pro_config.save_task(self.suite, name, time, task_type, value, None)
		elif isinstance(self.current_task, TaskGroup):
			group_name, loops, pause, group_tasks = (
				self.current_task.name, self.current_task.loops, self.current_task.pause_inbetween,
				self.current_task.tasks)
			self.psy_test_pro_config.create_group(self.suite, group_name, loops, str(pause), group_tasks)

	def set_current_task(self, task: Union[Task, TaskGroup]):
		self.current_task = task
		self.add_dialog.open()

	def search_tasks(self, tasks: list[Task], search_input: str) -> list[Task]:
		search_query = search_input.lower()
		return [task for task in tasks if search_query in task.name.lower()]
