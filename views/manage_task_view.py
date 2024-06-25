import sys

import pygame

from app_types import Task, TaskTypeEnum
from components import Button, InputBox
from services import PsyTestProConfig, TranslateService
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
        self.tasks: list[list[Task]] = []
        self.rects = []
        self.buttons: dict[str, Button] = {}
        self.input_boxes: dict[str, InputBox] = {}
        self.refresh = False
        self.suite = ''
        self.formatted_suite = ''
        self.page = 0
        self.font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 30)
        self.task_length = 0

    def display(self, suite_name: str):
        self.suite = suite_name
        self.formatted_suite = suite_name.replace('_schedule', '').replace('_list', '').replace('_', ' ')
        tasks: list[Task] = self.psy_test_pro_config.load_task_of_suite(suite_name)
        sorted_tasks = sorted(tasks, key=lambda task: task.position)
        self.task_length = len(sorted_tasks)
        current_tasks = list(self.split_list(sorted_tasks, 24))
        self.tasks = current_tasks
        self.create_buttons()
        while self.is_running:
            if self.refresh:
                self.refresh = False
                tasks = self.psy_test_pro_config.load_task_of_suite(suite_name)
                sorted_tasks = sorted(tasks, key=lambda task: task.position)
                self.task_length = len(sorted_tasks)
                current_tasks = list(self.split_list(sorted_tasks, 24))
                self.tasks = current_tasks
                self.create_buttons()
            self.draw()
            self.handle_events()
        self.is_running = True

    def draw(self):
        self.screen.fill(self.background_color)
        for button in self.buttons.values():
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

        title = self.translate_service.get_translation('manageTasksFor') + self.formatted_suite
        title_surface = self.title_font.render(title, True, self.primary_color)
        title_rect = title_surface.get_rect()
        title_rect.center = (
            self.screen.get_width() / 2, self.screen.get_height() / 8 - (self.title_font.get_height() * 3))

        self.screen.blit(title_surface, title_rect)
        pygame.display.flip()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            for input_box in self.input_boxes.values():
                input_box.handle_event(event)
            for button in self.buttons.values():
                button.handle_event(event)

    def create_buttons(self):
        self.buttons: dict[str, Button] = {}
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
                button = Button(
                    task_x + 25,
                    task_y,
                    200,
                    40,
                    task.name.replace('_', ' '),
                    lambda t=task: self.edit_task(t)
                )
                input_box = InputBox(task_x - 125, task_y, 40, 40, '', initial_text=str(task.position),
                                     is_numeric=True, icon=False, minVal=1, maxVal=self.task_length,
                                     on_deselect=lambda pos=task.position, t=task.name, r=row: self.rearrange(str(pos),
                                                                                                               t + str(
                                                                                                                   r),
                                                                                                               t))
                rect = pygame.Rect(task_x - 165, task_y - 10, 330, 60)

                self.buttons[task.name + str(row)] = button
                self.input_boxes[task.name + str(row)] = input_box
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
            self.screen.get_width() / 2,
            self.screen.get_height() - 60,
            150,
            40,
            'back',
            self.back,
            self.translate_service
        )
        self.buttons['back_button'] = back_button
        if len(self.tasks) > 1:
            self.buttons['left_button'] = left_button
            self.buttons['right_button'] = right_button

    def rearrange(self, old_pos, input_name, task_name):
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
            if task.name != task_name:
                if current_position < new_pos:
                    if current_position < task.position <= new_pos:
                        task.position -= 1
                else:
                    if new_pos <= task.position < current_position:
                        task.position += 1
            else:
                task.position = new_pos

        self.psy_test_pro_config.save_task_list(self.suite, tasks)
        self.refresh = True

    def back(self):
        self.is_running = False

    def split_list(self, input_list: list, chunk_size: int):
        for i in range(0, len(input_list), chunk_size):
            yield input_list[i:i + chunk_size]

    def page_update(self, increment: bool, splitted_tasks: list):
        if increment:
            self.page = (self.page + 1) % len(splitted_tasks)
        else:
            self.page = (self.page - 1) if self.page > 0 else len(splitted_tasks) - 1
        self.refresh = True

    def edit_task(self, task: Task):
        task_name = task.name.replace('_', ' ')
        task_time = task.duration
        task_position = task.position
        if task.task_type == TaskTypeEnum.COMMAND:
            task_command = task.value
            task_title = None
            task_desc = None
            task_url = None
        elif task.task_type == TaskTypeEnum.URL:
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
                                    task_title=task_title, task_desc=task_desc, task_command=task_command,
                                    task_url=task_url, position=task_position)
        add_task_view.add(False, self.suite)
        self.refresh = True
