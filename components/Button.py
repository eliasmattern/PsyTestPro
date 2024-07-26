from typing import Callable

import pygame

from events import LANGUAGE_EVENT
from services import PsyTestProConfig, TranslateService


class Button:
	def __init__(self, x: float, y: float, width: float, height: float, translation_key: str, action: Callable,
				 translate_service: TranslateService = None, color=None,
				 text_color=None, active_button_color=None, border_radius=8, hidden=False, align='center',
				 font_size=24, is_active=True):
		self.pos_x = x
		self.pos_y = y
		self.align = align
		self.translate_service = translate_service
		self.rect = pygame.Rect(x - width // 2, y, width, height)
		self.translation_key = translation_key
		self.psy_test_pro_config = PsyTestProConfig()
		self.settings = self.psy_test_pro_config.get_settings()
		self.font_size = font_size
		if color is None:
			self.color = pygame.Color(self.settings["buttonColor"])
		else:
			self.color = pygame.Color(color)
		if text_color is None:
			self.button_text_color = pygame.Color(self.settings["buttonTextColor"])
		else:
			self.button_text_color = pygame.Color(text_color)
		if active_button_color is None:
			self.active_button_color = pygame.Color(self.settings["activeButtonColor"])
		else:
			self.active_button_color = pygame.Color(active_button_color)
		self.label = pygame.font.SysFont('Arial', self.font_size).render(
			self.translate_service.get_translation(self.translation_key) if translate_service
			else self.translation_key,
			True, self.button_text_color)
		self.inactive_button_color = pygame.Color(self.settings["inactiveButtonColor"])
		self.action = action
		self.is_active = is_active
		self.border_radius = border_radius
		self.is_hidden = hidden
		self.pressed = False
		self.mouse_down = False

	def handle_event(self, event: pygame.event):
		if not self.is_hidden:
			if event.type == pygame.MOUSEBUTTONUP and self.rect.collidepoint(event.pos):
				if self.is_active and event.button == 1:
					self.action()
			elif event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
				if self.is_active:
					self.pressed = True
			elif event.type == pygame.MOUSEMOTION and not self.rect.collidepoint(event.pos):
				self.pressed = False
			elif event.type == pygame.MOUSEMOTION and self.rect.collidepoint(event.pos):
				if self.is_active:
					self.pressed = True
			elif event.type == LANGUAGE_EVENT:
				self.update_text()

	def set_hidden(self, hidden: bool):
		self.is_hidden = hidden

	def set_active(self, active: bool):
		self.is_active = active

	def update_text(self):
		self.label = pygame.font.SysFont('Arial', self.font_size).render(
			self.translate_service.get_translation(self.translation_key) if self.translate_service
			else self.translation_key,
			True, self.button_text_color)

	def draw(self, screen: pygame.Surface):
		if not self.is_hidden:
			label_width, label_height = self.label.get_size()
			if label_width > self.rect.width:
				count = 1
				while label_width > self.rect.width:
					self.label = self.label = pygame.font.SysFont('Arial', self.font_size - count).render(
						self.translate_service.get_translation(self.translation_key) if self.translate_service
						else self.translation_key, True, self.button_text_color)
					count += 1
					if self.font_size - count < 8:
						break
					label_width, label_height = self.label.get_size()

			if self.is_active:
				button_color = self.color if not self.pressed else self.active_button_color
			else:
				button_color = self.inactive_button_color
			pygame.draw.rect(screen, button_color, self.rect,
							 border_radius=self.border_radius)
			alignment_X = (self.rect.width - label_width) / 2 if self.align == 'center' else 5
			label_x = self.rect.x + alignment_X
			label_y = self.rect.y + (self.rect.height - label_height) / 2
			screen.blit(self.label, (label_x, label_y))

	def set_color(self, color: pygame.Color):
		self.color = color
