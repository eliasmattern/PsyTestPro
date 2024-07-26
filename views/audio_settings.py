import sys
from tkinter import filedialog

import pygame

from app_types import Settings
from components import UnderlinedText, Button
from events import LANGUAGE_EVENT
from services import TranslateService, PsyTestProConfig, get_resource_path


class AudioSettings:
	def __init__(self, screen: pygame.Surface, translate_service: TranslateService, old_settings: Settings):
		self.screen = screen
		self.translate_service = translate_service
		self.old_settings = old_settings
		self.psy_test_pro_config = PsyTestProConfig()
		self.font = pygame.font.Font(None, 34)
		self.texts = self.create_text()
		self.width_percentage, self.height_percentage = self.screen.get_width() / 100, self.screen.get_height() / 100
		self.button = self.create_button()
		self.button_desc = self.create_button_text()

	def draw(self):
		for text in self.texts:
			text.draw()
		self.button.draw(self.screen)

		self.screen.blit(self.button_desc[0], self.button_desc[1])

	def handle_event(self, event: pygame.event.Event):
		if event.type == LANGUAGE_EVENT:
			self.texts = self.create_text()
		self.button.handle_event(event)

	def create_text(self) -> list[UnderlinedText]:
		texts = []
		self.width_percentage, self.height_percentage = self.screen.get_width() / 100, self.screen.get_height() / 100

		audio_surface = self.font.render(self.translate_service.get_translation('audio'), True,
										 (255, 255, 255))
		audio_rect = audio_surface.get_rect()
		audio_rect.topleft = (self.width_percentage * 23, self.height_percentage * 15)

		start_pos = self.width_percentage * 21, self.height_percentage * 16 + self.font.get_height()
		end_pos = self.width_percentage * 79, self.height_percentage * 16 + self.font.get_height()

		texts.append(
			UnderlinedText(self.screen, audio_surface, audio_rect, start_pos, end_pos,
						   color=(255, 255, 255)))

		return texts

	def create_button(self):
		return Button(self.width_percentage * 62, self.height_percentage * 20, self.width_percentage * 34, 40,
					  self.old_settings.audio_path, lambda: self.choose_audio_file(), color=pygame.Color('#C0C0C0'),
					  text_color=pygame.Color('Black'), active_button_color=pygame.Color('#ACACAC'))

	def choose_audio_file(self):
		try:
			if sys.platform == "darwin":
				filepath = filedialog.askopenfilename(initialdir=get_resource_path('./'),
													  title=self.translate_service.get_translation('selectFile'))
			else:
				filepath = filedialog.askopenfilename(
					initialdir=get_resource_path('./'),
					title=self.translate_service.get_translation('selectFile'),
					filetypes=(
						('Audio files', '*.wav *.ogg *.mp3'),
						('All files', '*.*')
					)
				)
			self.button.translation_key = filepath
			self.button.update_text()

		except FileNotFoundError as e:
			print(e)

	def save_data(self, settings: Settings):
		settings.audio_path = self.button.translation_key
		return settings

	def create_button_text(self):
		text = self.font.render(self.translate_service.get_translation('beepSound'), True, (255, 255, 255))
		text_rect = text.get_rect()
		text_rect.midleft = self.width_percentage * 23, self.height_percentage * 20 + 20
		return text, text_rect
