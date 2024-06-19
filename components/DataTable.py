import math
from typing import Optional

import pygame

from components import Button
from events import LANGUAGE_EVENT
from services import TranslateService, PsyTestProConfig


class ActionRect:
    def __init__(self, x: float, y: float, width: float, heigth: float, column: int, row: int):
        self.rect = pygame.rect.Rect(x, y, width, heigth)
        self.column_index = column
        self.row_index = row


class DataTable:

    def __init__(self, columns: list, start_pos: tuple[float, float], column_width: int, data: Optional[list[list]] = None,
                 actions: Optional[list] = None, max_height: Optional[float] = None, translate_service: Optional[
                TranslateService] = None):
        self.columns = columns
        self.pos_x, self.pos_y = start_pos
        self.actions = actions
        self.max_height = max_height
        self.column_width = column_width
        self.font = pygame.font.Font(None, 28)
        self.column_font = pygame.font.Font(None, 32)
        self.padding = self.font.get_linesize() / 2
        self.row_height = self.padding * 4
        self.translate_service = translate_service
        self.surfaces: list[tuple[pygame.Surface, tuple[float, float]]] = []
        self.lines: list[tuple[tuple[float, float], tuple[float, float]]] = []
        self.buttons: list[Button] = []
        self.psy_test_pro_config = PsyTestProConfig()
        self.settings = self.psy_test_pro_config.get_settings()
        self.grid_color = pygame.Color(self.settings['gridColor'])
        self.primary_color = pygame.Color(self.settings['primaryColor'])
        self.split_data = list(self.split_list(data))
        self.page = 0
        self.data = self.format_data(self.split_data[self.page])
        self.prepare_table()
        self.action_rects: list[ActionRect] = self.get_action_rects()
        self.current_action_rect = None

    def draw(self, screen: pygame.Surface):
        for surface, pos in self.surfaces:
            screen.blit(surface, pos)
        for start_pos, end_pos in self.lines:
            pygame.draw.line(screen, self.grid_color, start_pos, end_pos)

        if len(self.split_data) > 1:
            for button in self.buttons:
                button.draw(screen)
            page_text = f'{self.page + 1}/{len(self.split_data)}'
            surface = self.font.render(page_text, True, self.primary_color)
            screen.blit(surface, (
                self.pos_x + (len(self.columns) * self.column_width / 2) - (self.font.size(page_text)[0] / 2),
                self.max_height + self.padding * 4))

    def handle_event(self, event):
        for button in self.buttons:
            button.handle_event(event)
        if event.type == pygame.MOUSEBUTTONUP:
            try:
                rect = next(
                    action_rect for action_rect in self.action_rects if action_rect.rect.collidepoint(event.pos))
                payload = self.split_data[self.page][rect.row_index][rect.column_index]
                self.current_action_rect = rect
                self.actions[rect.column_index](payload)
            except:
                pass
        elif event.type == LANGUAGE_EVENT:
            self.data = self.format_data(self.split_data[self.page])
            self.prepare_table()

    def prepare_table(self):
        self.surfaces = []
        self.lines = []
        self.buttons = []
        for index, column in enumerate(self.columns):
            label = self.column_font.render(self.translate_service.get_translation(column), False, self.primary_color)
            self.surfaces.append((label,
                                  (self.pos_x + self.column_width * index + self.padding, self.pos_y + self.padding)))

            left_border = ((self.pos_x + self.column_width * index, self.pos_y),
                           (self.pos_x + self.column_width * index, self.pos_y + self.row_height))
            right_border = ((self.pos_x + self.column_width * (index + 1), self.pos_y),
                            (self.pos_x + self.column_width * (index + 1), self.pos_y + self.row_height))
            self.lines.extend([left_border, right_border])

        column_top_line = (self.pos_x, self.pos_y), (self.pos_x + len(self.columns) * self.column_width, self.pos_y)
        column_bottom_line = ((self.pos_x, self.pos_y + self.row_height),
                              (self.pos_x + len(self.columns) * self.column_width, self.pos_y + self.row_height))
        self.lines.extend([column_top_line, column_bottom_line])

        for row_index, row in enumerate(self.data):
            for value_index, value in enumerate(row):
                if isinstance(value, dict):
                    label = self.font.render(self.translate_service.get_translation(value['value']), False,
                                             value['color'])
                else:
                    label = self.font.render(value, False, self.primary_color)
                self.surfaces.append((label, (self.pos_x + self.padding + self.column_width * value_index,
                                              self.pos_y + self.row_height * (row_index + 1) + self.padding)))
                left_border = (
                    (self.pos_x + self.column_width * value_index, self.pos_y + self.row_height * (row_index + 1)),
                    (self.pos_x + self.column_width * value_index,
                     self.pos_y + self.row_height * (row_index + 1) + self.row_height)
                )
                right_border = ((self.pos_x + self.column_width * (value_index + 1),
                                 self.pos_y + self.row_height * (row_index + 1)),
                                (self.pos_x + self.column_width * (value_index + 1),
                                 self.pos_y + self.row_height * (row_index + 1) + self.row_height))

                self.lines.extend([left_border, right_border])
            self.lines.append(((self.pos_x, self.pos_y + self.row_height * (row_index + 1) + self.row_height),
                               (self.pos_x + len(self.columns) * self.column_width,
                                self.pos_y + self.row_height * (row_index + 1) + self.row_height)))

        left_page_button = Button(self.pos_x + (len(self.columns) * self.column_width / 2 - 50),
                                  self.max_height + self.padding * 4,
                                  25, 20, '<', lambda: self.page_update(False, self.split_data), border_radius=90)
        right_page_button = Button(self.pos_x + (len(self.columns) * self.column_width / 2 + 50),
                                   self.max_height + self.padding * 4,
                                   25, 20, '>', lambda: self.page_update(True, self.split_data), border_radius=90)

        self.buttons.extend([left_page_button, right_page_button])

    def format_data(self, data):
        formatted_data = []
        for row in data:
            new_row = []
            for value in row:
                if isinstance(value, dict):
                    while self.font.size(value['value'])[0] > self.column_width - self.padding * 2:
                        value = value['value'][:-4] + '...'
                else:
                    while self.font.size(value)[0] > self.column_width - self.padding * 2:
                        value = value[:-4] + '...'
                new_row.append(value)
            formatted_data.append(new_row)
        return formatted_data

    def split_list(self, input_list: list):
        chunk_size = math.floor(self.max_height / self.row_height) - 2
        for i in range(0, len(input_list), chunk_size):
            yield input_list[i:i + chunk_size]

    def page_update(self, increment: bool, splitted_data: list):
        if increment:
            self.page = (self.page + 1) % len(splitted_data)
        else:
            self.page = (
                (self.page - 1) if self.page > 0 else len(splitted_data) - 1
            )
        self.data = self.format_data(self.split_data[self.page])
        self.prepare_table()
        self.action_rects: list[ActionRect] = self.get_action_rects()

    def get_action_rects(self):
        rects = []
        for row_index in range(len(self.split_data[self.page])):
            for column_index in range(len(self.columns)):
                rects.append(ActionRect(self.pos_x + column_index * self.column_width,
                                        self.pos_y + self.row_height * (row_index + 1), self.column_width,
                                        self.row_height, column_index, row_index))
        return rects

    def update_field(self, new_value):
        if self.current_action_rect:
            self.split_data[self.page][self.current_action_rect.row_index][
                self.current_action_rect.column_index] = new_value
            self.data = self.format_data(self.split_data[self.page])
            self.prepare_table()
            self.current_action_rect = None
            self.action_rects: list[ActionRect] = self.get_action_rects()

    def get_data(self):
        data = []
        for page in self.split_data:
            data.extend(page)
        return data

    def set_data(self, data):
        self.split_data = list(self.split_list(data))
        self.page = 0
        self.data = self.format_data(self.split_data[self.page])
        self.prepare_table()
        self.action_rects: list[ActionRect] = self.get_action_rects()
        self.current_action_rect = None
