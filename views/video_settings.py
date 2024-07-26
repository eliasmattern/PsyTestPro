import re
from math import floor

import pygame

from app_types import Settings
from components import UnderlinedText, Button, InputBox
from events import LANGUAGE_EVENT
from services import TranslateService, LanguageConfiguration, PsyTestProConfig

THEMES = {
	'backgroundColor': {'darkmode': '#000000', 'lightmode': '#faf9f9'},
	'primaryColor': {'darkmode': '#C0C0C0', 'lightmode': '#000000'},
	'buttonColor': {'darkmode': '#C0C0C0', 'lightmode': '#0e1116'},
	'buttonTextColor': {'darkmode': '#000000', 'lightmode': '#faf9f9'},
	'successColor': {'darkmode': '#00B371', 'lightmode': '#00B371'},
	'dangerColor': {'darkmode': '#FF0000', 'lightmode': '#FF0000'},
	'warningColor': {'darkmode': '#F0E68C', 'lightmode': '#9B9B28'},
	'activeButtonColor': {'darkmode': '#DADDDC', 'lightmode': '#232B38'},
	'inactiveButtonColor': {'darkmode': '#646464', 'lightmode': '#646464'},
	'gridColor': {'darkmode': '#C0C0C0', 'lightmode': '#232B38'},
	'groupButtonColor': {'darkmode': '#087F8C', 'lightmode': '#087F8C'}
}


class VideoSettings:
	def __init__(self, screen: pygame.Surface, translate_service: TranslateService, old_settings: Settings):
		self.errors = []
		self.screen = screen
		self.translate_service = translate_service
		self.old_settings = old_settings
		self.psy_test_pro_config = PsyTestProConfig()
		self.font = pygame.font.Font(None, 34)
		self.small_font = pygame.font.Font(None, 20)
		self.texts = self.create_text()
		self.width_percentage, self.height_percentage = self.screen.get_width() / 100, self.screen.get_height() / 100
		self.buttons = self.create_buttons()
		self.colors = ['primaryColor', 'backgroundColor', 'buttonColor', 'buttonTextColor', 'activeButtonColor',
					   'inactiveButtonColor', 'groupButtonColor', 'successColor', 'dangerColor',
					   'warningColor', 'gridColor']
		self.inputs, self.edit_buttons, self.color_indicator_rects, chunk_size = self.create_inputs()
		self.split_inputs = self.split_dict(self.inputs, chunk_size)
		self.split_edit_buttons = self.split_dict(self.edit_buttons, chunk_size)
		self.split_color_indicator_rects = self.split_dict(self.color_indicator_rects, chunk_size)
		self.page = 0
		self.pagination_buttons = self.create_pagination()

	def draw(self):
		for text in self.texts:
			text.draw()
		for button in self.buttons + list(self.split_edit_buttons[self.page].values()) + self.pagination_buttons:
			button.draw(self.screen)
		for color, input_box in self.split_inputs[self.page].items():
			input_box.draw(self.screen)
			if self.is_hex_color_code(input_box.text):
				pygame.draw.rect(self.screen, pygame.Color(input_box.text),
								 self.split_color_indicator_rects[self.page][color])
				input_box.text_color = pygame.Color('#000000')
			else:
				input_box.text_color = (255, 0, 0)
				text = self.small_font.render('?', True, (255, 255, 255))
				text_rect = text.get_rect()
				text_rect.center = self.split_color_indicator_rects[self.page][color].center
				self.screen.blit(text, text_rect)
			pygame.draw.rect(self.screen, (255, 255, 255), self.split_color_indicator_rects[self.page][color], width=1)

		if len(self.split_inputs) > 1:
			page_text = self.font.render(f'{self.page + 1}/{len(self.split_inputs)}', True, (255, 255, 255))
			page_text_rect = page_text.get_rect()
			page_text_rect.center = (self.width_percentage * 50, self.height_percentage * 80 + 12.5)
			self.screen.blit(page_text, page_text_rect)

	def handle_event(self, event: pygame.event.Event):
		if event.type == LANGUAGE_EVENT:
			self.texts = self.create_text()
		for button in self.buttons + list(self.split_edit_buttons[self.page].values()) + self.pagination_buttons:
			button.handle_event(event)
		for input_box in self.split_inputs[self.page].values():
			input_box.handle_event(event)

	def create_text(self) -> list[UnderlinedText]:
		texts = []
		self.width_percentage, self.height_percentage = self.screen.get_width() / 100, self.screen.get_height() / 100

		color_theme_surface = self.font.render(self.translate_service.get_translation('colorThemes'), True,
											   (255, 255, 255))
		color_theme_rect = color_theme_surface.get_rect()
		color_theme_rect.topleft = (self.width_percentage * 23, self.height_percentage * 15)

		start_pos = self.width_percentage * 21, self.height_percentage * 16 + self.font.get_height()
		end_pos = self.width_percentage * 79, self.height_percentage * 16 + self.font.get_height()

		texts.append(
			UnderlinedText(self.screen, color_theme_surface, color_theme_rect, start_pos, end_pos,
						   color=(255, 255, 255)))

		colors_surface = self.font.render(self.translate_service.get_translation('colors'), True,
										  (255, 255, 255))
		colors_rect = colors_surface.get_rect()
		colors_rect.topleft = (self.width_percentage * 23, self.height_percentage * 29)

		start_pos = self.width_percentage * 21, self.height_percentage * 30 + self.font.get_height()
		end_pos = self.width_percentage * 79, self.height_percentage * 30 + self.font.get_height()
		texts.append(UnderlinedText(self.screen, colors_surface, colors_rect, start_pos, end_pos,
									color=(255, 255, 255)))

		return texts

	def create_buttons(self) -> list[Button]:
		buttons = []

		dark_mode_button = Button(self.width_percentage * 35, self.height_percentage * 20, self.width_percentage * 25,
								  40,
								  'darkMode',
								  lambda: self.change_theme(True),
								  self.translate_service, color=pygame.Color('#C0C0C0'),
								  text_color=pygame.Color('Black'),
								  active_button_color=pygame.Color('#ACACAC'))
		light_mode_button = Button(self.width_percentage * 65, self.height_percentage * 20, self.width_percentage * 25,
								   40,
								   'lightMode',
								   lambda: self.change_theme(False),
								   self.translate_service, color=pygame.Color('#C0C0C0'),
								   text_color=pygame.Color('Black'),
								   active_button_color=pygame.Color('#ACACAC'))

		buttons.append(dark_mode_button)
		buttons.append(light_mode_button)
		return buttons

	def create_inputs(self):
		color_indicator_rects = {}
		inputs = {}
		edit_buttons = {}
		max_height = self.height_percentage * 70
		padding = 0
		chunk_size = floor((max_height - (self.height_percentage * 37)) / 60) + 1
		for color in self.colors:
			input_box = InputBox(self.width_percentage * 50, self.height_percentage * 37 + padding,
								 self.width_percentage * 30, 40, color, self.translate_service, is_active=False,
								 initial_text=self.old_settings.get_color_value(color),
								 desc=self.translate_service.get_translation(color), color=pygame.Color('#C0C0C0'),
								 active_color=pygame.Color('#DADDDC'), text_color=pygame.Color('#000000'),
								 label_color=pygame.Color('#000000'), active_text_color=pygame.Color('#000000'),
								 inactive_color=pygame.Color('#646464'))
			color_indicator = pygame.Rect(self.width_percentage * 32, self.height_percentage * 37 + padding + 8,
										  25, 25)
			color_indicator_rects[color] = color_indicator
			inputs[color] = input_box
			edit_buttons[color] = Button(self.width_percentage * 70, self.height_percentage * 37 + padding,
										 100, 40, 'edit', lambda c=color: self.activate_input(c),
										 self.translate_service, color=pygame.Color('#C0C0C0'),
										 text_color=pygame.Color('Black'), active_button_color=pygame.Color('#ACACAC'))
			if padding + 60 + self.height_percentage * 35 > max_height:
				padding = 0
			else:
				padding += 60

		return inputs, edit_buttons, color_indicator_rects, chunk_size

	def save_data(self, settings: Settings):
		for color, input_box in self.inputs.items():
			settings.set_color_value(color, input_box.text)
		return settings

	def activate_input(self, color: str):
		self.inputs[color].set_active(True)
		self.edit_buttons[color].translation_key = 'reset'
		self.edit_buttons[color].update_text()
		self.edit_buttons[color].action = lambda: self.inputs[color].set_text(
			self.old_settings.get_color_value(color))

	def is_hex_color_code(self, code: str):
		hex_color_pattern = re.compile(r'^#([A-Fa-f0-9]{6})$')
		return bool(hex_color_pattern.match(code))

	def validate_settings(self):
		self.errors = []

		for input_box in self.split_inputs[self.page].values():
			if not self.is_hex_color_code(input_box.text):
				self.errors.append(f'{input_box.text} {self.translate_service.get_translation('invalidHex')}')

	def split_dict(self, input_dict: dict, chunk_size: int):
		dict_list = [{}]
		current_dict = 0

		for key, value in input_dict.items():
			dict_list[current_dict][key] = value
			if len(dict_list[current_dict]) >= chunk_size:
				dict_list.append({})
				current_dict += 1
		filtered_dict = list(filter(lambda lst: len(lst) > 0, dict_list))

		return filtered_dict

	def create_pagination(self):
		left_button = Button(self.width_percentage * 45, self.height_percentage * 80,
							 30, 30, '<', lambda: self.page_update(self.split_inputs, False),
							 border_radius=90, color=pygame.Color('#C0C0C0'), text_color=pygame.Color('Black'),
							 active_button_color=pygame.Color('#ACACAC'))
		right_button = Button(self.width_percentage * 55, self.height_percentage * 80,
							  30, 30, '>', lambda: self.page_update(self.split_inputs, True),
							  border_radius=90, color=pygame.Color('#C0C0C0'), text_color=pygame.Color('Black'),
							  active_button_color=pygame.Color('#ACACAC'))

		return [left_button, right_button]

	def page_update(self, split_list: list, increment: bool):
		if increment:
			self.page = (self.page + 1) % len(split_list)
		else:
			self.page = (
				(self.page - 1) if self.page > 0 else len(split_list) - 1
			)

	def change_theme(self, darkmode: bool):
		for color, input_box in self.inputs.items():
			input_box.text = THEMES[color]['darkmode' if darkmode else 'lightmode']
