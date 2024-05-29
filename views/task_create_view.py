import subprocess
import sys
import pygame
from components import InputBox, Button, TimePicker
from lib import text_screen
from services import PsyTestProConfig
import shlex
from services import TranslateService


class AddTaskView():
    def __init__(self, translate_service: TranslateService) -> None:
        self.translate_service = translate_service
        self.adding = True
        self.selected_multiple = False
        self.error = ''
        self.is_task_working = False
        self.psy_test_pro_config = PsyTestProConfig()
        self.settings = self.psy_test_pro_config.get_settings()
        self.inactive_button_color = pygame.Color(self.settings["inactiveButtonColor"])
        self.timepicker = TimePicker(300, 200, 'timeForTask', self.translate_service, action_key='save')
        self.show_time_picker = False

    def validate_task_inputs(self, input_boxes: list, time_input: str, command_inputs: list, text_screen_inputs: list, is_command: bool):
        is_valid = False

        if input_boxes[0].text and time_input:
            if is_command and command_inputs[0].text or not is_command and text_screen_inputs[0].text:
                is_valid = True

        return is_valid

    def open_time_picker(self):
        self.show_time_picker = True

    def preview(self, command: bool, command_inputs: list, text_screen_inputs: list):
        custom_variables = PsyTestProConfig().load_custom_variables()
        participant_info = {
            'participant_id': 'VARIABLE_ID',
            'experiment': 'VARIABLE_EXPERMENT',
            'start_time': 'VARIABLE_STARTTIME',
            'timestamp': 'VARIABLE_TIMESTAMP'
        }

        variables = {}

        for value in custom_variables:
            variables[value] = 'CUSTOM_VARIABLE'
        if command:
            try:
                command = command_inputs[0].text.format(id=participant_info['participant_id'],
                                                        experiment=participant_info['experiment'],
                                                        startTime=participant_info['start_time'],
                                                        timestamp=participant_info['timestamp'],
                                                        **variables)
                process = subprocess.Popen(shlex.split(command))
                output, error = process.communicate()
                return_code = process.wait()
                self.error = ''
                self.is_task_working = True
            except Exception as e:
                print(e)
                self.error = self.translate_service.get_translation('commandFailedToExecute')
                self.is_task_working = False
        else:
            try:
                title = text_screen_inputs[0].text.format(id=participant_info['participant_id'],
                                                          experiment=participant_info['experiment'],
                                                          startTime=participant_info['start_time'],
                                                          timestamp=participant_info['timestamp'],
                                                          **variables)

                description = text_screen_inputs[1].text.format(id=participant_info['participant_id'],
                                                                experiment=participant_info['experiment'],
                                                                startTime=participant_info['start_time'],
                                                                timestamp=participant_info['timestamp'],
                                                                **variables)

                text_screen(title, description, self.translate_service.get_translation('escToReturn'))
                self.is_task_working = True
            except Exception as e:
                print(e)
                self.is_task_working = False

    def save_task(
            self,
            create_continously: bool,
            variable: str,
            name: str,
            time: str,
            input_boxes: list,
            command_inputs: list,
            text_screen_inputs: list,
            command=None,
            title=None,
            description=None,
            is_command: bool=False,

    ):
        type = 'text' if not is_command else 'command'
        value = (
            {'title': title, 'description': description} if not is_command else command
        )
        psy_test_pro_config = PsyTestProConfig()
        psy_test_pro_config.save_task(variable, name, time, type, value)
        if create_continously:
            self.is_task_working = False
            self.error = ''
            for input_box in input_boxes:
                input_box.text = ''
            for input_box in command_inputs:
                input_box.text = ''
            for input_box in text_screen_inputs:
                input_box.text = ''
            self.timepicker.set_time('')
            return
        else:
            self.adding = False
            self.is_task_working = False
            self.error = ''
            self.timepicker.set_time('')

    def backToAddTask(self):
        self.adding = False
        self.timepicker.set_time('')

    def add(
            self,
            psy_test_pro,
            create_continously: bool,
            experiment: str
    ):
        variable = experiment
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
        pygame.display.set_caption('Create Task')

        self.selected_multiple = create_continously

        input_boxes: list[InputBox] = []
        buttons: list[Button] = []
        text_screen_inputs = []
        command_inputs = []
        command_labels = ['command']
        text_labels = ['title', 'description']
        spacing = 60
        width, height = pygame.display.Info().current_w, pygame.display.Info().current_h
        x = width // 2
        y = height // 2 - 100
        input_box = InputBox(
            x, y, 400, 40, 'taskName', self.translate_service, allow_new_line=False
        )
        input_boxes.append(input_box)
        y += spacing
        choose_time_button = Button(
            x,
            y,
            400,
            40,
            'timeForTask',
            lambda: self.open_time_picker(),
            self.translate_service,
            align='left'
        )
        y += spacing + spacing
        for label in text_labels:
            input_box = InputBox(
                x, y, 400, 40, label, self.translate_service, allow_new_line=True
            )
            text_screen_inputs.append(input_box)
            y += spacing
        y = height // 2 - 100 + 3 * spacing
        for label in command_labels:
            input_box = InputBox(
                x, y, 400.1, 40, label, self.translate_service, allow_new_line=False
            )
            command_inputs.append(input_box)
            y += spacing
        y += spacing

        exit_button = Button(
            x - 150, y + 60, 100, 40, 'back', self.backToAddTask, self.translate_service
        )
        submit_button = Button(
            x + 150,
            y + 60,
            100,
            40,
            'submit',
            lambda: self.save_task(
                self.selected_multiple,
                variable,
                input_boxes[0].text,
                self.timepicker.time,
                input_boxes,
                command_inputs,
                text_screen_inputs,
                command_inputs[0].text,
                text_screen_inputs[0].text,
                text_screen_inputs[1].text,
                command,
            ),
            self.translate_service,
        )
        error_y = y + 60
        preview_button = Button(
            x,
            y + 60,
            100,
            40,
            'preview',
            lambda: self.preview(command, command_inputs, text_screen_inputs),
            self.translate_service,
        )

        buttons.append(choose_time_button)
        buttons.append(exit_button)
        buttons.append(submit_button)
        buttons.append(preview_button)

        width, height = pygame.display.Info().current_w, pygame.display.Info().current_h
        x = width // 2
        y = height // 2 - 150

        question_font = pygame.font.Font(
            None, int(24)
        )  # Create font object for header
        option_text_rendered = question_font.render(
            self.translate_service.get_translation('createMultipleTasks'), True, light_grey
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
            self.translate_service.get_translation('createTask')
            + ' ' + self.translate_service.get_translation('for') + ' '
            + experiment.split('_')[0],
            True,
            light_grey,
        )  # Render the text 'Task' with the font and color light_grey
        text_rect = text_surface.get_rect()

        text_screen = True
        command = False

        text_screen_rendered = question_font.render(
            self.translate_service.get_translation('textScreen'), True, light_grey
        )
        text_screen_rect = text_screen_rendered.get_rect(left=x - 300, top=y + 180)
        text_tick_box_rect = pygame.Rect(
            x - 315 - 20 * height_scale_factor,
            y + 180,
            20 * width_scale_factor,
            20 * height_scale_factor,
        )

        command_screen_rendered = question_font.render(
            self.translate_service.get_translation('command'), True, light_grey
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
                if self.show_time_picker:
                    self.timepicker.handle_events(event)
                else:
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
                                self.error = ''
                            if command_tick_box_rect.collidepoint(
                                    mouse_pos
                            ):  # If the cursor position has collided with the start timer button
                                text_screen = not text_screen
                                command = not command
                                self.error = ''
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
                    input_boxes, self.timepicker.time, command_inputs, text_screen_inputs, command
            ):
                buttons[2].set_active(True)
                buttons[2].set_color(pygame.Color(self.settings["buttonColor"]))
                buttons[3].set_active(True)
                buttons[3].set_color(pygame.Color(self.settings["buttonColor"]))
            else:
                buttons[2].set_active(False)
                buttons[2].set_color(self.inactive_button_color)
                buttons[3].set_active(False)
                buttons[3].set_color(self.inactive_button_color)
            if not self.is_task_working:
                buttons[2].set_active(False)
                buttons[2].set_color(self.inactive_button_color)

            if self.timepicker.time and len(self.timepicker.time) > 0:
                choose_time_button.translate_service = None
                choose_time_button.translation_key = self.timepicker.time
            else:
                choose_time_button.translate_service = self.translate_service
                choose_time_button.translation_key = 'timeForTask'
            choose_time_button.update_text()

            for box in input_boxes:
                box.update_text()
                box.draw(screen)
            if command:
                for box in command_inputs:
                    box.set_hidden(False)
                    box.update_text()
                    box.draw(screen)
            else:
                for box in command_inputs:
                    box.set_hidden(True)
                    box.update_text()
                    box.draw(screen)
            if text_screen:
                for box in text_screen_inputs:
                    box.set_hidden(False)
                    box.draw(screen)
                    box.update_text()
            else:
                for box in text_screen_inputs:
                    box.set_hidden(True)
                    box.draw(screen)
                    box.update_text()
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
                error_font = pygame.font.Font(None, int(24))
                error_text_surface = error_font.render(
                    self.error,
                    True,
                    light_grey,
                )
                error_rect = error_text_surface.get_rect()
                screen.blit(
                    error_text_surface,
                    (x - error_rect.width // 2, error_y + spacing))

            if self.show_time_picker:
                self.timepicker.draw(screen)
            if not self.timepicker.is_open:
                self.show_time_picker = False
                self.timepicker.is_open = True

            pygame.display.flip()  # Flip the display to update the screen
