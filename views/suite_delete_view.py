import json
import sys

import pygame

from components import Button, QuestionDialog
from services import PsyTestProConfig
from services import TranslateService


class DeleteSuiteView:
    def __init__(self, translate_service: TranslateService):
        self.translate_service = translate_service
        self.page = 0
        self.running = True
        self.update = False
        self.psy_test_pro_config = PsyTestProConfig()
        self.settings = self.psy_test_pro_config.get_settings()
        self.suite_name = None
        self.delete_dialog = QuestionDialog(500, 200, 'delete', 'deleteSuiteMsg', '', self.translate_service,
                                            lambda: self.delete_action(self.suite_name), action_key='delete')
        self.show_delete_dialog = False

    def back(self):
        self.running = False

    def delete_suite(self, suite_name: str):
        self.suite_name = suite_name
        self.delete_dialog.info = self.translate_service.get_translation('suite') + ' ' + suite_name
        self.show_delete_dialog = True

    def delete_action(self, suite_name: str):
        if suite_name:
            # Load the original JSON from the file
            with open('json/taskConfig.json', 'r') as file:
                original_tasks = json.load(file)

            exp_keys = [key for key in original_tasks.keys() if suite_name in key]

            del original_tasks[exp_keys[0]]
            with open('json/suiteConfig.json', 'r') as file:
                original_suites = json.load(file)

            # Add a new value to the array

            original_suites.remove(suite_name)

            # Save the updated array back to the file
            with open('json/suiteConfig.json', 'w') as file:
                json.dump(original_suites, file)

            # Save the updated JSON back to the file
            with open('json/taskConfig.json', 'w') as file:
                json.dump(original_tasks, file, indent=4)
            self.update = True
            self.running = False
            self.suite_name = None
        return

    def page_update(self, increment: bool, splitted_suites: list):
        if increment:
            self.page = (self.page + 1) % len(splitted_suites)
        else:
            self.page = (
                (self.page - 1) if self.page > 0 else len(splitted_suites) - 1
            )

    def delete_suite_config_display(self, psy_test_pro):
        psy_test_pro_config = PsyTestProConfig()

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
        pygame.display.set_caption('Delete Suite')

        psy_test_pro_config.load_suites()
        suites = psy_test_pro_config.suites
        suites = list(filter(None, suites))

        splitted_suite = [
            suites[i: i + 5] for i in range(0, len(suites), 5)
        ]

        self.page = 0

        while self.running:
            screen.fill(black)  # Fill the screen with the black color

            buttons: list[Button] = []

            spacing = 0
            width, height = (
                pygame.display.Info().current_w,
                pygame.display.Info().current_h,
            )

            x = width // 2
            y = height // 2 - 150
            if len(splitted_suite) > 0:
                for suite in splitted_suite[self.page]:
                    exp_button = Button(
                        x,
                        y + 60 + spacing,
                        400,
                        40,
                        suite,
                        lambda exp=suite: self.delete_suite(
                            exp
                        ),
                    )
                    buttons.append(exp_button)
                    spacing += 60

            spacing = 5 * 60
            spacing += 60
            back_button = Button(
                x,
                y + spacing + 100,
                100,
                40,
                'back',
                lambda: self.back(),
                self.translate_service,
            )
            buttons.append(back_button)

            if len(splitted_suite) > 1:
                page_font = pygame.font.Font(None, int(24))
                page_text_surface = page_font.render(
                    str(self.page + 1) + '/' + str(len(splitted_suite)),
                    True,
                    light_grey,
                )
                page_rect = page_text_surface.get_rect()
                screen.blit(
                    page_text_surface,
                    (x - page_rect.width // 2, y + 100 + spacing - 60),
                )
                previous_page_button = Button(
                    x - 40,
                    y + 100 + spacing - 60,
                    25,
                    25,
                    '<',
                    lambda: self.page_update(False, splitted_suite),
                    border_radius=90
                )
                next_page_back_button = Button(
                    x + 40,
                    y + 100 + spacing - 60,
                    25,
                    25,
                    '>',
                    lambda: self.page_update(True, splitted_suite),
                    border_radius=90
                )
                buttons.append(previous_page_button)
                buttons.append(next_page_back_button)

            # This invokes the function draw_button

            # Display column headers with adjusted font size
            width, height = (
                pygame.display.Info().current_w,
                pygame.display.Info().current_h,
            )
            x = width // 2
            y = height // 2 - 150
            font = pygame.font.Font(
                None, int(30)
            )  # Create font object for header
            text_surface = font.render(
                self.translate_service.get_translation('deleteSuite'), True, light_grey
            )  # Render the text 'Task' with the font and color light_grey
            text_rect = text_surface.get_rect()
            screen.blit(text_surface, (x - text_rect.width // 2, y))

            for button in buttons:
                button.draw(screen)

            if self.show_delete_dialog:
                self.delete_dialog.draw(screen)
            if not self.delete_dialog.is_open:
                self.show_delete_dialog = False
                self.delete_dialog.is_open = True

            pygame.display.flip()  # Flip the display to update the screen
            for event in pygame.event.get():
                if self.show_delete_dialog:
                    self.delete_dialog.handle_events(event)
                else:
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    for button in buttons:
                        button.handle_event(event)
        self.running = True
        if (self.update):
            self.update = False
            self.delete_suite_config_display(psy_test_pro)
