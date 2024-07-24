import pygame

from app_types import Settings
from components import UnderlinedText, Button, CheckBox
from events import LANGUAGE_EVENT
from services import TranslateService, LanguageConfiguration, PsyTestProConfig


class GeneralSettings:
    def __init__(self, screen: pygame.Surface, translate_service: TranslateService, old_settings: Settings):
        self.screen = screen
        self.translate_service = translate_service
        self.psy_test_pro_config = PsyTestProConfig()
        self.old_settings = old_settings
        self.language_config = LanguageConfiguration()
        self.font = pygame.font.Font(None, 34)
        self.texts = self.create_text()
        self.width_percentage, self.height_percentage = self.screen.get_width() / 100, self.screen.get_height() / 100
        self.buttons = self.create_buttons()
        self.checkboxes = self.create_checkboxes()

    def draw(self):
        for text in self.texts:
            text.draw()
        for button in self.buttons:
            button.draw(self.screen)
        for checkbox in self.checkboxes.values():
            self.screen.blit(checkbox['surface'], checkbox['rect'])
            checkbox['checkbox'].draw(self.screen)

    def handle_event(self, event: pygame.event.Event):
        if event.type == LANGUAGE_EVENT:
            self.checkboxes = self.create_checkboxes()
            self.texts = self.create_text()
        elif event.type == pygame.MOUSEBUTTONUP:
            for checkbox in self.checkboxes.values():
                if checkbox['rect'].collidepoint(event.pos):
                    checkbox['checkbox'].active = not checkbox['checkbox'].active
        for button in self.buttons:
            button.handle_event(event)
        for checkbox in self.checkboxes.values():
            checkbox['checkbox'].handle_event(event)

    def create_text(self) -> list[UnderlinedText]:
        texts = []
        self.width_percentage, self.height_percentage = self.screen.get_width() / 100, self.screen.get_height() / 100

        language_surface = self.font.render(self.translate_service.get_translation('language'), True, (255, 255, 255))
        language_rect = language_surface.get_rect()
        language_rect.topleft = (self.width_percentage * 23, self.height_percentage * 15)

        start_pos = self.width_percentage * 21, self.height_percentage * 16 + self.font.get_height()
        end_pos = self.width_percentage * 79, self.height_percentage * 16 + self.font.get_height()

        texts.append(
            UnderlinedText(self.screen, language_surface, language_rect, start_pos, end_pos, color=(255, 255, 255)))

        dispalay_settings_surface = self.font.render(self.translate_service.get_translation('displaySettings'), True,
                                                     (255, 255, 255))
        display_settings_rect = dispalay_settings_surface.get_rect()
        display_settings_rect.topleft = (self.width_percentage * 23, self.height_percentage * 29)

        start_pos = self.width_percentage * 21, self.height_percentage * 30 + self.font.get_height()
        end_pos = self.width_percentage * 79, self.height_percentage * 30 + self.font.get_height()
        texts.append(UnderlinedText(self.screen, dispalay_settings_surface, display_settings_rect, start_pos, end_pos,
                                    color=(255, 255, 255)))

        return texts

    def create_buttons(self) -> list[Button]:
        buttons = []

        english_button = Button(self.width_percentage * 35, self.height_percentage * 20, self.width_percentage * 25, 40,
                                'english',
                                lambda: self.change_language('en'),
                                self.translate_service, color=pygame.Color('#C0C0C0'), text_color=pygame.Color('Black'),
                                active_button_color=pygame.Color('#ACACAC'))
        german_button = Button(self.width_percentage * 65, self.height_percentage * 20, self.width_percentage * 25, 40,
                               'german',
                               lambda: self.change_language('de'),
                               self.translate_service, color=pygame.Color('#C0C0C0'), text_color=pygame.Color('Black'),
                               active_button_color=pygame.Color('#ACACAC'))

        buttons.append(english_button)
        buttons.append(german_button)
        return buttons

    def create_checkboxes(self):
        checkboxes = {}

        task_and_time_check_box = CheckBox('', self.width_percentage * 78, self.height_percentage * 35,
                                           active=self.old_settings.show_next_task, font_size=24,
                                           color=pygame.Color('#C0C0C0'))
        play_task_check_box = CheckBox('', self.width_percentage * 78, self.height_percentage * 40,
                                       active=self.old_settings.show_play_task_button, font_size=24,
                                       color=pygame.Color('#C0C0C0'))

        show_task_and_time_text = self.font.render(self.translate_service.get_translation('showTaskAndTime'), True,
                                                   (255, 255, 255))
        show_task_and_time_rect = show_task_and_time_text.get_rect()
        show_task_and_time_rect.topleft = (self.width_percentage * 23, self.height_percentage * 35)

        show_play_button_text = self.font.render(self.translate_service.get_translation('showPlayTaskButton'), True,
                                                 (255, 255, 255))
        show_play_button_rect = show_play_button_text.get_rect()
        show_play_button_rect.midleft = (self.width_percentage * 23, self.height_percentage * 40)

        checkboxes['show_task_and_time'] = {'surface': show_task_and_time_text, 'rect': show_task_and_time_rect,
                                            'checkbox': task_and_time_check_box}
        checkboxes['show_play_button'] = {'surface': show_play_button_text, 'rect': show_play_button_rect,
                                          'checkbox': play_task_check_box}

        return checkboxes

    def change_language(self, lang: str):
        self.translate_service.set_language(lang)
        self.language_config.update_language_config(lang)

    def save_data(self, settings: Settings):
        settings.show_next_task = self.checkboxes.get('show_task_and_time')['checkbox'].active
        settings.show_play_task_button = self.checkboxes.get('show_play_button')['checkbox'].active
        return settings
