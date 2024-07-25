import pygame

from components import Button
from services import PsyTestProConfig, TranslateService


class QuestionDialog:
    def __init__(self, width: int, height: int, window_key: str, title_key: str, desc_key: str,
                 translate_service: TranslateService, action=None, action_key='', info='', cancel_key='back'):
        screen_width, screen_height = pygame.display.get_surface().get_width(), pygame.display.get_surface().get_height()
        self.window_key, self.title_key, self.desc_key, self.info = window_key, title_key, desc_key, info
        self.translate_service = translate_service
        self.action = action
        self.width, self.height = width, height
        self.window = pygame.Rect((screen_width / 2) - width // 2, (screen_height / 2) - height / 2, width, height)
        self.title_bar = pygame.Rect((screen_width / 2) - width // 2, (screen_height / 2) - height / 2, width, 30)
        self.font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 30)
        self.psy_test_pro_config = PsyTestProConfig()
        self.settings = self.psy_test_pro_config.get_settings()
        self.background_color = pygame.Color(self.settings["backgroundColor"])
        self.primary_color = pygame.Color(self.settings["primaryColor"])
        self.highlight_color = (min(self.primary_color[0] + 25, 255), min(self.primary_color[1] + 25, 255),
                                min(self.primary_color[2] + 25, 255))
        self.danger_color = pygame.Color(self.settings["dangerColor"])
        self.is_open = True
        self.move = False
        self.quit_rect = None
        self.action_key = action_key
        self.action_button = Button(self.window.x + self.width - 60, self.window.y + self.height - 35, 100, 25,
                                    self.action_key, lambda: self.execute_action(),
                                    translate_service=self.translate_service)
        self.close_button = Button(self.window.x + self.width - 170, self.window.y + self.height - 35, 100, 25,
                                   cancel_key, lambda: self.close(),
                                   translate_service=self.translate_service)

    def open(self):
        self.is_open = True

    def close(self):
        self.is_open = False

    def handle_events(self, event):
        self.action_button.handle_event(event)
        self.close_button.handle_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.quit_rect and self.quit_rect.collidepoint(event.pos):
                    pass
                elif self.title_bar.collidepoint(event.pos):
                    self.move = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.move = False
                if self.quit_rect and self.quit_rect.collidepoint(event.pos):
                    self.is_open = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.close()
            elif event.key == pygame.K_RETURN:
                self.execute_action()

    def draw(self, screen: pygame.Surface):
        left, top = pygame.mouse.get_pos()
        if self.move:
            if -10 < top < screen.get_height() + 10 and -10 < left < screen.get_width() + 10:
                self.title_bar.top = top - 15
                self.title_bar.left = left - self.width // 2
                self.window.top = top - 15
                self.window.left = left - self.width // 2
                self.action_button = Button(self.window.x + self.width - 60, self.window.y + self.height - 35, 100, 25,
                                            self.action_key, lambda: self.execute_action(),
                                            translate_service=self.translate_service)
                self.close_button = Button(self.window.x + self.width - 170, self.window.y + self.height - 35, 100, 25,
                                           'back', lambda: self.close(),
                                           translate_service=self.translate_service)

        pygame.draw.rect(screen, self.background_color, self.window)
        pygame.draw.rect(screen, self.primary_color if not self.move else self.highlight_color, self.window, width=2)
        pygame.draw.rect(screen, self.primary_color if not self.move else self.highlight_color, self.title_bar)

        title_bar_surface = self.font.render(self.translate_service.get_translation(self.window_key), True,
                                             self.background_color)
        title_bar_pos = (self.title_bar.x + 10, self.title_bar.y + (self.title_bar.height // 4))

        quit_surface = self.font.render('X', True, self.background_color)
        quit_bar_pos = (self.title_bar.x + self.width - 22.5, self.title_bar.y + (self.title_bar.height // 4))
        self.quit_rect = quit_surface.get_rect()

        self.quit_rect.height = 30
        self.quit_rect.width = 30
        self.quit_rect.center = (quit_bar_pos[0] + 7.5,
                                 quit_bar_pos[1] + self.quit_rect.height / 4)

        if self.quit_rect.collidepoint((left, top)):
            pygame.draw.rect(screen, self.danger_color, self.quit_rect)

        title_surface = self.title_font.render(self.translate_service.get_translation(self.title_key), True,
                                               self.primary_color)
        title_pos = (self.window.x + 10, self.window.y + (self.window.height // 4))

        desc_surface = self.font.render(self.translate_service.get_translation(self.desc_key), True, self.primary_color)
        desc_pos = (self.window.x + 10, self.window.y + (self.window.height // 4) + self.title_font.get_linesize())

        info_surface = self.font.render(self.info, True,
                                        self.primary_color)
        info_pos = (self.window.x + 10, self.window.y + (
                    self.window.height // 4) + self.title_font.get_linesize() + desc_surface.get_height())

        screen.blit(title_bar_surface, title_bar_pos)
        screen.blit(title_surface, title_pos)
        screen.blit(desc_surface, desc_pos)
        screen.blit(info_surface, info_pos)
        screen.blit(quit_surface, quit_bar_pos)

        self.action_button.draw(screen)
        self.close_button.draw(screen)

    def execute_action(self):
        self.action()
        self.is_open = False
