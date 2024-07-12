import sys
import tkinter as tk
import tkinter.filedialog
import webbrowser
from typing import Union

import pygame

from app_types import Task, TaskTypeEnum, TaskGroup
from components import Button, InputBox, IconButton, QuestionDialog
from services import PsyTestProConfig, TranslateService, ImportTasksService, get_resource_path
from .task_create_group_view import CreateTaskGroupView
from .task_create_view import AddTaskView


class ManageTasksView:
    def __init__(self, translate_service: TranslateService):
        self.screen = pygame.display.get_surface()
        self.translate_service = translate_service
        self.is_running = True
        self.psy_test_pro_config = PsyTestProConfig()
        self.settings = self.psy_test_pro_config.get_settings()
        self.primary_color = pygame.Color(self.settings["primaryColor"])
        self.background_color = pygame.Color(self.settings["backgroundColor"])
        self.group_button_color = pygame.Color(self.settings["groupButtonColor"])
        self.danger_color = pygame.Color(self.settings["dangerColor"])
        self.tasks: list[list[Task]] = []
        self.rects = []
        self.buttons: dict[str, Button] = {}
        self.icon_buttons: dict[str, IconButton] = {}
        self.input_boxes: dict[str, InputBox] = {}
        self.refresh = False
        self.suite = ''
        self.formatted_suite = ''
        self.page = 0
        self.font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 30)
        self.task_length = 0
        self.active_group = None
        self.title = ''
        self.delete_dialog = QuestionDialog(500, 200, 'delete', 'deleteTaskMsg', '', self.translate_service,
                                            lambda: self.delete_action(), action_key='delete')
        self.delete_dialog.is_open = False
        self.deleting_task = None

    def display(self, suite_name: str):
        self.suite = suite_name
        self.formatted_suite = suite_name.replace('_schedule', '').replace('_list', '').replace('_', ' ')
        self.title = self.translate_service.get_translation('manageTasksFor') + self.formatted_suite
        tasks: list[Task] = self.psy_test_pro_config.load_task_of_suite(suite_name)
        sorted_tasks = sorted(tasks, key=lambda task: task.position)
        self.task_length = len(sorted_tasks)
        current_tasks = list(self.split_list(sorted_tasks, 24))
        self.tasks = current_tasks
        self.create_buttons()
        while self.is_running:
            if self.refresh and self.active_group is None:
                self.refresh = False
                tasks = self.psy_test_pro_config.load_task_of_suite(suite_name)
                sorted_tasks = sorted(tasks, key=lambda task: task.position)
                self.task_length = len(sorted_tasks)
                current_tasks = list(self.split_list(sorted_tasks, 24))
                self.tasks = current_tasks
                self.create_buttons()
            elif self.refresh and self.active_group is not None:
                self.refresh = False
                tasks = self.psy_test_pro_config.load_task_of_group(suite_name, self.active_group)
                sorted_tasks = sorted(tasks, key=lambda task: task.position)
                self.task_length = len(sorted_tasks)
                current_tasks = list(self.split_list(sorted_tasks, 24))
                self.tasks = current_tasks
                self.create_buttons()
                pass
            self.draw()
            self.handle_events()
        self.is_running = True

    def draw(self):
        self.screen.fill(self.background_color)
        for button in self.buttons.values():
            button.draw(self.screen)
        for button in self.icon_buttons.values():
            button.draw(self.screen)
        for input_box in self.input_boxes.values():
            input_box.draw(self.screen)
        for rect in self.rects:
            pygame.draw.rect(self.screen, self.primary_color, rect, width=2, border_radius=10)
        if len(self.tasks) > 1:
            page_text = f'{self.page + 1}/{len(self.tasks)}'
            page_surface = self.font.render(page_text, True, self.primary_color)
            page_rect = page_surface.get_rect()
            page_rect.center = (self.screen.get_width() / 2, self.screen.get_height() / 8 + 8 * 80 + 12.5)
            self.screen.blit(page_surface, page_rect)

        title_surface = self.title_font.render(self.title, True, self.primary_color)
        title_rect = title_surface.get_rect()
        title_rect.center = (
            self.screen.get_width() / 2, self.screen.get_height() / 8 - (self.title_font.get_height() * 3))

        self.screen.blit(title_surface, title_rect)

        if self.delete_dialog.is_open:
            self.delete_dialog.draw(self.screen)
        pygame.display.flip()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if self.delete_dialog.is_open:
                self.delete_dialog.handle_events(event)
            else:
                for input_box in self.input_boxes.values():
                    input_box.handle_event(event)
                for button in self.buttons.values():
                    button.handle_event(event)
                for button in self.icon_buttons.values():
                    button.handle_event(event)

    def create_buttons(self):
        self.buttons: dict[str, Button] = {}
        self.icon_buttons: dict[str, IconButton] = {}
        self.input_boxes: dict[str, InputBox] = {}
        self.rects = []
        x = self.screen.get_width() / 5
        y = self.screen.get_height() / 8
        row_spacing = 80
        column_spacing = self.screen.get_width() / 2 - self.screen.get_width() / 5
        row, column = 0, 0
        if not len(self.tasks) == 0:
            for task in self.tasks[self.page]:
                task_x, task_y = x + column * column_spacing, y + row * row_spacing
                button_color = self.primary_color if isinstance(task, Task) else self.group_button_color
                active_color = pygame.Color(min(button_color.r + 10, 255), min(button_color.g + 10, 255),
                                            min(button_color.b + 10, 255)) if isinstance(task, TaskGroup) else None
                button = Button(
                    task_x,
                    task_y,
                    200,
                    40,
                    task.name,
                    lambda t=task: self.edit_task(t),
                    color=button_color,
                    active_button_color=active_color
                )
                icon_active_color = pygame.Color(min(self.danger_color.r + 10, 255), min(self.danger_color.g + 10, 255),
                                                 min(self.danger_color.b + 10, 255))

                icon_button = IconButton(
                    task_x + 130,
                    task_y,
                    40,
                    40,
                    30,
                    30,
                    'img/dark_trash.png' if sum([self.primary_color.g, self.primary_color.r,
                                                 self.primary_color.b]) > 382 else 'img/light_trash.png',
                    lambda t=task: self.delete_task(t),
                    color=self.danger_color,
                    active_button_color=icon_active_color
                )

                input_box = InputBox(task_x - 130, task_y, 40, 40, '', initial_text=str(task.position),
                                     is_numeric=True, icon=False, minVal=1, maxVal=self.task_length,
                                     on_deselect=lambda pos=task.position, t=task.id, r=row: self.rearrange(str(pos),
                                                                                                            t + str(
                                                                                                                r),
                                                                                                            t))
                rect = pygame.Rect(task_x - 165, task_y - 10, 330, 60)

                self.buttons[task.id + str(row)] = button
                self.icon_buttons[task.id + str(row)] = icon_button
                self.input_boxes[task.id + str(row)] = input_box
                self.rects.append(rect)

                if row < 7:
                    row += 1
                else:
                    column += 1
                    row = 0
        left_button = Button(
            self.screen.get_width() / 2 - 50,
            y + 8 * row_spacing,
            25,
            25,
            '<',
            lambda: self.page_update(False, self.tasks),
            border_radius=90
        )
        right_button = Button(
            self.screen.get_width() / 2 + 50,
            y + 8 * row_spacing,
            25,
            25,
            '>',
            lambda: self.page_update(True, self.tasks),
            border_radius=90
        )
        back_button = Button(
            self.screen.get_width() / 2 - 300,
            self.screen.get_height() - 60,
            150,
            40,
            'back',
            self.back,
            self.translate_service
        )

        create_task_button = Button(
            self.screen.get_width() / 2 -100,
            self.screen.get_height() - 60,
            150,
            40,
            'createTask',
            lambda: self.add_task(),
            self.translate_service,
        )

        import_task_button = Button(
            self.screen.get_width() / 2 + 300,
            self.screen.get_height() - 60,
            150,
            40,
            'importTasks',
            lambda: self.import_task(self.suite, True),
            self.translate_service,
        )

        create_group_button = Button(
            self.screen.get_width() / 2 + 100,
            self.screen.get_height() - 60,
            150,
            40,
            'addGroup' if self.active_group is None else 'editGroup',
            lambda: self.open_creat_group_view(),
            self.translate_service,
        )

        get_template_button = Button(
            self.screen.get_width() - 150,
            self.screen.get_height() / 8 - (self.title_font.get_height() * 3) -20,
            250,
            40,
            'getImportTemplate',
            lambda: self.download_template(),
            self.translate_service,
        )

        self.buttons['back_button'] = back_button
        self.buttons['create_group_button'] = create_group_button
        self.buttons['add_task'] = create_task_button
        self.buttons['import_tasks'] = import_task_button
        self.buttons['download_template'] = get_template_button
        if len(self.tasks) > 1:
            self.buttons['left_button'] = left_button
            self.buttons['right_button'] = right_button

    def rearrange(self, old_pos, input_name, task_id):
        if old_pos == self.input_boxes[input_name].text:
            return
        if self.input_boxes[input_name].text == '':
            self.input_boxes[input_name].text = old_pos
            return
        tasks = []
        for task in self.tasks:
            tasks.extend(task)
        new_pos = int(self.input_boxes[input_name].text)
        current_position = int(old_pos)
        for task in tasks:
            if task.id != task_id:
                if current_position < new_pos:
                    if current_position < task.position <= new_pos:
                        task.position -= 1
                else:
                    if new_pos <= task.position < current_position:
                        task.position += 1
            else:
                task.position = new_pos
        if self.active_group is None:
            self.psy_test_pro_config.save_task_list(self.suite, tasks)
        else:
            self.psy_test_pro_config.save_group_task_list(self.suite, self.active_group, tasks)
        self.refresh = True

    def back(self):
        if self.active_group is None:
            self.is_running = False
        else:
            self.active_group = None
            self.refresh = True
            self.page = 0
            self.title = self.translate_service.get_translation('manageTasksFor') + self.formatted_suite

    def split_list(self, input_list: list, chunk_size: int):
        for i in range(0, len(input_list), chunk_size):
            yield input_list[i:i + chunk_size]

    def page_update(self, increment: bool, splitted_tasks: list):
        if increment:
            self.page = (self.page + 1) % len(splitted_tasks)
        else:
            self.page = (self.page - 1) if self.page > 0 else len(splitted_tasks) - 1
        self.refresh = True

    def edit_task(self, task: Union[Task, TaskGroup]):
        if isinstance(task, TaskGroup):
            self.active_group = task.id
            self.refresh = True
            self.title = self.translate_service.get_translation('manageTasksForGroup') + task.name
            return
        task_name = task.name
        task_time = task.duration
        task_position = task.position
        if task.task_type == TaskTypeEnum.COMMAND.value:
            task_command = task.value
            task_title = None
            task_desc = None
            task_url = None
        elif task.task_type == TaskTypeEnum.URL.value:
            task_command = None
            task_title = None
            task_desc = None
            task_url = task.value
        else:
            task_command = None
            task_title = task.value['title']
            task_desc = task.value['description']
            task_url = None

        add_task_view = AddTaskView(self.translate_service, editing=True, task_name=task_name, task_time=task_time,
                                    task_id=task.id, task_title=task_title, task_desc=task_desc,
                                    task_command=task_command,
                                    task_url=task_url, position=task_position, group=self.active_group)
        add_task_view.add(False, self.suite)
        self.refresh = True

    def delete_task(self, task: Task):
        self.deleting_task = task
        self.delete_dialog.info = self.translate_service.get_translation('task') + ': ' + task.name
        self.delete_dialog.is_open = True

    def delete_action(self):
        self.psy_test_pro_config.delete_task(self.suite, self.deleting_task.id, self.active_group)
        self.deleting_task = None
        self.delete_dialog.is_open = False
        self.refresh = True

    def add_task(self):
        add_task_view = AddTaskView(self.translate_service, group=self.active_group)
        add_task_view.add(False, self.suite)
        self.refresh = True

    def import_task(self, suite_name: str, show_preview: bool):
        try:
            if sys.platform == "darwin":
                filepath = tk.filedialog.askopenfilename(initialdir=get_resource_path('./'),
                                                         title=self.translate_service.get_translation('selectFile'))
            else:
                filepath = tk.filedialog.askopenfilename(
                    initialdir=get_resource_path('./'),
                    title=self.translate_service.get_translation('selectFile'),
                    filetypes=(('Excel files', '*.xlsx;*.xls'), ('CSV files', '*.csv'), ('All files', '*.*'))
                )
            if filepath:
                import_tasks_service = ImportTasksService(self.translate_service)
                result = import_tasks_service.import_tasks(suite_name, filepath, show_preview, self.active_group)
                self.success_msg = None
                self.error_msg = None
                if result[0]:
                    self.success_msg = self.translate_service.get_translation(result[1])
                else:
                    self.error_msg = self.translate_service.get_translation(result[1])
                    if len(result) == 3:
                        self.error_msg = ' '.join((self.error_msg, result[2]))

        except Exception as e:
            print(f'An error occurred: {e}')

        self.refresh = True

    def download_template(self):
        webbrowser.open('https://github.com/eliasmattern/PsyTestPro/raw/main/information/taskImportTemplate.xlsx')

    def open_creat_group_view(self):
        if self.active_group is None:
            CreateTaskGroupView(self.screen, self.suite, self.translate_service).show()
        else:
            group = self.psy_test_pro_config.load_group(self.suite, self.active_group)
            deleted = CreateTaskGroupView(self.screen, self.suite, self.translate_service, edit=True, group=group).show()
            if deleted:
                self.active_group = None
        self.refresh = True
