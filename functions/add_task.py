import pygame
import sys
from pygame.locals import *
from classes import InputBox, Button, TimeInput
from services import TeststarterConfig
from services import TeststarterConfig
from lib import text_screen
import subprocess

class AddTask():
    def __init__(self) -> None:
        self.adding = True
        self.selected_multiple = False
        self.error = ""
        self.is_task_working = False
    
    def validate_task_inputs(self, input_boxes, time_input, command_inputs, text_screen_inputs, is_command):
        is_valid = False

        if input_boxes[0].text and time_input.time:
            if command_inputs and command_inputs[0].text:
                is_valid = True

            if (
                not command_inputs
                and text_screen_inputs[0].text
                and text_screen_inputs[1].text
            ):
                is_valid = False

        return is_valid

    def preview(self, translate_service,command, command_inputs, text_screen_inputs):
        if command:
            try: 
                process = subprocess.Popen(command_inputs[0].text)
                process.communicate()
                self.error = ""
                self.is_task_working = True
            except Exception as e:
                print(e)
                self.error = translate_service.get_translation("commandFailedToExecute")
                self.is_task_working = False
        else:
            try:
                text_screen(text_screen_inputs[0].text, text_screen_inputs[1].text)
                self.is_task_working = True
            except Exception as e:
                print(e)
                self.is_task_working = False

    def save_task(
        self,
        teststarter,
        translate_service,
        create_continously,
        experiment,
        time_of_day,
        variable,
        name,
        time,
        command=None,
        title=None,
        description=None,
        is_command=False,
    ):
        type = "text" if not is_command else "command"
        value = (
            {"title": title, "description": description} if not is_command else command
        )
        teststarter_Config = TeststarterConfig()
        teststarter_Config.save_task(variable, name, time, type, value)
        if create_continously:
            self.is_task_working = False
            self.error = ""
            self.add(
                teststarter,
                translate_service,
                create_continously,
                experiment,
                time_of_day,
            )
        else:
            self.adding = False
            self.is_task_working = False
            self.error = ""

    def backToAddTask(self):
        self.adding = False

    def add(
        self,
        teststarter,
        translate_service,
        create_continously,
        experiment,
        time_of_day,
    ):
        variable = time_of_day + "_" + experiment + "_variable"
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
        pygame.display.set_caption("Create Task")

        self.selected_multiple = create_continously

        input_boxes = []
        buttons = []
        text_screen_inputs = []
        command_inputs = []
        command_labels = ["command"]
        text_labels = ["title", "description"]
        spacing = 60
        width, height = pygame.display.Info().current_w, pygame.display.Info().current_h
        x = width // 2
        y = height // 2 - 100
        input_box = InputBox(
            x, y, 400, 40, "taskName", translate_service, allow_new_line=False
        )
        input_boxes.append(input_box)
        y += spacing
        time_input = TimeInput(x, y, 400, 40, "timeForTask", translate_service)
        y += spacing + spacing
        for label in text_labels:
            input_box = InputBox(
                x, y, 400, 40, label, translate_service, allow_new_line=True
            )
            text_screen_inputs.append(input_box)
            y += spacing
        y = height // 2 - 100 + 3 * spacing
        for label in command_labels:
            input_box = InputBox(
                x, y, 400.1, 40, label, translate_service, allow_new_line=False
            )
            command_inputs.append(input_box)
            y += spacing
        y += spacing

        exit_button = Button(
            x - 150, y + 60, 100, 40, "back", self.backToAddTask, translate_service
        )
        submit_button = Button(
            x + 150,
            y + 60,
            100,
            40,
            "submit",
            lambda: self.save_task(
                teststarter,
                translate_service,
                self.selected_multiple,
                experiment,
                time_of_day,
                variable,
                input_boxes[0].text,
                time_input.time,
                command_inputs[0].text,
                text_screen_inputs[0].text,
                text_screen_inputs[1].text,
                command,
            ),
            translate_service,
        )
        error_y = y + 60
        preview_button = Button(
            x,
            y + 60,
            100,
            40,
            "preview",
            lambda: self.preview(translate_service, command, command_inputs, text_screen_inputs),
            translate_service,
        )

        buttons.append(time_input)
        buttons.append(exit_button)
        buttons.append(submit_button)
        buttons.append(preview_button)

        width, height = pygame.display.Info().current_w, pygame.display.Info().current_h
        x = width // 2
        y = height // 2 - 150

        question_font = pygame.font.Font(
            None, int(24 * width_scale_factor)
        )  # Create font object for header
        option_text_rendered = question_font.render(
            translate_service.get_translation("createMultipleTasks"), True, light_grey
        )
        option_text_rect = option_text_rendered.get_rect(left=x + 285, top=y + 420)
        tick_box_rect = pygame.Rect(
            x + 260 - 20 * height_scale_factor,
            y + 420,
            20 * width_scale_factor,
            20 * height_scale_factor,
        )

        font = pygame.font.Font(
            None, int(30 * width_scale_factor)
        )  # Create font object for header
        text_surface = font.render(
            translate_service.get_translation("createTask")
            + " for "
            + experiment
            + " "
            + time_of_day,
            True,
            light_grey,
        )  # Render the text 'Task' with the font and color light_grey
        text_rect = text_surface.get_rect()

        text_screen = True
        command = False

        text_screen_rendered = question_font.render(
            translate_service.get_translation("textScreen"), True, light_grey
        )
        text_screen_rect = text_screen_rendered.get_rect(left=x - 300, top=y + 180)
        text_tick_box_rect = pygame.Rect(
            x - 315 - 20 * height_scale_factor,
            y + 180,
            20 * width_scale_factor,
            20 * height_scale_factor,
        )

        command_screen_rendered = question_font.render(
            translate_service.get_translation("command"), True, light_grey
        )
        command_screen_rect = command_screen_rendered.get_rect(
            left=x + 100, top=y + 180
        )
        command_tick_box_rect = pygame.Rect(
            x + 85 - 20 * height_scale_factor,
            y + 180,
            20 * width_scale_factor,
            20 * height_scale_factor,
        )
        self.adding = True
        while self.adding:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # If the left mouse button clicked
                        mouse_pos = (
                            pygame.mouse.get_pos()
                        )  # Store the position of the curser when the mouse was clicked to a variable mouse_pos
                        if tick_box_rect.collidepoint(
                            mouse_pos
                        ):  # If the cursor position has collided with the start timer button
                            self.selected_multiple = not self.selected_multiple
                        if text_tick_box_rect.collidepoint(
                            mouse_pos
                        ):  # If the cursor position has collided with the start timer button
                            text_screen = not text_screen
                            command = not command
                            self.error = ""
                        if command_tick_box_rect.collidepoint(
                            mouse_pos
                        ):  # If the cursor position has collided with the start timer button
                            text_screen = not text_screen
                            command = not command
                            self.error = ""
                for box in input_boxes:
                    box.handle_event(event)
                for box in text_screen_inputs:
                    box.handle_event(event)
                for box in command_inputs:
                    box.handle_event(event)
                for button in buttons:
                    button.handle_event(event)
            screen.fill(black)  # Fill the screen with the black color

            screen.blit(option_text_rendered, option_text_rect)
            screen.blit(text_surface, (x - text_rect.width // 2, y))

            if self.validate_task_inputs(
                input_boxes, time_input, command_inputs, text_screen_inputs, command
            ):
                buttons[2].set_active(True)
                buttons[2].set_color("gray")
                buttons[3].set_active(True)
                buttons[3].set_color("gray")
            else:
                buttons[2].set_active(False)
                buttons[2].set_color((100, 100, 100))
                buttons[3].set_active(False)
                buttons[3].set_color((100, 100, 100))
            if not self.is_task_working:
                buttons[2].set_active(False)
                buttons[2].set_color((100, 100, 100))


            for box in input_boxes:
                box.draw(screen)
            if command:
                for box in command_inputs:
                    box.draw(screen)
            if text_screen:
                for box in text_screen_inputs:
                    box.draw(screen)

            for button in buttons:
                button.draw(screen)

            # draw the tick box rectangle on the window surface
            pygame.draw.rect(screen, light_grey, tick_box_rect, 2)
            pygame.draw.rect(screen, light_grey, text_tick_box_rect, 2)
            pygame.draw.rect(screen, light_grey, command_tick_box_rect, 2)
            # if the selected_multiple variable is equal to the option currently being processed in the loop
            if self.selected_multiple:
                # create a list of points that define the shape of the tick mark
                tick_mark_points = [
                    (
                        x + 275 - 25 * height_scale_factor,
                        y + 420 + 10 * height_scale_factor,
                    ),
                    (
                        x + 275 - 20 * height_scale_factor,
                        y + 420 + 15 * height_scale_factor,
                    ),
                    (
                        x + 275 - 15 * height_scale_factor,
                        y + 420 + 5 * width_scale_factor,
                    ),
                ]
                # draw lines connecting the points defined above (draw the tick)
                pygame.draw.lines(screen, light_grey, False, tick_mark_points, 2)

            screen.blit(text_screen_rendered, text_screen_rect)

            if text_screen:
                # create a list of points that define the shape of the tick mark
                text_tick_mark_points = [
                    (
                        x - 300 - 25 * height_scale_factor,
                        y + 180 + 10 * height_scale_factor,
                    ),
                    (
                        x - 300 - 20 * height_scale_factor,
                        y + 180 + 15 * height_scale_factor,
                    ),
                    (
                        x - 300 - 15 * height_scale_factor,
                        y + 180 + 5 * width_scale_factor,
                    ),
                ]

                # draw lines connecting the points defined above (draw the tick)
                pygame.draw.lines(screen, light_grey, False, text_tick_mark_points, 2)

            screen.blit(command_screen_rendered, command_screen_rect)

            if command:
                # create a list of points that define the shape of the tick mark
                command_tick_mark_points = [
                    (
                        x + 100 - 25 * height_scale_factor,
                        y + 180 + 10 * height_scale_factor,
                    ),
                    (
                        x + 100 - 20 * height_scale_factor,
                        y + 180 + 15 * height_scale_factor,
                    ),
                    (
                        x + 100 - 15 * height_scale_factor,
                        y + 180 + 5 * width_scale_factor,
                    ),
                ]

                # draw lines connecting the points defined above (draw the tick)
                pygame.draw.lines(
                    screen, light_grey, False, command_tick_mark_points, 2
                )

            if self.error:
                error_font = pygame.font.Font(None, int(24 * width_scale_factor))
                error_text_surface = error_font.render(
                    self.error,
                    True,
                    light_grey,
                )
                error_rect = error_text_surface.get_rect()
                screen.blit(
                    error_text_surface,
                    (x - error_rect.width // 2, error_y + spacing))
            pygame.display.flip()  # Flip the display to update the screen
