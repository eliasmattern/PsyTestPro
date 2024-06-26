import sys

import pygame

from components import Button, QuestionDialog
from services import PsyTestProConfig
from services import TranslateService


class DeleteTaskView:
    def __init__(self, translate_service: TranslateService):
        self.running = True
        self.page = 0
        self.removing = True
        self.suite_name = ''
        self.psy_test_pro_config = PsyTestProConfig()
        self.settings = self.psy_test_pro_config.get_settings()
        self.suite = None
        self.task = None
        self.translate_service = translate_service
        self.delete_dialog = QuestionDialog(500, 200, 'delete', 'deleteTaskMsg', '', self.translate_service,
                                            lambda: self.delete_action(), action_key='delete')
        self.show_delete_dialog = False

    def backToConfig(self):
        self.running = False

    def backToAddTask(self):
        self.removing = False

    def split_dict(self, input_list: list, chunk_size: int):
        for i in range(0, len(input_list), chunk_size):
            yield input_list[i:i + chunk_size]

    def page_update(self, increment: bool, splitted_tasks: list):
        if increment:
            self.page = (self.page + 1) % len(splitted_tasks)
        else:
            self.page = ((self.page - 1) if self.page > 0 else len(splitted_tasks) - 1)

    def delete_task_from_config(self, suite: str, task: str):
        self.suite = suite
        self.task = task
        self.delete_dialog.info = self.translate_service.get_translation('task') + ': ' + task
        self.show_delete_dialog = True

    def delete_task(self, suite_name: str):
        self.suite = suite_name
        self.page = 0
        self.running = True

        psy_test_pro_config = PsyTestProConfig()
        # Define colors
        black = pygame.Color(self.settings["backgroundColor"])
        light_grey = pygame.Color(self.settings["primaryColor"])

        # Creating a fullscreen display surface
        screen = pygame.display.get_surface()

        # Setting the window caption
        pygame.display.set_caption('Delete task')
        full_suite_name = suite_name
        tasks = (psy_test_pro_config.load_task_of_suite(full_suite_name))
        chunk_size = 5
        splitted_tasks = [tasks[i:i + chunk_size] for i in range(0, len(tasks), chunk_size)]

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
            if len(splitted_tasks) > 0:
                for task in splitted_tasks[self.page]:
                    exp_button = Button(
                        x,
                        y + 60 + spacing,
                        400,
                        40,
                        task.name,
                        lambda t=task.name: self.delete_task_from_config(
                            full_suite_name,
                            t
                        ),
                    )
                    buttons.append(exp_button)
                    spacing += 60

            spacing = len(splitted_tasks[0]) * 60 if len(splitted_tasks) > 0 else 60
            spacing += 60
            back_button = Button(
                x,
                y + spacing + 100,
                100,
                40,
                'back',
                lambda: self.backToConfig(),
                self.translate_service,
            )
            buttons.append(back_button)

            if len(splitted_tasks) > 1:
                page_font = pygame.font.Font(None, int(24))
                page_text_surface = page_font.render(
                    str(self.page + 1) + '/' + str(len(splitted_tasks)),
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
                    lambda: self.page_update(False, splitted_tasks),
                    border_radius=90
                )
                next_page_back_button = Button(
                    x + 40,
                    y + 100 + spacing - 60,
                    25,
                    25,
                    '>',
                    lambda: self.page_update(True, splitted_tasks),
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
                None, int(32)
            )  # Create font object for header
            text_surface = font.render(
                self.translate_service.get_translation('deleteTaskFrom') + ' ' + suite_name.split('_')[0], True,
                light_grey
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

    def delete_action(self):
        config = PsyTestProConfig()
        config.delete_task(self.suite, self.task)
        self.show_delete_dialog = False
        self.delete_task(self.suite)
