import pygame

from services import PsyTestProConfig


class UnderlinedText:
    def __init__(self, screen: pygame.Surface, text_surface: pygame.Surface, rect: pygame.Rect, start_pos: tuple, end_pos: tuple, color=None):
        self.psy_test_pro_config = PsyTestProConfig()
        self.screen = screen
        self.text_surface, self.rect, self.start_pos, self.end_pos = text_surface, rect, start_pos, end_pos
        self.settings = self.psy_test_pro_config.get_settings()
        self.primary_color = pygame.Color(self.settings["primaryColor"]) if color is None else color

    def draw(self):
        self.screen.blit(self.text_surface, self.rect)
        pygame.draw.line(self.screen, self.primary_color, self.start_pos, self.end_pos)