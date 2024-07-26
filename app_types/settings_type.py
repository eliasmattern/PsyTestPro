import re

import pygame

from services import TranslateService


class Settings:
	def __init__(self, translate_service: TranslateService, settings):
		self.translate_service = translate_service
		self.errors = []
		self.__settings = settings
		self.__background_color = self.__settings.get('backgroundColor')
		self.__primary_color = self.__settings.get('primaryColor')
		self.__button_color = self.__settings.get('buttonColor')
		self.__button_text_color = self.__settings.get('buttonTextColor')
		self.__success_color = self.__settings.get('successColor')
		self.__danger_color = self.__settings.get('dangerColor')
		self.__warning_color = self.__settings.get('warningColor')
		self.__active_button_color = self.__settings.get('activeButtonColor')
		self.__inactive_button_color = self.__settings.get('inactiveButtonColor')
		self.__group_button_color = self.__settings.get('groupButtonColor')
		self.__grid_color = self.__settings.get('gridColor')
		self.__show_next_task = self.__settings.get('showNextTask')
		self.__show_play_task_button = self.__settings.get('showPlayTaskButton')
		self.__audio_path = self.__settings.get('audioPath')

	@property
	def background_color(self):
		return self.__background_color

	@property
	def primary_color(self):
		return self.__primary_color

	@property
	def button_color(self):
		return self.__button_color

	@property
	def button_text_color(self):
		return self.__button_text_color

	@property
	def success_color(self):
		return self.__success_color

	@property
	def danger_color(self):
		return self.__danger_color

	@property
	def warning_color(self):
		return self.__warning_color

	@property
	def active_button_color(self):
		return self.__active_button_color

	@property
	def inactive_button_color(self):
		return self.__inactive_button_color

	@property
	def group_button_color(self):
		return self.__group_button_color

	@property
	def grid_color(self):
		return self.__grid_color

	@property
	def show_next_task(self):
		return self.__show_next_task

	@property
	def show_play_task_button(self):
		return self.__show_play_task_button

	@property
	def audio_path(self):
		return self.__audio_path

	@background_color.setter
	def background_color(self, value):
		old_value = self.__background_color
		self.__background_color = value
		result = self.check_color_contrasts()
		if not result:
			self.__background_color = old_value

	@primary_color.setter
	def primary_color(self, value):
		old_value = self.__primary_color
		self.__primary_color = value
		result = self.check_color_contrasts()
		if not result:
			self.__primary_color = old_value

	@button_color.setter
	def button_color(self, value):
		old_value = self.__button_color
		self.__button_color = value
		result = self.check_color_contrasts()
		if not result:
			self.__button_color = old_value

	@button_text_color.setter
	def button_text_color(self, value):
		old_value = self.__button_text_color
		self.__button_text_color = value
		result = self.check_color_contrasts()
		if not result:
			self.__button_text_color = old_value

	@success_color.setter
	def success_color(self, value):
		old_value = self.__success_color
		self.__success_color = value
		result = self.check_color_contrasts()
		if not result:
			self.__success_color = old_value

	@danger_color.setter
	def danger_color(self, value):
		old_value = self.__danger_color
		self.__danger_color = value
		result = self.check_color_contrasts()
		if not result:
			self.__danger_color = old_value

	@warning_color.setter
	def warning_color(self, value):
		old_value = self.__warning_color
		self.__warning_color = value
		result = self.check_color_contrasts()
		if not result:
			self.__warning_color = old_value

	@active_button_color.setter
	def active_button_color(self, value):
		old_value = self.__active_button_color
		self.__active_button_color = value
		result = self.check_color_contrasts()
		if not result:
			self.__active_button_color = old_value

	@inactive_button_color.setter
	def inactive_button_color(self, value):
		old_value = self.__inactive_button_color
		self.__inactive_button_color = value
		result = self.check_color_contrasts()
		if not result:
			self.__inactive_button_color = old_value

	@group_button_color.setter
	def group_button_color(self, value):
		old_value = self.__group_button_color
		self.__group_button_color = value
		result = self.check_color_contrasts()
		if not result:
			self.__group_button_color = old_value

	@grid_color.setter
	def grid_color(self, value):
		old_value = self.__grid_color
		self.__grid_color = value
		result = self.check_color_contrasts()
		if not result:
			self.__grid_color = old_value

	@show_next_task.setter
	def show_next_task(self, value):
		self.__show_next_task = value

	@show_play_task_button.setter
	def show_play_task_button(self, value):
		self.__show_play_task_button = value

	@audio_path.setter
	def audio_path(self, value):
		self.__audio_path = value

	def rgb_contrast(self, rgb1, rgb2):
		return abs(rgb1[0] - rgb2[0]) + abs(rgb1[1] - rgb2[1]) + abs(rgb1[2] - rgb2[2])

	def check_color_contrasts(self):
		self.errors = []
		background_color = pygame.Color(self.__background_color)
		button_text_color = pygame.Color(self.__button_text_color)

		case_1_colors = {
			'primaryColor': self.__primary_color,
			'buttonColor': self.__button_color,
			'activeButtonColor': self.__active_button_color,
			'inactiveButtonColor': self.__inactive_button_color,
			'groupButtonColor': self.__group_button_color,
			'successColor': self.__success_color,
			'dangerColor': self.__danger_color,
			'warningColor': self.__warning_color,
			'gridColor': self.__grid_color
		}

		case_2_colors = {
			'buttonColor': self.__button_color,
			'activeButtonColor': self.__active_button_color,
			'groupButtonColor': self.__group_button_color,
			'inactiveButtonColor': self.__inactive_button_color
		}

		for key, color in case_1_colors.items():
			if self.rgb_contrast(background_color, pygame.Color(color)) < 60:
				self.errors.append(
					self.translate_service.get_translation(key) + " " + self.translate_service.get_translation(
						'contrastErrorMsg') + " " + self.translate_service.get_translation('backgroundColor'))

		# Check case 2
		for key, color in case_2_colors.items():
			if self.rgb_contrast(button_text_color, pygame.Color(color)) < 60:
				self.errors.append(
					self.translate_service.get_translation(key) + " " + self.translate_service.get_translation(
						'contrastErrorMsg') + " " + self.translate_service.get_translation('buttonTextColor'))

		if len(self.errors) > 0:
			return False
		return True

	def camel_to_snake(self, name: str):
		s1 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', name)
		return s1.lower()

	def get_color_value(self, color_name: str):
		snake_case_name = self.camel_to_snake(color_name)
		property_name = f'_{self.__class__.__name__}__{snake_case_name}'
		return getattr(self, property_name, None)

	def set_color_value(self, color_name: str, new_value: str):
		snake_case_name = self.camel_to_snake(color_name)
		property_name = f'_{self.__class__.__name__}__{snake_case_name}'
		setattr(self, property_name, new_value)

	def __eq__(self, other):
		if not isinstance(other, Settings):
			# don't attempt to compare against unrelated types
			return NotImplemented
		return (
				self.__background_color == other.__background_color and
				self.__primary_color == other.__primary_color and
				self.__button_color == other.__button_color and
				self.__button_text_color == other.__button_text_color and
				self.__success_color == other.__success_color and
				self.__danger_color == other.__danger_color and
				self.__warning_color == other.__warning_color and
				self.__active_button_color == other.__active_button_color and
				self.__inactive_button_color == other.__inactive_button_color and
				self.__group_button_color == other.__group_button_color and
				self.__grid_color == other.__grid_color and
				self.__show_next_task == other.__show_next_task and
				self.__show_play_task_button == other.__show_play_task_button and
				self.__audio_path == other.__audio_path
		)
