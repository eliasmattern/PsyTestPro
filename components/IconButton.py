from typing import Callable

import pygame

from services import PsyTestProConfig, get_resource_path


class IconButton:
    def __init__(self, x: float, y: float, width: float, height: float, img_width, img_height, icon_file: str,
                 action: Callable, color=None,
                 text_color=None, active_button_color=None, border_radius=8, hidden=False, align='center', font_size=24,
                 is_active=True):
        self.pos_x = x
        self.pos_y = y
        self.align = align
        self.rect = pygame.Rect(x - width // 2, y, width, height)
        self.icon = pygame.image.load(get_resource_path(icon_file))
        self.icon = pygame.transform.scale(self.icon, (img_width, img_height))
        self.img_width, self.img_height = img_width, img_height
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

    def set_hidden(self, hidden: bool):
        self.is_hidden = hidden

    def set_active(self, active: bool):
        self.is_active = active

    def draw(self, screen: pygame.Surface):
        if not self.is_hidden:
            if self.is_active:
                button_color = self.color if not self.pressed else self.active_button_color
            else:
                button_color = self.inactive_button_color
            pygame.draw.rect(screen, button_color, self.rect,
                             border_radius=self.border_radius)

            screen.blit(self.icon, (self.pos_x - self.img_width / 2, self.pos_y + 5))

    def set_color(self, color: pygame.Color):
        self.color = color
