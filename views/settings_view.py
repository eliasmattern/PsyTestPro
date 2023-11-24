import sys
import re
import pygame

from components import InputBox, Button
from services import TeststarterConfig


class SettingsView:
    def __init__(self):
        self.running = True
        self.refresh = False
        self.teststarter_config = TeststarterConfig()
        self.errors = []
        self.settings = self.teststarter_config.get_settings()

    def backToTeststarter(self, teststarter):
        teststarter()

    def save_colors(self, input_boxes):
        self.teststarter_config.save_colors(input_boxes['backgroundColor'].text,
                                            input_boxes['primaryColor'].text,
                                            input_boxes['buttonColor'].text,
                                            input_boxes['buttonTextColor'].text,
                                            input_boxes['activeButtonColor'].text,
                                            input_boxes['inactiveButtonColor'].text,
                                            input_boxes['successColor'].text,
                                            input_boxes['dangerColor'].text,
                                            input_boxes['warningColor'].text,
                                            input_boxes['gridColor'].text)
        self.refresh_view()

    def refresh_view(self):
        self.running = False
        self.refresh = True

    def change_language(self, lang, translate_service, language_config):
        translate_service.set_language(lang)
        language_config.update_language_config(lang)
        self.refresh_view()

    def create_input_boxes(self, teststarter, translate_service, language_config, initial_texts):
        input_boxes = {}
        buttons = {}
        labels = ['backgroundColor', 'primaryColor', 'buttonColor', 'buttonTextColor', 'activeButtonColor',
                  'inactiveButtonColor', 'successColor', 'dangerColor', 'warningColor', 'gridColor']
        spacing = 60
        width, height = pygame.display.Info().current_w, pygame.display.Info().current_h
        x = width // 2
        y = height // 4 - 40

        english_button = Button(x - 110, y, 180, 40, 'english',
                                lambda: self.change_language('en', translate_service, language_config),
                                translate_service, color=pygame.Color('#C0C0C0'), text_color=pygame.Color('Black'))
        german_button = Button(x + 110, y, 180, 40, 'german',
                               lambda: self.change_language('de', translate_service, language_config),
                               translate_service, color=pygame.Color('#C0C0C0'), text_color=pygame.Color('Black'))
        y += 2 * spacing
        for label, initial_text in zip(labels, initial_texts):
            input_box = InputBox(x, y, 400, 40, label, translate_service, is_active=False,
                                 desc=translate_service.get_translation(label), initial_text=initial_text,
                                 color=pygame.Color('#C0C0C0'), active_color=pygame.Color('#DADDDC'),
                                 text_color=pygame.Color('#000000'), label_color=pygame.Color('#000000'),
                                 active_text_color=pygame.Color('#000000'), inactive_color=pygame.Color('#646464'))
            edit_button = Button(x + 275, y, 100, 40, 'edit', lambda name=label: input_boxes[name].set_active(True),
                                 translate_service, color=pygame.Color('#C0C0C0'), text_color=pygame.Color('Black'))
            buttons[label] = edit_button
            input_boxes[label] = input_box
            y += spacing

        exit_button = Button(x - 75, y + 60, 100, 40, 'back', lambda: self.backToTeststarter(teststarter),
                             translate_service, color=pygame.Color('#C0C0C0'), text_color=pygame.Color('Black'))
        save_button = Button(
            x + 75,
            y + 60,
            100,
            40,
            'save',
            lambda: self.save_colors(input_boxes),
            translate_service,
            color=pygame.Color('#C0C0C0'),
            text_color=pygame.Color('Black')
        )

        buttons['english'] = english_button
        buttons['german'] = german_button
        buttons['back'] = exit_button
        buttons['save'] = save_button
        return input_boxes, buttons

    def is_hex_color_code(self, code):
        hex_color_pattern = re.compile(r'^#([A-Fa-f0-9]{6})$')
        return bool(hex_color_pattern.match(code))

    def validate_inputs(self, input_boxes, translate_service):
        is_valid = True
        self.errors.clear()
        for key, box in input_boxes.items():
            if not self.is_hex_color_code(box.text):
                is_valid = False
                self.errors.append(box.text + ' ' + translate_service.get_translation('invalidHex'))
        if is_valid:
            self.errors.clear()
        return is_valid

    def display(self, teststarter, translate_service, language_config):
        # Define colors
        black = (0, 0, 0)
        light_grey = (192, 192, 192)

        # Get the screen width and height from the current device in use
        screen_info = pygame.display.Info()
        # Store the screen width in a new variable
        screen_width = screen_info.current_w
        # Store the screen height in a new variable
        screen_height = screen_info.current_h

        # Store the original screen dimensions used to design this program
        original_width = 1280
        original_height = 800

        # Calculate scaling factors for position and size adjustments (this is how we can make sure that the program adjusts to any screen it is executed on)
        width_scale_factor = screen_width / original_width
        height_scale_factor = screen_height / original_height

        # Creating a fullscreen display surface
        screen = pygame.display.get_surface()

        # Setting the window caption
        pygame.display.set_caption('Settings')

        settings = self.teststarter_config.get_settings()

        initial_texts = [settings['backgroundColor'], settings['primaryColor'], settings['buttonColor'],
                         settings['buttonTextColor'], settings['activeButtonColor'], settings['inactiveButtonColor'],
                         settings['successColor'], settings['dangerColor'], settings['warningColor'],
                         settings['gridColor']]

        input_boxes, buttons = self.create_input_boxes(
            teststarter, translate_service, language_config, initial_texts
        )

        iniitial_text_dict = {}

        for key, label in zip(input_boxes.keys(), initial_texts):
            iniitial_text_dict[key] = label

        width, height = pygame.display.Info().current_w, pygame.display.Info().current_h
        x = width // 2
        y = height // 4 - 150

        title_font = pygame.font.Font(
            None, int(40 * width_scale_factor)
        )  # Create font object for header
        text_surface = title_font.render(
            translate_service.get_translation('settings'), True, light_grey
        )  # Render the text 'Task' with the font and color light_grey
        text_rect = text_surface.get_rect()

        font = pygame.font.Font(
            None, int(30 * width_scale_factor)
        )
        language_surface = font.render(
            translate_service.get_translation('language'), True, light_grey
        )
        language_rect = language_surface.get_rect()

        color_surface = font.render(
            translate_service.get_translation('colors'), True, light_grey
        )
        color_rect = color_surface.get_rect()

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                for key, box in input_boxes.items():
                    box.handle_event(event)
                for key, button in buttons.items():
                    button.handle_event(event)
            screen.fill(black)  # Fill the screen with the black color

            screen.blit(text_surface, (x - text_rect.width // 2, y - 30))
            screen.blit(color_surface, (x - color_rect.width // 2, y + 180))
            screen.blit(language_surface, (x - language_rect.width // 2, y + 60))

            for key, box in input_boxes.items():
                if self.is_hex_color_code(box.text):
                    color = pygame.Color(box.text)
                    box_rect = pygame.Rect(box.posX - 225, box.posY + 10, 20, 20)
                    pygame.draw.rect(screen, color, box_rect)
                    pygame.draw.rect(screen, (255, 255, 255), box_rect, width=1)

            if self.validate_inputs(input_boxes, translate_service):
                buttons['save'].set_active(True)
                buttons['save'].set_color('gray')

            else:
                buttons['save'].set_active(False)
                buttons['save'].set_color((100, 100, 100))

            for key, box in input_boxes.items():
                box.update_text()
                box.draw(screen)

            for key, button in buttons.items():
                if key in input_boxes.keys():
                    if not input_boxes[key].is_active:
                        button.draw(screen)
                else:
                    button.draw(screen)

            if self.errors:
                error_font = pygame.font.Font(None, 18)
                spacing = 0
                height = len(self.errors) * error_font.get_height()
                for error in self.errors:
                    error_surface = error_font.render(error, True, (200, 0, 0))
                    screen.blit(error_surface,
                                ((screen_width // 2 - (error_surface.get_width() // 2)),
                                 float((screen_height - height) / 100 * 90) + spacing))
                    spacing += error_font.get_height()

            pygame.display.flip()  # Flip the display to update the screen
        self.running = True
        if self.refresh:
            self.display(teststarter, translate_service, language_config)
