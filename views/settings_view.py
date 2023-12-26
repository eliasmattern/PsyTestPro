import sys
import re
import pygame
import math
from components import InputBox, Button
from services import TeststarterConfig


class SettingsView:
    def __init__(self):
        self.chunk_size = math.floor((pygame.display.get_surface().get_height() / 100 * 40) / 100)
        self.running = True
        self.refresh = False
        self.teststarter_config = TeststarterConfig()
        self.errors = []
        self.settings = self.teststarter_config.get_settings()
        self.input_page = 0
        self.saving_errors = []
        self.translate_service = None
        self.saved_msg = []

    def check_contrast(self, input_boxes):
        MINIMUN_CONTRAST = 60
        has_contrast = True
        background_color_group = {
            'primaryColor': input_boxes['primaryColor'].text,
            'buttonColor': input_boxes['buttonColor'].text,
            'activeButtonColor': input_boxes['activeButtonColor'].text,
            'inactiveButtonColor': input_boxes['inactiveButtonColor'].text,
            'successColor': input_boxes['successColor'].text,
            'dangerColor': input_boxes['dangerColor'].text,
            'warningColor': input_boxes['warningColor'].text,
            'gridColor': input_boxes['gridColor'].text
        }

        button_text_color_group = {
            'buttonColor': input_boxes['buttonColor'].text,
            'activeButtonColor': input_boxes['activeButtonColor'].text,
            'inactiveButtonColor': input_boxes['inactiveButtonColor'].text,
        }

        background_color = pygame.Color(input_boxes['backgroundColor'].text)
        button_text_color = pygame.Color(input_boxes['buttonTextColor'].text)

        for key, entry in background_color_group.items():
            entry_color = pygame.Color(entry)
            check = abs(background_color[0] - entry_color[0]) + abs(background_color[1] - entry_color[1]) + abs(
                background_color[2] - entry_color[2])
            if not check > MINIMUN_CONTRAST:
                self.saving_errors.append(
                    self.translate_service.get_translation(key) + " " + self.translate_service.get_translation(
                        'contrastErrorMsg') + " " + self.translate_service.get_translation('backgroundColor'))
                has_contrast = False

        for key, entry in button_text_color_group.items():
            entry_color = pygame.Color(entry)
            check = abs(button_text_color[0] - entry_color[0]) + abs(button_text_color[1] - entry_color[1]) + abs(
                button_text_color[2] - entry_color[2])
            if not check > MINIMUN_CONTRAST:
                self.saving_errors.append(
                    self.translate_service.get_translation(key) + " " + self.translate_service.get_translation(
                        'contrastErrorMsg') + " " + self.translate_service.get_translation('buttonTextColor'))
                has_contrast = False

        return has_contrast

    def save_colors(self, input_boxes):
        self.saved_msg = []
        has_contrast = self.check_contrast(input_boxes)
        if has_contrast:
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
            self.saved_msg.append(self.translate_service.get_translation('updatedColors'))
            self.refresh_view()

    def refresh_view(self):
        self.running = False
        self.refresh = True

    def change_language(self, lang, translate_service, language_config):
        translate_service.set_language(lang)
        language_config.update_language_config(lang)
        self.refresh_view()

    def backToTeststarter(self, teststarter):
        teststarter()

    def change_theme(self, theme, input_boxes):
        if theme == 'darkMode':
            input_boxes['backgroundColor'].text = '#000000'
            input_boxes['primaryColor'].text = '#C0C0C0'
            input_boxes['buttonColor'].text = '#C0C0C0'
            input_boxes['buttonTextColor'].text = '#000000'
            input_boxes['successColor'].text = '#00B371'
            input_boxes['dangerColor'].text = '#FF0000'
            input_boxes['warningColor'].text = '#F0E68C'
            input_boxes['activeButtonColor'].text = '#DADDDC'
            input_boxes['inactiveButtonColor'].text = '#646464'
            input_boxes['gridColor'].text = '#C0C0C0'
        elif theme == 'lightMode':
            input_boxes['backgroundColor'].text = '#faf9f9'
            input_boxes['primaryColor'].text = '#000000'
            input_boxes['buttonColor'].text = '#0e1116'
            input_boxes['buttonTextColor'].text = '#faf9f9'
            input_boxes['successColor'].text = '#00B371'
            input_boxes['dangerColor'].text = '#FF0000'
            input_boxes['warningColor'].text = '#9B9B28'
            input_boxes['activeButtonColor'].text = '#232B38'
            input_boxes['inactiveButtonColor'].text = '#646464'
            input_boxes['gridColor'].text = '#232B38'
        for box in input_boxes.values():
            box.is_touched = True


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
                                translate_service, color=pygame.Color('#C0C0C0'), text_color=pygame.Color('Black'),
                                active_button_color=pygame.Color('#ACACAC'))
        german_button = Button(x + 110, y, 180, 40, 'german',
                               lambda: self.change_language('de', translate_service, language_config),
                               translate_service, color=pygame.Color('#C0C0C0'), text_color=pygame.Color('Black'),
                               active_button_color=pygame.Color('#ACACAC'))
        y += 2 * spacing
        dark_mode = Button(x - 110, y, 180, 40, 'darkMode',
                           lambda: self.change_theme('darkMode', input_boxes),
                           translate_service, color=pygame.Color('#C0C0C0'), text_color=pygame.Color('Black'),
                           active_button_color=pygame.Color('#ACACAC'))
        light_mode = Button(x + 110, y, 180, 40, 'lightMode',
                            lambda: self.change_theme('lightMode', input_boxes),
                            translate_service, color=pygame.Color('#C0C0C0'), text_color=pygame.Color('Black'),
                            active_button_color=pygame.Color('#ACACAC'))
        y += 2 * spacing

        input_y_pos = y
        for label, initial_text in zip(labels, initial_texts):
            if len(input_boxes) % self.chunk_size == 0:
                y = input_y_pos
            input_box = InputBox(x, y, 400, 40, label, translate_service, is_active=False,
                                 desc=translate_service.get_translation(label), initial_text=initial_text,
                                 color=pygame.Color('#C0C0C0'), active_color=pygame.Color('#DADDDC'),
                                 text_color=pygame.Color('#000000'), label_color=pygame.Color('#000000'),
                                 active_text_color=pygame.Color('#000000'), inactive_color=pygame.Color('#646464'))
            edit_button = Button(x + 275, y, 100, 40, 'edit', lambda name=label: input_boxes[name].set_active(True),
                                 translate_service, color=pygame.Color('#C0C0C0'), text_color=pygame.Color('Black'),
                                 active_button_color=pygame.Color('#ACACAC'))
            reset_button = Button(x + 275, y, 100, 40, 'reset',
                                  lambda name=label: input_boxes[name].set_text(self.settings[name]),
                                  translate_service, color=pygame.Color('#C0C0C0'), text_color=pygame.Color('Black'),
                                  active_button_color=pygame.Color('#ACACAC'), hidden=True)
            buttons[label] = edit_button
            buttons[label + "Reset"] = reset_button
            input_boxes[label] = input_box
            y += spacing
        y = input_y_pos + spacing * self.chunk_size
        exit_button = Button(x - 75, y + 100, 100, 40, 'back', lambda: self.backToTeststarter(teststarter),
                             translate_service, color=pygame.Color('#C0C0C0'), text_color=pygame.Color('Black'),
                             active_button_color=pygame.Color('#ACACAC'))
        save_button = Button(
            x + 75,
            y + 100,
            100,
            40,
            'save',
            lambda: self.save_colors(input_boxes),
            translate_service,
            color=pygame.Color('#C0C0C0'),
            text_color=pygame.Color('Black'),
            active_button_color=pygame.Color('#ACACAC')
        )

        buttons['english'] = english_button
        buttons['german'] = german_button
        buttons['darkMode'] = dark_mode
        buttons['lightMode'] = light_mode
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
                self.saving_errors = []
                self.saved_msg = []
                self.errors.append(box.text + ' ' + translate_service.get_translation('invalidHex'))
        if is_valid:
            self.errors.clear()
        return is_valid

    def split_dict(self, input_dict, chunk_size):
        dict_list = [{}]
        current_dict = 0

        for key, value in input_dict.items():
            dict_list[current_dict][key] = value
            if len(dict_list[current_dict]) >= chunk_size:
                dict_list.append({})
                current_dict += 1
        filtered_dict = [entry for entry in dict_list if entry]

        return filtered_dict

    def page_update(self, splitted_experiments, increment):
        if increment:
            self.input_page = (self.input_page + 1) % len(splitted_experiments)
        else:
            self.input_page = (
                (self.input_page - 1) if self.input_page > 0 else len(splitted_experiments) - 1
            )

    def display(self, teststarter, translate_service, language_config):
        self.translate_service = translate_service
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

        splitted_inputs = self.split_dict(input_boxes, self.chunk_size)

        iniitial_text_dict = {}

        page_x = buttons['back'].pos_x
        page_y = buttons['back'].pos_y

        font = pygame.font.Font(
            None, int(30 * width_scale_factor)
        )

        left_button = Button(page_x, page_y - 100, 40, 40, '<', lambda: self.page_update(splitted_inputs, False),
                             border_radius=90, color=pygame.Color('#C0C0C0'), text_color=pygame.Color('Black'),
                             active_button_color=pygame.Color('#ACACAC'))
        right_button = Button(page_x + 150, page_y - 100, 40, 40, '>', lambda: self.page_update(splitted_inputs, True),
                              border_radius=90, color=pygame.Color('#C0C0C0'), text_color=pygame.Color('Black'),
                              active_button_color=pygame.Color('#ACACAC'))

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

        language_surface = font.render(
            translate_service.get_translation('language'), True, light_grey
        )
        language_rect = language_surface.get_rect()

        color_surface = font.render(
            translate_service.get_translation('colors'), True, light_grey
        )
        color_rect = color_surface.get_rect()

        color_themes_surface = font.render(
            translate_service.get_translation('colorThemes'), True, light_grey
        )
        color_themes_rect = color_themes_surface.get_rect()
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                left_button.handle_event(event)
                right_button.handle_event(event)
                for key, box in input_boxes.items():
                    if key in splitted_inputs[self.input_page].keys():
                        box.handle_event(event)
                for key, button in buttons.items():
                    button.handle_event(event)
            screen.fill(black)  # Fill the screen with the black color

            page_surface = font.render(
                str(self.input_page + 1) + '/' + str(len(splitted_inputs)), True, light_grey
            )
            page_rect = page_surface.get_rect()
            page_rect.center = (page_x + 75, page_y - 80)

            screen.blit(text_surface, (x - text_rect.width // 2, y - 30))
            screen.blit(color_themes_surface, (x - color_themes_rect.width // 2, y + 180))
            screen.blit(color_surface, (x - color_rect.width // 2, y + 300))
            screen.blit(language_surface, (x - language_rect.width // 2, y + 60))
            screen.blit(page_surface, page_rect)
            for key, box in splitted_inputs[self.input_page].items():
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
                if key in splitted_inputs[self.input_page].keys():
                    box.set_hidden(False)
                    box.update_text()
                    box.draw(screen)
                else:
                    box.set_hidden(True)

            for key, button in buttons.items():
                if key in input_boxes.keys():
                    if not input_boxes[key].is_active and key in splitted_inputs[self.input_page].keys():
                        button.set_hidden(False)
                        button.draw(screen)
                    else:
                        button.set_hidden(True)
                elif "Reset" in key:
                    input_name = key.split('Reset')[0]
                    if input_boxes[input_name].is_active and input_name in splitted_inputs[self.input_page].keys() and \
                            input_boxes[input_name].is_touched and input_boxes[input_name].text != settings[
                        input_name]:
                        button.set_hidden(False)
                        button.draw(screen)
                    else:
                        button.set_hidden(True)
                else:
                    button.draw(screen)

            left_button.draw(screen)
            right_button.draw(screen)

            if self.errors:
                error_font = pygame.font.Font(None, 18)
                spacing = 0
                height = len(self.errors) * error_font.get_height()
                for error in self.errors:
                    error_surface = error_font.render(error, True, (200, 0, 0))
                    screen.blit(error_surface,
                                ((screen_width // 2 - (error_surface.get_width() // 2)),
                                 float((screen_height - height) / 100 * 95) + spacing))
                    spacing += error_font.get_height()

            if self.saving_errors or self.saved_msg:
                error_font = pygame.font.Font(None, 18)
                spacing = 0
                height = len(self.errors) * error_font.get_height()
                for error in self.saving_errors:
                    error_surface = error_font.render(error, True, (200, 0, 0))
                    screen.blit(error_surface,
                                ((screen_width // 2 - (error_surface.get_width() // 2)),
                                 float((screen_height - height) / 100 * 90) + spacing))
                    spacing += error_font.get_height()

                spacing = 0
                height = len(self.errors) * error_font.get_height()
                for msg in self.saved_msg:
                    msg_surface = error_font.render(msg, True, (192, 192, 192))
                    screen.blit(msg_surface,
                                ((screen_width // 2 - (msg_surface.get_width() // 2)),
                                 float((screen_height - height) / 100 * 90) + spacing))
                    spacing += error_font.get_height()

            pygame.display.flip()  # Flip the display to update the screen
        self.running = True
        if self.refresh:
            self.display(teststarter, translate_service, language_config)
