import sys

import pygame
from pygame.locals import *
from components import InputBox, Button, CheckBox
from services import PsyTestProConfig
from services import TranslateService


class CreateSuiteView:
    def __init__(self, translate_service: TranslateService):
        self.running = True
        self.selected_multiple = False
        self.psy_test_pro_config = PsyTestProConfig()
        self.settings = self.psy_test_pro_config.get_settings()
        self.translate_service = translate_service
        self.create_multiple_check_box = None

    def back_to_psy_test_pro(self, psy_test_pro):
        self.selected_multiple = False
        psy_test_pro()

    def back(self):
        self.running = False

    def save_suite(
            self, psy_test_pro, suite_name: str, input_boxes: list[InputBox], check_box: CheckBox
    ):
        psy_test_pro_config = PsyTestProConfig()
        psy_test_pro_config.save_suite(suite_name, check_box.active)

        if self.create_multiple_check_box.active:
            check_box.active = True
            for input_box in input_boxes:
                input_box.text = ''
            return
        else:
            self.back_to_psy_test_pro(psy_test_pro)

    def create_input_boxes(self, psy_test_pro_config: PsyTestProConfig) -> tuple[list[InputBox], list[Button], CheckBox]:
        input_boxes = []
        buttons = []
        labels = ['suiteName']
        spacing = 60
        width, height = pygame.display.Info().current_w, pygame.display.Info().current_h
        x = width // 2
        y = height // 2 - 100
        for label in labels:
            input_box = InputBox(x, y, 400, 40, label, self.translate_service, not_allowed_characters=['_'])
            input_boxes.append(input_box)
            y += spacing
        option_check_box = CheckBox('createWithSchedule', x, y, active=True, translate_service=self.translate_service,
                                    font_size=24)
        exit_button = Button(x - 75, y + 60, 100, 40, 'back', lambda: self.back(), self.translate_service)
        submit_button = Button(
            x + 75,
            y + 60,
            100,
            40,
            'submit',
            lambda: self.save_suite(psy_test_pro_config, input_boxes[0].text, input_boxes, option_check_box),
            self.translate_service,
        )

        text_width = pygame.font.Font(None, int(24)).size(self.translate_service.get_translation('createWithSchedule'))
        self.create_multiple_check_box = CheckBox('createMultipleSuites', x + 160 + text_width[0] / 2, y + 75, active=True,
                                                  translate_service=self.translate_service, font_size=24)

        buttons.append(exit_button)
        buttons.append(submit_button)
        return input_boxes, buttons, option_check_box

    def validate_inputs(self, input_boxes):
        is_valid = False

        if input_boxes[0].text:
            is_valid = True

        if is_valid:
            return True
        else:
            return False

    def create_suite_config_display(self, psy_test_pro_config: PsyTestProConfig, create_continously=False):
        # Define colors
        black = pygame.Color(self.settings["backgroundColor"])
        light_grey = pygame.Color(self.settings["primaryColor"])

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
        pygame.display.set_caption('Create Suite')

        input_boxes, buttons, option_check_box = self.create_input_boxes(psy_test_pro_config)
        self.create_multiple_check_box.active = create_continously

        def get_input_index():
            index = 0
            for input_box in input_boxes:
                index += 1
                if input_box.is_selected:
                    input_boxes[index - 1].is_selected = False
                    break
            if index < len(input_boxes):
                return index
            else:
                return 0

        width, height = pygame.display.Info().current_w, pygame.display.Info().current_h
        x = width // 2
        y = height // 2 - 150

        font = pygame.font.Font(
            None, int(30 * width_scale_factor)
        )  # Create font object for header
        text_surface = font.render(
            self.translate_service.get_translation('createSuite'), True, light_grey
        )  # Render the text 'Task' with the font and color light_grey
        text_rect = text_surface.get_rect()

        while self.running:
            for event in pygame.event.get():
                self.create_multiple_check_box.handle_event(event)
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == KEYDOWN:
                    if event.key == K_TAB:
                        index = get_input_index()
                        input_boxes[index].is_selected = True
                    elif event.key == K_RETURN:
                        if self.validate_inputs(input_boxes):
                            self.save_suite(psy_test_pro_config, input_boxes[0].text, input_boxes, option_check_box)
                for box in input_boxes:
                    box.handle_event(event)
                for button in buttons:
                    button.handle_event(event)
                option_check_box.handle_event(event)
            screen.fill(black)  # Fill the screen with the black color

            screen.blit(text_surface, (x - text_rect.width // 2, y))

            if self.validate_inputs(input_boxes):
                buttons[1].set_active(True)
                buttons[1].set_color(pygame.Color(self.settings["buttonColor"]))
            else:
                buttons[1].set_active(False)
                buttons[1].set_color(pygame.Color(self.settings["inactiveButtonColor"]))

            for box in input_boxes:
                box.draw(screen)

            for button in buttons:
                button.draw(screen)

            option_check_box.draw(screen)
            self.create_multiple_check_box.draw(screen)
            pygame.display.flip()  # Flip the display to update the screen
        self.running = True
