import calendar
from datetime import date, timedelta

import pygame
from dateutil.relativedelta import relativedelta

from components import Button
from services import PsyTestProConfig, TranslateService


class DatePickerComponent():
    def __init__(self, date: str, window_key: str, translate_service: TranslateService, action=None, action_key=''):
        screen_width, screen_height = pygame.display.get_surface().get_width(), pygame.display.get_surface().get_height()
        self.window_key = window_key
        self.translate_service = translate_service
        self.action = action
        self.day, self.month, self.year = date.split('/')
        width, height = 480, 390
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
        self.action_button = Button(self.window.x + self.width / 2, self.window.y + self.height - 35, 100, 25,
                                    self.action_key, lambda: self.execute_action(),
                                    translate_service=self.translate_service)
        self.date_buttons = None
        self.create_calendar(int(self.year), int(self.month), int(self.day))
        self.prev_month = None
        self.next_month = None

    def open(self):
        self.is_open = True

    def close(self):
        self.is_open = False

    def set_date(self, new_date: str):
        self.day, self.month, self.year = new_date.split('/')
        self.create_calendar(int(self.year), int(self.month), int(self.day))

    def handle_events(self, event: pygame.event):
        self.action_button.handle_event(event)
        if self.prev_month and self.next_month:
            self.prev_month.handle_event(event)
            self.next_month.handle_event(event)
        if self.date_buttons:
            for button in self.date_buttons:
                button.handle_event(event)
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

    def draw(self, screen: pygame.Surface):
        left, top = pygame.mouse.get_pos()
        if self.move:
            if -10 < top < screen.get_height() + 10 and -10 < left < screen.get_width() + 10:
                self.title_bar.top = top - 15
                self.title_bar.left = left - self.width // 2
                self.window.top = top - 15
                self.window.left = left - self.width // 2
                self.action_button = Button(self.window.x + self.width / 2, self.window.y + self.height - 35, 100, 25,
                                            self.action_key, lambda: self.execute_action(),
                                            translate_service=self.translate_service)
                self.create_calendar(int(self.year), int(self.month), int(self.day))

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
        title_surface = self.title_font.render(
            self.day + '. ' + self.translate_service.get_translation(
                calendar.month_name[int(self.month)].lower()) + ' ' + self.year,
            True, self.primary_color)
        title_pos = (self.window.x + self.width / 2 - title_surface.get_width() / 2, self.window.y + 50)

        self.prev_month = Button(self.window.x + self.width / 2 - title_surface.get_width() / 2 - 40,
                                 self.window.y + 50, 25, 25, '<', lambda: self.switch_month(False), border_radius=90)
        self.next_month = Button(self.window.x + self.width / 2 + title_surface.get_width() / 2 + 40,
                                 self.window.y + 50, 25, 25, '>', lambda: self.switch_month(True), border_radius=90)

        screen.blit(title_bar_surface, title_bar_pos)
        screen.blit(title_surface, title_pos)
        screen.blit(quit_surface, quit_bar_pos)

        self.prev_month.draw(screen)
        self.next_month.draw(screen)
        self.action_button.draw(screen)
        if self.date_buttons:
            for button in self.date_buttons:
                button.draw(screen)

    def execute_action(self):
        self.action()
        self.is_open = False

    def create_calendar(self, year: int, month: int, day: int):
        month_days = calendar.monthrange(year, month)[1]

        first_day = date(year, month, 1)

        weekday = first_day.weekday() + 1
        weeks = [[]]
        for _ in range(weekday - 1):
            weeks[0].append('')
        for _ in range(1, month_days + 1):
            weeks[-1].append(first_day) if len(weeks[-1]) < 7 else weeks.append([first_day])
            first_day = first_day + timedelta(days=1)
        self.date_buttons = []
        spacing = 40
        for index, week in enumerate(weeks):
            for day_num, day_date in enumerate(week):
                if day_date == '':
                    continue
                if str(day_date).split('-')[-1] == str(day).rjust(2, '0'):
                    color = (0, 0, 255)
                else:
                    color = None
                self.date_buttons.append(
                    Button(self.window.x + (self.width / 2) - (3 * spacing) + (day_num * spacing),
                           self.window.y + 100 + (index * spacing),
                           25, 25, str(day_date).split('-')[-1],
                           lambda y=year, m=month, d=str(day_date).split('-')[-1]: self.set_date(
                               '/'.join([str(d), str(m), str(y)])), border_radius=0,
                           color=color))

    def switch_month(self, next: bool):
        new_date = date(int(self.year), int(self.month), 1) + relativedelta(months=1) if next \
            else date(int(self.year), int(self.month), 1) + relativedelta(months=-1)
        self.day, self.month, self.year = str(new_date.day), str(new_date.month), str(new_date.year)
        self.create_calendar(int(self.year), int(self.month), int(self.day))
