import copy
import sys
from datetime import datetime, timedelta
from enum import Enum

import pygame.event

from app_types import Settings
from components import Button
from events import LANGUAGE_EVENT
from services import TranslateService, PsyTestProConfig
from views.audio_settings import AudioSettings
from views.general_settings import GeneralSettings
from views.video_settings import VideoSettings


class SettingsTypes(Enum):
    GENERAL = 'general'
    VIDEO = 'video'
    AUDIO = 'audio'


class SettingsView:
    def __init__(self, screen: pygame.Surface, translate_service: TranslateService):
        self.screen = screen
        self.translate_service = translate_service
        self.psy_test_pro_config = PsyTestProConfig()
        self.width_percentage, self.height_percentage = self.screen.get_width() / 100, self.screen.get_height() / 100
        self.current_settings_type = SettingsTypes.GENERAL
        self.settings = Settings(self.translate_service, self.psy_test_pro_config.get_settings())
        self.old_settings = Settings(self.translate_service, self.psy_test_pro_config.get_settings())
        self.general_settings = GeneralSettings(self.screen, self.translate_service, self.old_settings)
        self.video_settings = VideoSettings(self.screen, self.translate_service, self.old_settings)
        self.audio_settings = AudioSettings(self.screen, self.translate_service, self.old_settings)
        self.running = True
        self.font = pygame.font.Font(None, 30)
        self.tabs, self.active_tabs, self.rects, self.divider = self.create_tabs()
        self.back_button, self.save_button = self.create_buttons()
        self.saving = None

    def display(self):
        self.current_settings_type = SettingsTypes.GENERAL
        self.settings = Settings(self.translate_service, self.psy_test_pro_config.get_settings())
        self.old_settings = Settings(self.translate_service, self.psy_test_pro_config.get_settings())
        self.general_settings = GeneralSettings(self.screen, self.translate_service, self.old_settings)
        self.video_settings = VideoSettings(self.screen, self.translate_service, self.old_settings)
        self.audio_settings = AudioSettings(self.screen, self.translate_service, self.old_settings)
        while self.running:
            self.draw()
            self.handle_events()
        self.running = True

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONUP:
                for tab, rect in self.rects.items():
                    if rect.collidepoint(event.pos):
                        self.current_settings_type = tab
            elif event.type == LANGUAGE_EVENT:
                self.tabs, self.active_tabs, self.rects, self.divider = self.create_tabs()
            if self.current_settings_type == SettingsTypes.GENERAL:
                self.general_settings.handle_event(event)
            elif self.current_settings_type == SettingsTypes.VIDEO:
                self.video_settings.handle_event(event)
            elif self.current_settings_type == SettingsTypes.AUDIO:
                self.audio_settings.handle_event(event)
            self.back_button.handle_event(event)
            self.save_button.handle_event(event)

    def draw(self):
        self.screen.fill((0, 0, 0))
        pygame.draw.line(self.screen, (255, 255, 255), self.divider['start_pos'], self.divider['end_pos'], width=2)
        pygame.draw.line(self.screen, (255, 255, 255), self.active_tabs[self.current_settings_type.value]['start'],
                         self.active_tabs[self.current_settings_type.value]['end'], width=4)
        for tab, rect in self.rects.items():
            if rect.collidepoint(pygame.mouse.get_pos()):
                temp_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
                temp_surface.fill((255, 255, 255, 160))
                self.screen.blit(temp_surface, rect.topleft)
                pygame.draw.line(self.screen, (255, 255, 255),
                                 self.active_tabs[tab.value]['start'],
                                 self.active_tabs[tab.value]['end'], width=4)

        for text in self.tabs:
            self.screen.blit(text['surface'], text['rect'])

        if self.current_settings_type == SettingsTypes.GENERAL:
            self.general_settings.draw()
        elif self.current_settings_type == SettingsTypes.VIDEO:
            self.video_settings.draw()
        elif self.current_settings_type == SettingsTypes.AUDIO:
            self.audio_settings.draw()

        self.back_button.draw(self.screen)
        self.video_settings.validate_settings()
        if len(self.video_settings.errors) > 0:
            self.save_button.set_active(False)
        else:
            self.save_button.set_active(True)
        if self.saving is not None:
            if self.saving + timedelta(seconds=2) > datetime.now():
                self.save_button.color = pygame.Color('#00B371')
                self.save_button.active_button_color = pygame.Color('#00B371')
                self.save_button.translation_key = 'savedSettings'
                self.save_button.update_text()
            else:
                self.save_button.color = pygame.Color('#C0C0C0')
                self.save_button.active_button_color = pygame.Color('#ACACAC')
                self.save_button.translation_key = 'save'
                self.save_button.update_text()
                self.saving = None

        self.save_button.draw(self.screen)

        pygame.display.flip()

    def create_tabs(self):
        tabs = []
        active_tabs = {}
        rects = {}

        divider = {'start_pos': (self.width_percentage * 20, self.height_percentage * 10),
                   'end_pos': (self.width_percentage * 80, self.height_percentage * 10)}

        for i, tab in enumerate(SettingsTypes):
            text = self.font.render(self.translate_service.get_translation(tab.value), True, pygame.Color('white'))
            text_rect = text.get_rect()

            text_rect.center = (
                self.width_percentage * 30 + (i * self.width_percentage * 20), self.height_percentage * 7)
            tabs.append({'surface': text, 'rect': text_rect})

            rects[tab] = pygame.Rect(self.width_percentage * 20 + (i * self.width_percentage * 20),
                                     self.height_percentage * 5,
                                     self.width_percentage * 20, self.height_percentage * 5)

            active_tabs[tab.value] = {
                'start': (
                    self.width_percentage * 20 + (i * self.width_percentage * 20), self.height_percentage * 10 - 3),
                'end': (self.width_percentage * 40 + (i * self.width_percentage * 20), self.height_percentage * 10 - 3)}

        return tabs, active_tabs, rects, divider

    def create_buttons(self):
        back_button = Button(self.width_percentage * 35, self.height_percentage * 90, self.width_percentage * 20, 40,
                             'back', self.back, self.translate_service, color=pygame.Color('#C0C0C0'),
                             text_color=pygame.Color('Black'), active_button_color=pygame.Color('#ACACAC'))
        save_button = Button(self.width_percentage * 65, self.height_percentage * 90, self.width_percentage * 20, 40,
                             'save', self.save, self.translate_service, color=pygame.Color('#C0C0C0'),
                             text_color=pygame.Color('Black'), active_button_color=pygame.Color('#ACACAC'))
        return back_button, save_button

    def back(self):
        self.running = False

    def save(self):
        self.saving = datetime.now()
        self.settings = self.general_settings.save_data(self.settings)
        self.settings = self.video_settings.save_data(self.settings)
        self.settings = self.audio_settings.save_data(self.settings)
        if self.settings != self.old_settings:
            self.psy_test_pro_config.save_settings(self.settings)
            self.old_settings = copy.deepcopy(self.settings)
            self.general_settings.old_settings = copy.deepcopy(self.settings)
            self.video_settings.old_settings = copy.deepcopy(self.settings)
            self.audio_settings.old_settings = copy.deepcopy(self.settings)
