import sys

import pygame
from pygame.locals import *
from classes import InputBox, Button, CheckBox
from services import TeststarterConfig


class CreateExperimentConfig:
    def __init__(self):
        self.running = True
        self.selected_multiple = False

    def backToTeststarter(self, teststarter):
        self.selected_multiple = False
        teststarter()

    def back(self):
        self.running = False

    def save_experiment(
            self, teststarter, experiment_name, input_boxes, check_box
    ):
        teststarter_config = TeststarterConfig()
        teststarter_config.save_experiment(experiment_name, check_box.active)

        if self.selected_multiple:
            check_box.active = True
            for input_box in input_boxes:
                input_box.text = ''
            return
        else:
            self.backToTeststarter(teststarter)

    def create_input_boxes(self, teststarter, translate_service, selected_multiple):
        input_boxes = []
        buttons = []
        labels = ['experimentName']
        spacing = 60
        width, height = pygame.display.Info().current_w, pygame.display.Info().current_h
        x = width // 2
        y = height // 2 - 100
        for label in labels:
            input_box = InputBox(x, y, 400, 40, label, translate_service, not_allowed_characters=['_'])
            input_boxes.append(input_box)
            y += spacing
        check_box = CheckBox('createWithSchedule', x, y, active=True, translate_service=translate_service, font_size=24)
        exit_button = Button(x - 75, y + 60, 100, 40, 'back', lambda: self.back(), translate_service)
        submit_button = Button(
            x + 75,
            y + 60,
            100,
            40,
            'submit',
            lambda: self.save_experiment(
                teststarter, input_boxes[0].text, input_boxes, check_box
            ),
            translate_service,
        )

        buttons.append(exit_button)
        buttons.append(submit_button)
        return input_boxes, buttons, check_box

    def validate_inputs(self, input_boxes):
        is_valid = False

        if (
                input_boxes[0].text
        ):
            is_valid = True

        if is_valid:
            return True
        else:
            return False

    def create_experiment_config_display(
            self, teststarter, translate_service, create_continously=False
    ):
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
        pygame.display.set_caption('Create Experiment')

        self.selected_multiple = create_continously

        input_boxes, buttons, check_box = self.create_input_boxes(
            teststarter, translate_service, self.selected_multiple
        )

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

        question_font = pygame.font.Font(
            None, int(24 * width_scale_factor)
        )  # Create font object for header
        option_text_rendered = question_font.render(
            translate_service.get_translation('createMultipleExperiments'),
            True,
            light_grey,
        )
        option_text_rect = option_text_rendered.get_rect(left=x + 180, top=y + 180)
        tick_box_rect = pygame.Rect(
            x + 170 - 20 * height_scale_factor,
            y + 180,
            20 * width_scale_factor,
            20 * height_scale_factor,
        )

        font = pygame.font.Font(
            None, int(30 * width_scale_factor)
        )  # Create font object for header
        text_surface = font.render(
            translate_service.get_translation('createExperiment'), True, light_grey
        )  # Render the text 'Task' with the font and color light_grey
        text_rect = text_surface.get_rect()

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == KEYDOWN:
                    if event.key == K_TAB:
                        index = get_input_index()
                        input_boxes[index].is_selected = True
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # If the left mouse button clicked
                        mouse_pos = (
                            pygame.mouse.get_pos()
                        )  # Store the position of the curser when the mouse was clicked to a variable mouse_pos
                        if tick_box_rect.collidepoint(
                                mouse_pos
                        ):  # If the cursor position has collided with the start timer button
                            self.selected_multiple = not self.selected_multiple
                for box in input_boxes:
                    box.handle_event(event)
                for button in buttons:
                    button.handle_event(event)
                check_box.handle_event(event)
            screen.fill(black)  # Fill the screen with the black color

            screen.blit(option_text_rendered, option_text_rect)
            screen.blit(text_surface, (x - text_rect.width // 2, y))

            if self.validate_inputs(input_boxes):
                buttons[1].set_active(True)
                buttons[1].set_color('gray')
            else:
                buttons[1].set_active(False)
                buttons[1].set_color((100, 100, 100))

            for box in input_boxes:
                box.update_text()
                box.draw(screen)

            for button in buttons:
                button.draw(screen)

            check_box.draw(screen)

            # draw the tick box rectangle on the window surface
            pygame.draw.rect(screen, light_grey, tick_box_rect, 2)
            # if the selected_multiple variable is equal to the option currently being processed in the loop
            if self.selected_multiple:
                # create a list of points that define the shape of the tick mark
                tick_mark_points = [
                    (
                        x + 180 - 25 * height_scale_factor,
                        y + 180 + 10 * height_scale_factor,
                    ),
                    (
                        x + 180 - 20 * height_scale_factor,
                        y + 180 + 15 * height_scale_factor,
                    ),
                    (
                        x + 180 - 15 * height_scale_factor,
                        y + 180 + 5 * width_scale_factor,
                    ),
                ]
                # draw lines connecting the points defined above (draw the tick)
                pygame.draw.lines(screen, light_grey, False, tick_mark_points, 2)

            pygame.display.flip()  # Flip the display to update the screen
        self.running = True
