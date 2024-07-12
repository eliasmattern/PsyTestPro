import sys

import pygame

from app_types import Task, TaskGroup
from components import Button, InputBox, TimePicker, QuestionDialog
from services import TranslateService, PsyTestProConfig
from views.task_create_view import AddTaskView


class CreateTaskGroupView:
    def __init__(self, screen: pygame.Surface, suite: str, translate_service: TranslateService, edit: bool = False,
                 group: TaskGroup = None):
        self.screen = screen
        self.translate_service = translate_service
        self.suite = suite
        self.psy_test_pro_config = PsyTestProConfig()
        self.settings = self.psy_test_pro_config.get_settings()
        self.primary_color = pygame.Color(self.settings["primaryColor"])
        self.background_color = pygame.Color(self.settings["backgroundColor"])
        self.buttons: dict[str, Button] = {}
        self.input_boxes: dict[str, InputBox] = {}
        self.running = True
        self.timepicker = TimePicker(300, 200, 'pauseBetweenLoops', self.translate_service, action_key='save')
        self.timepicker.is_open = False
        if group:
            time = str(group.pause_inbetween).split(':')
            new_time = ':'.join([s.zfill(2) for s in time])
            self.timepicker.set_time(new_time)
        self.existing_group: TaskGroup = group
        self.exists = edit
        self.edit = edit
        self.group_tasks = group.tasks if group else []
        self.initial_tasks = self.group_tasks.copy()
        self.save_warning_dialog = QuestionDialog(500, 200, 'warning', 'unsavedChanges', 'askForSave',
                                                  self.translate_service,
                                                  lambda: self.back(force=True), action_key='doNotSave',
                                                  cancel_key='cancel')
        self.save_warning_dialog.is_open = False
        self.delete_dialog = QuestionDialog(500, 200, 'delete', 'deleteGroupMsg', '', self.translate_service,
                                            lambda: self.delete_action(), action_key='delete')
        self.delete_dialog.is_open = False
        self.deleted = False

    def show(self):
        self.create_buttons()
        while self.running:
            self.handle_events()
            self.draw()
        self.running = True
        return self.deleted

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if self.timepicker.is_open:
                self.timepicker.handle_events(event)
            elif self.save_warning_dialog.is_open:
                self.save_warning_dialog.handle_events(event)
            elif self.delete_dialog.is_open:
                self.delete_dialog.handle_events(event)
            else:
                for button in self.buttons.values():
                    button.handle_event(event)
                for input_box in self.input_boxes.values():
                    input_box.handle_event(event)

    def draw(self):
        self.buttons['save_button'].is_active = all(len(input_box.text) > 0 for input_box in self.input_boxes.values())
        self.buttons['delete_button'].is_active = self.exists
        self.screen.fill(self.background_color)
        if self.timepicker.time and len(self.timepicker.time) > 0:
            self.buttons['choose_time_button'].translate_service = None
            self.buttons['choose_time_button'].translation_key = self.timepicker.time
        else:
            self.buttons['choose_time_button'].translation_key = 'pauseBetweenLoops'
            self.buttons['choose_time_button'].translate_service = self.translate_service
        self.buttons['choose_time_button'].update_text()

        for button in self.buttons.values():
            button.draw(self.screen)
        for input_box in self.input_boxes.values():
            input_box.draw(self.screen)

        if self.timepicker.is_open:
            self.timepicker.draw(self.screen)
        if self.save_warning_dialog.is_open:
            self.save_warning_dialog.draw(self.screen)
        if self.delete_dialog.is_open:
            self.delete_dialog.draw(self.screen)

        pygame.display.flip()

    def create_buttons(self):
        self.buttons: dict[str, Button] = {}
        input_names = ['group_name', 'loops']
        if self.existing_group:
            initial_texts = [self.existing_group.name, str(self.existing_group.loops)]
        else:
            initial_texts = ['', '']
        padding = 60
        for i, (name, initial_text) in enumerate(zip(input_names, initial_texts)):
            input_box = InputBox(self.screen.get_width() / 2, self.screen.get_height() / 4 + i * padding, 400, 40, name,
                                 self.translate_service, is_numeric=name == 'loops',
                                 maxVal=1000 if name == 'loops' else None, initial_text=initial_text,
                                 desc=self.translate_service.get_translation(name))
            self.input_boxes[name] = input_box

        choose_time_button = Button(
            self.screen.get_width() / 2,
            self.screen.get_height() / 4 + len(input_names) * padding,
            400,
            40,
            'pauseBetweenLoops',
            lambda: self.open_timepicker(),
            self.translate_service
        )

        create_task_button = Button(
            self.screen.get_width() / 2,
            self.screen.get_height() / 4 + (len(input_names) + 1) * padding,
            400,
            40,
            'createTask',
            lambda: self.add_task(),
            self.translate_service
        )

        save_button = Button(
            self.screen.get_width() / 2,
            self.screen.get_height() - 60,
            150,
            40,
            'save',
            self.save,
            self.translate_service
        )

        delete_button = Button(
            self.screen.get_width() / 2 + 200,
            self.screen.get_height() - 60,
            150,
            40,
            'delete',
            self.delete_group,
            self.translate_service
        )

        back_button = Button(
            self.screen.get_width() / 2 - 200,
            self.screen.get_height() - 60,
            150,
            40,
            'back',
            self.back,
            self.translate_service
        )

        self.buttons['choose_time_button'] = choose_time_button
        self.buttons['create_task_button'] = create_task_button
        self.buttons['delete_button'] = delete_button
        self.buttons['save_button'] = save_button
        self.buttons['back_button'] = back_button

    def back(self, force: bool = False):
        if force:
            self.running = False
        elif not self.exists and self.initial_tasks == self.group_tasks:
            self.running = False
        elif self.edit:
            time = str(self.existing_group.pause_inbetween).split(':')
            new_time = ':'.join([s.zfill(2) for s in time])
            if (self.group_tasks == self.initial_tasks and self.existing_group.name == self.input_boxes[
                'group_name'].text and str(self.existing_group.loops) == self.input_boxes['loops'].text
                    and new_time == self.timepicker.time):
                self.running = False
            else:
                self.save_warning_dialog.open()
        else:
            self.save_warning_dialog.open()

    def open_timepicker(self):
        self.timepicker.open()

    def add_task(self):
        add_task_view = AddTaskView(self.translate_service, new_group=True)
        new_tasks = add_task_view.add(False, self.suite)
        current_pos = len(self.group_tasks)
        for name, time, task_type, value in new_tasks:
            current_pos += 1
            task = Task(str(current_pos - 1), name, time, task_type, value, current_pos)
            self.group_tasks.append(task)

    def save(self):
        group_name = self.input_boxes['group_name'].text
        loops = int(self.input_boxes['loops'].text)
        pause = self.timepicker.time if self.timepicker.time is not None else "00:00:00"
        if not self.edit:
            self.psy_test_pro_config.create_group(self.suite, group_name, loops, pause, self.group_tasks)
        else:
            self.psy_test_pro_config.edit_group(self.suite, self.existing_group.id, group_name, loops, pause,
                                                self.group_tasks)
        self.back(True)

    def delete_action(self):
        self.psy_test_pro_config.delete_task(self.suite, self.existing_group.id)
        self.delete_dialog.is_open = False
        self.back(True)

    def delete_group(self):
        self.delete_dialog.info = self.translate_service.get_translation('group') + ': ' + self.existing_group.name
        self.delete_dialog.is_open = True
        self.deleted = True
