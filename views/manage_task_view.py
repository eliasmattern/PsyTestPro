import sys

import pygame

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
        self.tasks: list[dict[str, any]] = []
        self.rects = []
        self.buttons: dict[str, Button] = {}
        self.input_boxes: dict[str, InputBox] = {}
        self.refresh = False
        self.experiment = ''
        self.page = 0
        self.font = pygame.font.Font(None, 24)
        self.task_length = 0

    def display(self, experiment_name: str):
        self.experiment = experiment_name
        tasks = self.psy_test_pro_config.load_task_of_experiment(experiment_name)
        sorted_tasks = sorted(tasks.items(), key=lambda item: item[1]['position'])
        current_tasks = {k: v for k, v in sorted_tasks}
        self.task_length = len(current_tasks)
        current_tasks = self.split_dict(current_tasks, 24)
        self.tasks = current_tasks
        self.create_buttons()
        while self.is_running:
            if self.refresh:
                self.refresh = False
                tasks = self.psy_test_pro_config.load_task_of_experiment(experiment_name)
                sorted_tasks = sorted(tasks.items(), key=lambda item: item[1]['position'])
                current_tasks = {k: v for k, v in sorted_tasks}
                self.task_length = len(current_tasks)
                current_tasks = self.split_dict(current_tasks, 24)
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

        page_text = f'{self.page + 1}/{len(self.tasks)}'
        page_surface = self.font.render(page_text, True, self.primary_color)
        page_rect = page_surface.get_rect()
        page_rect.center = (self.screen.get_width() / 2, self.screen.get_height() / 8 + 8 * 80 + 12.5)
        self.screen.blit(page_surface, page_rect)
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
        for task, details in self.tasks[self.page].items():
            task_x, task_y = x + column * column_spacing, y + row * row_spacing
            button = Button(
                task_x + 25,
                task_y,
                200,
                40,
                task.replace('_', ' '),
                lambda t=task, d=details: self.edit_task(t, d)
            )
            input_box = InputBox(task_x - 125, task_y, 40, 40, '', initial_text=str(details['position']),
                                 is_numeric=True, icon=False, minVal=1, maxVal=self.task_length,
                                 on_deselect=lambda pos=details['position'], t=task, r=row: self.rearrange(str(pos),
                                                                                                           t + str(r),
                                                                                                           t))
            rect = pygame.Rect(task_x - 165, task_y - 10, 330, 60)

            self.buttons[task + str(row)] = button
            self.input_boxes[task + str(row)] = input_box
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
        self.buttons['left_button'] = left_button
        self.buttons['right_button'] = right_button

    def rearrange(self, old_pos, input_name, task_name):
        if old_pos == self.input_boxes[input_name].text:
            return
        if self.input_boxes[input_name].text == '':
            self.input_boxes[input_name].text = old_pos
            return
        tasks = {}
        for task in self.tasks:
            tasks.update(task)
        new_pos = int(self.input_boxes[input_name].text)
        current_position = int(old_pos)
        for key, value in tasks.items():
            if key != task_name:
                if current_position < new_pos:
                    if current_position < value['position'] <= new_pos:
                        tasks[key]['position'] -= 1
                else:
                    if new_pos <= value['position'] < current_position:
                        tasks[key]['position'] += 1

        tasks[task_name]['position'] = new_pos
        self.psy_test_pro_config.save_task_list(self.experiment, tasks)
        self.refresh = True

    def back(self):
        self.is_running = False

    def split_dict(self, input_dict: dict, chunk_size: int):
        dict_list = [{}]
        current_dict = 0

        for key, value in input_dict.items():
            dict_list[current_dict][key] = value
            if len(dict_list[current_dict]) >= chunk_size:
                dict_list.append({})
                current_dict += 1

        return dict_list

    def page_update(self, increment: bool, splitted_tasks: list):
        if increment:
            self.page = (self.page + 1) % len(splitted_tasks)
        else:
            self.page = (self.page - 1) if self.page > 0 else len(splitted_tasks) - 1
        self.refresh = True

    def edit_task(self, task, details):
        task_name = task.replace('_', ' ')
        task_time = details['time']
        task_position = details['position']
        if details['type'] == 'command':
            task_command = details['value']
            task_title = None
            task_desc = None
        else:
            task_command = None
            task_title = details['value']['title']
            task_desc = details['value']['description']

        add_task_view = AddTaskView(self.translate_service, editing=True, task_name=task_name, task_time=task_time,
                                    task_title=task_title, task_desc=task_desc, task_command=task_command,
                                    position=task_position)
        add_task_view.add(False, self.experiment)
        self.refresh = True
