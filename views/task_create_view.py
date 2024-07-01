import re
import sys
import webbrowser

import pygame
from components import InputBox, Button, TimePicker, CheckBox
from events import LANGUAGE_EVENT
from lib import text_screen
from services import PsyTestProConfig
from services import TranslateService, execute_command


class AddTaskView:
    def __init__(self, translate_service: TranslateService, editing=False, task_id: str=None, task_name=None, task_time=None,
                 task_title=None, task_desc=None, task_command=None, task_url=None, position=None) -> None:
        self.editing = editing
        self.task_id = task_id
        self.task_name = task_name
        self.task_time = task_time
        self.task_title = task_title
        self.task_desc = task_desc
        self.task_command = task_command
        self.task_url = task_url
        self.task_position = position
        self.translate_service = translate_service
        self.adding = True
        self.selected_multiple = False
        self.error = ''
        self.is_task_working = False
        self.psy_test_pro_config = PsyTestProConfig()
        self.settings = self.psy_test_pro_config.get_settings()
        self.inactive_button_color = pygame.Color(self.settings["inactiveButtonColor"])
        self.timepicker = TimePicker(300, 200, 'timeDuration', self.translate_service, action_key='save')
        if self.task_time:
            self.timepicker.set_time(self.task_time)
        self.show_time_picker = False

    def validate_task_inputs(self, input_boxes: list[InputBox], time_input: str, command_inputs: list[InputBox],
                             text_screen_inputs: list[InputBox], url_inputs: list[InputBox], is_command: bool,
                             is_url: bool):
        is_valid = False

        if input_boxes[0].text and time_input:
            if (is_command and command_inputs[0].text or not is_command and text_screen_inputs[0].text
                    or url_inputs[0].text and is_url):
                is_valid = True
        if is_url and is_valid:
            pattern = re.compile(r'^(http://|https://)[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(:[0-9]{1,5})?(/.*)?$')
            is_valid = re.match(pattern, url_inputs[0].text) is not None

        return is_valid

    def open_time_picker(self):
        self.show_time_picker = True

    def preview(self, command: bool, is_url: bool, command_inputs: list[InputBox], text_screen_inputs: list[InputBox], url_inputs: list[InputBox]):
        custom_variables = PsyTestProConfig().load_custom_variables()
        participant_info = {
            'participant_id': 'VARIABLE_ID',
            'suite': 'VARIABLE_SUITE',
            'start_time': 'VARIABLE_STARTTIME',
            'timestamp': 'VARIABLE_TIMESTAMP',
            'script_count': 0
        }

        variables = {}

        for value in custom_variables:
            variables[value] = 'CUSTOM_VARIABLE'
        if command:
            try:
                error, return_code = execute_command(command_inputs[0].text, participant_info, variables)
                if return_code != 0:
                    raise Exception(f"Command failed with return code {return_code}, Error: {error}")
                self.error = ''
                self.is_task_working = True
            except Exception as e:
                self.error = self.translate_service.get_translation('commandFailedToExecute')
                self.is_task_working = False
        elif is_url:
            try:
                url = url_inputs[0].text.format(id=participant_info['participant_id'],
                                                          suite=participant_info['suite'],
                                                          startTime=participant_info['start_time'],
                                                          timestamp=participant_info['timestamp'],
                                                          scriptCount='',
                                                          **variables)
                webbrowser.open(url)
                self.error = ''
                self.is_task_working = True
            except Exception as e:
                print(e)
                self.error = self.translate_service.get_translation('urlFailed')
                self.is_task_working = False
        else:
            try:
                title = text_screen_inputs[0].text.format(id=participant_info['participant_id'],
                                                          suite=participant_info['suite'],
                                                          startTime=participant_info['start_time'],
                                                          timestamp=participant_info['timestamp'],
                                                          scriptCount='',
                                                          **variables)

                description = text_screen_inputs[1].text.format(id=participant_info['participant_id'],
                                                                suite=participant_info['suite'],
                                                                startTime=participant_info['start_time'],
                                                                timestamp=participant_info['timestamp'],
                                                                scriptCount='',
                                                                **variables)

                text_screen(title, description, self.translate_service.get_translation('escToReturn'))
                self.is_task_working = True
            except Exception as e:
                print(e)
                self.is_task_working = False

    def save_task(
            self,
            create_continously: bool,
            suite: str,
            name: str,
            time: str,
            input_boxes: list[InputBox],
            command_inputs: list[InputBox],
            text_screen_inputs: list[InputBox],
            url_inputs: list[InputBox],
            command=None,
            title=None,
            description=None,
            url=None,
            is_text_field: bool = False,
            is_command: bool = False):
        if is_command or is_text_field:
            task_type = 'text' if not is_command else 'command'
            value = (
                {'title': title, 'description': description} if not is_command else command
            )
        else:
            task_type = 'url'
            value = url
        psy_test_pro_config = PsyTestProConfig()
        if not self.editing:
            psy_test_pro_config.save_task(suite, name, time, task_type, value)
        else:
            psy_test_pro_config.edit_task(self.task_id, suite, name, time, task_type, value)
        if create_continously:
            self.is_task_working = False
            self.error = ''
            for input_box in input_boxes:
                input_box.text = ''
            for input_box in command_inputs:
                input_box.text = ''
            for input_box in text_screen_inputs:
                input_box.text = ''
            for input_box in url_inputs:
                input_box.text = 'https://'
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
            create_continuously: bool,
            suite: str
    ):
        # Define colors
        background_color = pygame.Color(self.settings["backgroundColor"])
        primary_color = pygame.Color(self.settings["primaryColor"])

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

        self.selected_multiple = create_continuously

        input_boxes: list[InputBox] = []
        buttons: list[Button] = []
        text_screen_inputs: list[InputBox] = []
        command_inputs: list[InputBox] = []
        url_inputs: list[InputBox] = []
        command_labels = [('command', self.task_command)]
        url_labels = [('url', self.task_url)]
        text_labels = [('title', self.task_title), ('description', self.task_desc)]
        spacing = 60
        width, height = pygame.display.Info().current_w, pygame.display.Info().current_h
        x = width // 2
        y = height // 2 - 100
        input_box = InputBox(x, y, 400, 40, 'taskName', self.translate_service, allow_new_line=False,
                             initial_text=self.task_name if self.task_name else '')
        input_boxes.append(input_box)
        y += spacing
        choose_time_button = Button(
            x,
            y,
            400,
            40,
            'timeDuration',
            lambda: self.open_time_picker(),
            self.translate_service,
            align='left'
        )
        y += spacing + spacing
        for label in text_labels:
            input_box = InputBox(x, y, 400, 40, label[0], self.translate_service, allow_new_line=True,
                                 initial_text=label[1] if label[1] else '')
            text_screen_inputs.append(input_box)
            y += spacing

        y = height // 2 - 100 + 3 * spacing
        font = pygame.font.Font(None, int(30 * width_scale_factor))  # Create font object for header
        x_offset = font.size('?')[0] / 2
        info_text = font.render('?', True, primary_color)
        info_pos = (x + 225, y + 20 - (font.get_height() / 2))
        info_circle = (x + 225 + x_offset, y + 20)
        info_rect = pygame.rect.Rect(x + 212.5, y, 40, 40)
        triangle_vertices = [(x + 225 + x_offset, y), (x + 205 + x_offset, y - 20), (x + 245 + x_offset, y - 20)]
        popup_rect = pygame.rect.Rect(0, 0, 400, 250)
        popup_rect.center = x + 225 + x_offset, y - 145

        for label in command_labels:
            input_box = InputBox(
                x, y, 400, 40, label[0], self.translate_service, allow_new_line=False,
                initial_text=label[1] if label[1] else ''
            )
            command_inputs.append(input_box)
        for label in url_labels:
            input_box = InputBox(
                x, y, 400, 40, label[0], self.translate_service, allow_new_line=False,
                initial_text=label[1] if label[1] else 'https://'
            )
            url_inputs.append(input_box)

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
                create_continuously_check_box.active,
                suite,
                input_boxes[0].text,
                self.timepicker.time,
                input_boxes,
                command_inputs,
                text_screen_inputs,
                url_inputs,
                command_inputs[0].text,
                text_screen_inputs[0].text,
                text_screen_inputs[1].text,
                url_inputs[0].text,
                text_screen_check_box.active,
                command_check_box.active
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
            lambda: self.preview(command_check_box.active, url_check_box.active, command_inputs, text_screen_inputs, url_inputs),
            self.translate_service,
        )

        buttons.append(choose_time_button)
        buttons.append(exit_button)
        buttons.append(submit_button)
        buttons.append(preview_button)

        width, height = pygame.display.Info().current_w, pygame.display.Info().current_h
        x = width // 2
        y = height // 2 - 150

        tick_box_rect = pygame.Rect(
            x + 260 - 20 * height_scale_factor,
            y + 420,
            20 * width_scale_factor,
            20 * height_scale_factor,
        )

        text_surface = font.render(
            self.translate_service.get_translation('createTask')
            + ' ' + self.translate_service.get_translation('for') + ' '
            + suite.split('_')[0],
            True,
            primary_color,
        )  # Render the text 'Task' with the font and color primary_color
        text_rect = text_surface.get_rect()
        text_pos = x - text_rect.width // 2, y

        text_screen = False if self.task_command or self.task_url else True
        command = False if self.task_title or self.task_url or not self.task_command else True
        url = False if self.task_command or self.task_command or not self.task_url else True
        command_check_box = CheckBox('command', screen_width / 2 + 200, y + 180, command,
                                     self.translate_service)
        text_screen_check_box = CheckBox('textScreen', screen_width / 2 - 200, y + 180, text_screen,
                                         self.translate_service)
        url_check_box = CheckBox('url', screen_width / 2, y + 180, url, self.translate_service)

        create_continuously_check_box = CheckBox('createMultipleTasks', x + 320, y + 420, create_continuously, self.translate_service)
        var_font = pygame.font.Font(None, int(20))

        variables = ['id', 'suite', 'startTime', 'timestamp', 'scriptCount']
        x = width // 2
        y = height // 2 - 100 + 3 * spacing
        var_x, var_y = x + 225 + x_offset - 180, y - 250
        var_table_texts = []

        variables_title = self.translate_service.get_translation('variables')
        surface = var_font.render(variables_title, True, background_color)
        pos = (var_x, var_y)
        var_table_texts.append((surface, pos))
        var_y += var_font.get_height()

        for variable in variables:
            text = '{' + variable + '} ' + self.translate_service.get_translation(variable + 'Description')
            if var_font.size(text)[0] + var_x < var_x + 360:
                surface = var_font.render(text, True, background_color)
                pos = (var_x, var_y)
                var_table_texts.append((surface, pos))
                var_y += var_font.get_height()
            else:
                new_text = ''
                while var_font.size(text)[0] + var_x > var_x + 360:
                    words = text.split()
                    text = ' '.join(words[:-1])
                    new_text = ' '.join([words[-1], new_text])
                new_text2 = ''
                while var_font.size(new_text)[0] + var_x > var_x + 360:
                    words = new_text.split()
                    new_text = ' '.join(words[:-1])
                    new_text2 = ' '.join([words[-1], new_text2])
                surface = var_font.render(text, True, background_color)
                pos = (var_x, var_y)
                var_table_texts.append((surface, pos))
                var_y += var_font.get_height()
                surface = var_font.render(new_text, True, background_color)
                pos = (var_x, var_y)
                var_table_texts.append((surface, pos))
                var_y += var_font.get_height()
                surface = var_font.render(new_text2, True, background_color)
                pos = (var_x, var_y)
                var_table_texts.append((surface, pos))

        var_y += var_font.get_height()

        custom_variables = PsyTestProConfig().load_custom_variables()

        if len(custom_variables) > 0:
            var_y += var_font.get_height()
            custom_variables_title = self.translate_service.get_translation('customVariables')
            surface = var_font.render(custom_variables_title, True, background_color)
            pos = (var_x, var_y)
            var_table_texts.append((surface, pos))
            var_y += var_font.get_height()

            for variable in custom_variables:
                text = '{' + variable + '}'
                surface = var_font.render(text, True, background_color)
                pos = (var_x, var_y)
                var_table_texts.append((surface, pos))
                var_y += var_font.get_height()

        show_info = False

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
                                pygame.mouse.get_pos())  # Store the position of the curser when the mouse was clicked to a variable mouse_pos
                            if tick_box_rect.collidepoint(
                                    mouse_pos) and not self.editing:  # If the cursor position has collided with the start timer button
                                self.selected_multiple = not self.selected_multiple
                    elif event.type == pygame.MOUSEMOTION:
                        show_info = info_rect.collidepoint(event.pos)
                    command_before = command_check_box.active
                    text_screen_before = text_screen_check_box.active
                    url_before = url_check_box.active
                    text_screen_check_box.handle_event(event)
                    command_check_box.handle_event(event)
                    url_check_box.handle_event(event)
                    if not self.editing:
                        create_continuously_check_box.handle_event(event)
                    if command_before != command_check_box.active:
                        text_screen_check_box.active = False
                        command_check_box.active = True
                        url_check_box.active = False
                        self.is_task_working = False
                    elif text_screen_before != text_screen_check_box.active:
                        command_check_box.active = False
                        text_screen_check_box.active = True
                        url_check_box.active = False
                        self.is_task_working = False
                    elif url_before != url_check_box.active:
                        command_check_box.active = False
                        url_check_box.active = True
                        text_screen_check_box.active = False
                        self.is_task_working = False
                    for box in input_boxes:
                        box.handle_event(event)
                    for box in text_screen_inputs:
                        box.handle_event(event)
                    for box in url_inputs:
                        box.handle_event(event)
                    for box in command_inputs:
                        box.handle_event(event)
                    for button in buttons:
                        button.handle_event(event)
            screen.fill(background_color)  # Fill the screen with the background_color color

            screen.blit(text_surface, text_pos)

            if self.validate_task_inputs(input_boxes, self.timepicker.time, command_inputs, text_screen_inputs,
                                         url_inputs, command_check_box.active, url_check_box.active):
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
                choose_time_button.translation_key = 'timeDuration'
            choose_time_button.update_text()
            for box in input_boxes:
                box.draw(screen)
            if command_check_box.active:
                for box in command_inputs:
                    box.set_hidden(False)
                    box.draw(screen)
            else:
                for box in command_inputs:
                    box.set_hidden(True)
                    box.draw(screen)
            if text_screen_check_box.active:
                for box in text_screen_inputs:
                    box.set_hidden(False)
                    box.draw(screen)
            else:
                for box in text_screen_inputs:
                    box.set_hidden(True)
                    box.draw(screen)
            if url_check_box.active:
                for box in url_inputs:
                    box.set_hidden(False)
                    box.draw(screen)
            else:
                for box in url_inputs:
                    box.set_hidden(True)
                    box.draw(screen)
            for button in buttons:
                button.draw(screen)
            screen.blit(info_text, info_pos)
            pygame.draw.circle(screen, primary_color, info_circle, radius=20, width=2)
            if show_info:
                pygame.draw.polygon(screen, primary_color, triangle_vertices)
                pygame.draw.rect(screen, primary_color, popup_rect, border_radius=30)
                for surface, pos in var_table_texts:
                    screen.blit(surface, pos)
            # draw the tick box rectangle on the window surface
            # if the selected_multiple variable is equal to the option currently being processed in the loop
            if not self.editing:
                create_continuously_check_box.draw(screen)

            command_check_box.draw(screen)
            text_screen_check_box.draw(screen)
            url_check_box.draw(screen)

            if self.error:
                error_font = pygame.font.Font(None, int(24))
                error_text_surface = error_font.render(
                    self.error,
                    True,
                    primary_color,
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
