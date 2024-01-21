import pygame
from pygame.locals import *

from components import Button, InputBox
from services import PsyTestProConfig
import re


class TimePicker:
    def __init__(self, width, height, window_key, translate_service, time=None, action=None, action_key=''):
        screen_width, screen_height = pygame.display.get_surface().get_width(), pygame.display.get_surface().get_height()
        self.time = time
        if time is not None:
            self.hour, self.minute, self.second = time.split(':')
        self.window_key = window_key
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
        self.inactive_button_color = pygame.Color(self.settings['inactiveButtonColor'])
        self.button_color = pygame.Color(self.settings["buttonColor"])
        self.is_open = True
        self.move = False
        self.quit_rect = None
        self.action_key = action_key
        self.action_button = Button(self.window.x + self.width - 60, self.window.y + self.height - 35, 100, 25,
                                    self.action_key, lambda: self.execute_action(),
                                    translate_service=self.translate_service)
        self.close_button = Button(self.window.x + 60, self.window.y + self.height - 35, 100, 25,
                                   'back', lambda: self.close(),
                                   translate_service=self.translate_service)
        self.hour_input = InputBox(self.window.x + self.width / 2 - 55, self.window.y + self.height / 4, 40, 40,
                                   'hour_short', translate_service=self.translate_service, icon=False,
                                   initial_text=self.hour if self.time else '')
        self.minute_input = InputBox(self.window.x + self.width / 2, self.window.y + self.height / 4, 40, 40,
                                     'minute_short', translate_service=self.translate_service, icon=False,
                                     initial_text=self.minute if self.time else '')
        self.second_input = InputBox(self.window.x + self.width / 2 + 55, self.window.y + self.height / 4, 40, 40,
                                     'second_short', translate_service=self.translate_service, icon=False,
                                     initial_text=self.second if self.time else '')
        self.active_input = -1
        self.hour_input.is_selected = True
        self.hour_input.is_highlighted = True
        self.is_typing_hours, self.is_typing_minutes = False, False

    def open(self):
        self.is_open = True

    def close(self):
        self.is_open = False
        self.active_input = -1
        self.hour_input.is_selected = False
        self.minute_input.is_selected = False
        self.second_input.is_selected = False

    def set_time(self, time):
        self.time = time
        if len(self.time) > 0:
            self.hour, self.minute, self.second = time.split(':')
            self.hour_input = InputBox(self.window.x + self.width / 2 - 55, self.window.y + self.height / 4, 40, 40,
                                       'hour_short', translate_service=self.translate_service, icon=False,
                                       initial_text=self.hour if self.time else '')
            self.minute_input = InputBox(self.window.x + self.width / 2, self.window.y + self.height / 4, 40, 40,
                                         'minute_short', translate_service=self.translate_service, icon=False,
                                         initial_text=self.minute if self.time else '')
            self.second_input = InputBox(self.window.x + self.width / 2 + 55, self.window.y + self.height / 4, 40, 40,
                                         'second_short', translate_service=self.translate_service, icon=False,
                                         initial_text=self.second if self.time else '')
        else:
            self.hour, self.minute, self.second = '', '', ''
            self.hour_input.text, self.minute_input.text, self.second_input.text = '', '', ''

    def is_valid_datetime_format(self, datetime_str):
        # This pattern strictly matches DD/MM/YYYY HH:MM:SS
        pattern = r"^\d{2}:\d{2}:\d{2}$"
        return re.match(pattern, datetime_str) is not None

    def next_input(self):
        if self.hour_input.is_selected:
            self.active_input = 0
        if self.minute_input.is_selected:
            self.active_input = 1
        if self.second_input.is_selected:
            self.active_input = 2
        self.hour_input.is_selected = False
        self.minute_input.is_selected = False
        self.second_input.is_selected = False
        self.hour_input.is_highlighted = False
        self.minute_input.is_highlighted = False
        self.second_input.is_highlighted = False
        self.active_input += 1
        if self.active_input > 2:
            self.active_input = 0
        if self.active_input == 0:
            self.hour_input.is_selected = True
            self.hour_input.is_highlighted = True
        elif self.active_input == 1:
            self.minute_input.is_selected = True
            self.minute_input.is_highlighted = True
        elif self.active_input == 2:
            self.second_input.is_selected = True
            self.second_input.is_highlighted = True

    def handle_events(self, event):
        self.action_button.handle_event(event)
        self.close_button.handle_event(event)
        self.hour_input.handle_event(event)
        self.minute_input.handle_event(event)
        self.second_input.handle_event(event)

        # input validation
        self.hour_input.text = re.sub("[^0-9]", "", self.hour_input.text)
        self.minute_input.text = re.sub("[^0-9]", "", self.minute_input.text)
        self.second_input.text = re.sub("[^0-9]", "", self.second_input.text)

        # hour validation
        if len(self.hour_input.text) > 2:
            self.hour_input.text = self.hour_input.text[:2]
        if len(self.hour_input.text) == 1:
            self.is_typing_hours = True
        if len(self.hour_input.text) == 1 and int(self.hour_input.text) > 2:
            self.is_typing_hours = True
            self.hour_input.text = '0%s' % self.hour_input.text
        if len(self.hour_input.text) == 2 and int(self.hour_input.text[0]) > 2:
            self.hour_input.text = self.hour_input.text[1:2]
        if len(self.hour_input.text) == 2 and int(self.hour_input.text) >= 24:
            self.hour_input.text = self.hour_input.text[:1]
        if len(self.hour_input.text) == 2:
            if self.is_typing_hours:
                self.is_typing_hours = False
                self.next_input()

        # minute validation
        if len(self.minute_input.text) > 2:
            self.minute_input.text = self.minute_input.text[:2]
        if len(self.minute_input.text) == 1:
            self.is_typing_minutes = True
        if len(self.minute_input.text) == 1 and int(self.minute_input.text) > 5:
            self.is_typing_minutes = True
            self.minute_input.text = '0%s' % self.minute_input.text
        if len(self.minute_input.text) == 2 and int(self.minute_input.text[0]) > 5:
            self.minute_input.text = self.minute_input.text[1:2]
        if len(self.minute_input.text) == 2:
            if self.is_typing_minutes:
                self.is_typing_minutes = False
                self.next_input()

        # second validation
        if len(self.second_input.text) > 2:
            self.second_input.text = self.second_input.text[:2]
        if len(self.second_input.text) == 1 and int(self.second_input.text) > 5:
            self.second_input.text = '0%s' % self.second_input.text
        if len(self.second_input.text) == 2 and int(self.second_input.text[0]) > 5:
            self.second_input.text = self.second_input.text[1:2]

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
                    self.active_input = 0
                    self.hour_input.is_selected = False
                    self.minute_input.is_selected = False
                    self.second_input.is_selected = False
        elif event.type == KEYUP:
            if event.key == pygame.K_TAB:
                self.next_input()

            elif event.key == pygame.K_RETURN:
                self.execute_action()

    def draw(self, screen):
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
                self.close_button = Button(self.window.x + 60, self.window.y + self.height - 35, 100, 25,
                                           'back', lambda: self.close(),
                                           translate_service=self.translate_service)
                self.hour_input = InputBox(self.window.x + self.width / 2 - 55, self.window.y + self.height / 4, 40,
                                           40,
                                           'hour_short', translate_service=self.translate_service,
                                           initial_text=self.hour_input.text, icon=False)
                self.minute_input = InputBox(self.window.x + self.width / 2, self.window.y + self.height / 4, 40, 40,
                                             'minute_short', translate_service=self.translate_service,
                                             initial_text=self.minute_input.text, icon=False)
                self.second_input = InputBox(self.window.x + self.width / 2 + 55, self.window.y + self.height / 4, 40,
                                             40,
                                             'second_short', translate_service=self.translate_service,
                                             initial_text=self.second_input.text, icon=False)
                if self.active_input == 0:
                    self.hour_input.set_active(True)
                    self.hour_input.is_highlighted = False
                elif self.active_input == 1:
                    self.minute_input.set_active(True)
                    self.minute_input.is_highlighted = False
                elif self.active_input == 2:
                    self.second_input.set_active(True)
                    self.second_input.is_highlighted = False

        pygame.draw.rect(screen, self.background_color, self.window)
        pygame.draw.rect(screen, self.primary_color if not self.move else self.highlight_color, self.window, width=2)
        pygame.draw.rect(screen, self.primary_color if not self.move else self.highlight_color, self.title_bar)

        title_bar_surface = self.font.render(self.translate_service.get_translation(self.window_key), True,
                                             self.background_color)
        title_bar_pos = (self.title_bar.x + 10, self.title_bar.y + (self.title_bar.height // 4))

        split_surface = self.title_font.render(':', True,
                                               self.primary_color)
        split_pos1 = (self.window.x + self.width / 2 - 31, self.window.y + self.height / 4 + 10)
        split_pos2 = (self.window.x + self.width / 2 + 24, self.window.y + self.height / 4 + 10)

        quit_surface = self.font.render('X', True, self.background_color)
        quit_bar_pos = (self.title_bar.x + self.width - 22.5, self.title_bar.y + (self.title_bar.height // 4))
        self.quit_rect = quit_surface.get_rect()

        self.quit_rect.height = 30
        self.quit_rect.width = 30
        self.quit_rect.center = (quit_bar_pos[0] + 7.5,
                                 quit_bar_pos[1] + self.quit_rect.height / 4)

        if self.quit_rect.collidepoint((left, top)):
            pygame.draw.rect(screen, self.danger_color, self.quit_rect)

        screen.blit(title_bar_surface, title_bar_pos)
        screen.blit(quit_surface, quit_bar_pos)
        screen.blit(split_surface, split_pos1)
        screen.blit(split_surface, split_pos2)

        if self.is_valid_datetime_format(
                ':'.join((self.hour_input.text, self.minute_input.text, self.second_input.text))):
            self.action_button.set_active(True)
            self.action_button.set_color(self.button_color)
        else:
            self.action_button.set_active(False)
            self.action_button.set_color(self.inactive_button_color)

        self.action_button.update_text()
        self.close_button.update_text()

        self.hour_input.update_text()
        self.minute_input.update_text()
        self.second_input.update_text()

        self.action_button.draw(screen)
        self.close_button.draw(screen)
        self.hour_input.draw(screen)
        self.minute_input.draw(screen)
        self.second_input.draw(screen)

    def execute_action(self):
        if self.action_button.is_active:
            self.time = ':'.join((self.hour_input.text, self.minute_input.text, self.second_input.text))
            if self.action:
                self.action()
            self.is_open = False
            self.active_input = -1
