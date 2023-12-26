import pygame
from services import PsyTestProConfig


class Button:
    def __init__(self, x, y, width, height, translation_key, action, translate_service=None, color=None,
                 text_color=None, active_button_color=None, border_radius=8, hidden=False):
        self.pos_x = x
        self.pos_y = y
        self.translate_service = translate_service
        self.rect = pygame.Rect(x - width // 2, y, width, height)
        self.translation_key = translation_key
        self.psy_test_pro_config = PsyTestProConfig()
        self.settings = self.psy_test_pro_config.get_settings()
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
        self.label = pygame.font.SysFont('Arial', 24).render(
            self.translate_service.get_translation(self.translation_key) if translate_service
            else self.translation_key,
            True, self.button_text_color)
        self.action = action
        self.is_active = True
        self.border_radius = border_radius
        self.is_hidden = hidden
        self.pressed = False
        self.mouse_down = False

    def handle_event(self, event):
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

    def set_hidden(self, hidden):
        self.is_hidden = hidden

    def set_active(self, active):
        self.is_active = active

    def update_text(self):
        self.label = pygame.font.SysFont('Arial', 24).render(
            self.translate_service.get_translation(self.translation_key) if self.translate_service
            else self.translation_key,
            True, self.button_text_color)

    def draw(self, screen):
        if not self.is_hidden:
            pygame.draw.rect(screen, self.color if not self.pressed else self.active_button_color, self.rect,
                             border_radius=self.border_radius)
            label_width, label_height = self.label.get_size()
            label_x = self.rect.x + (self.rect.width - label_width) // 2
            label_y = self.rect.y + (self.rect.height - label_height) // 2
            screen.blit(self.label, (label_x, label_y))

    def set_color(self, color):
        self.color = color
