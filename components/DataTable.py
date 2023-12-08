import pygame.font
import math

from components import Button
from services import TeststarterConfig


class DataTable:

    def __init__(self, columns, max_rows, start_pos, data=None, max_cell_width=None, actions=[], max_height=None,
                 translate_service=None):
        self.split_data = None
        self.buttons = None
        if data is None:
            data = [[]]
        self.data = data
        self.columns = columns
        self.max_rows = max_rows
        self.pos_x, self.pos_y = start_pos
        self.font = pygame.font.Font(None, 24)
        self.header_font = pygame.font.Font(None, 30)
        self.teststarter_config = TeststarterConfig()
        self.settings = self.teststarter_config.get_settings()
        self.margin_left = 10
        self.margin_top = 5
        self.max_cell_width = max_cell_width - 10 if max_cell_width else None
        self.page = 0
        self.grid_color = pygame.Color(self.settings['gridColor'])
        self.primary_color = pygame.Color(self.settings['gridColor'])
        self.max_height = max_height
        self.row_height = 50
        self.translate_service = translate_service
        self.event_areas = {}
        self.actions = actions
        self.action_data = None
        self.entries_per_page = []
        if len(self.data) > 0:
            self.table_width, self.table_height, self.row_width, self.row_height, self.header_heigth = self.get_table_proportions()

    def set_action_data(self, data):
        self.action_data = data

    def get_table_proportions(self):
        width = 0
        table_height = 0
        max_header_width = 0
        row_height = 50
        for header in self.columns:
            header_width = 2 * self.margin_left + self.header_font.size(header)[0]
            if header_width > max_header_width:
                max_header_width = header_width
            width += 2 * self.margin_left
        if self.max_cell_width != None and max_header_width > self.max_cell_width:
            max_header_width = self.max_cell_width
        row_width = max_header_width + 2 * self.margin_left
        max_row_height = self.get_max_row_height(row_width)
        header_height = 0
        for header in self.columns:
            word_to_split = 1
            final_header = header
            header_copy = header

            if ' ' in header and row_width != None:
                headers = []
                split_text = None
                while self.header_font.size(header_copy)[0] + self.margin_left > row_width and ' ' in header_copy:
                    split_text = header.rsplit(' ', word_to_split)
                    header_copy = split_text[0]
                    word_to_split += 1
                    if self.header_font.size(split_text[1])[0] > row_width:
                        split_text[1] = self.get_fromatted_text(split_text[1], row_width, self.header_font)
                    if len(headers) > 0 and self.header_font.size(split_text[1] + ' ' + headers[-1])[
                        0] + self.margin_left < row_width:
                        split_text[1] = split_text[1] + ' ' + headers[-1]
                        del headers[len(headers) - 1]
                    headers.append(split_text[1])
                if split_text:
                    first_word = self.get_fromatted_text(split_text[0], row_width, self.header_font)
                else:
                    first_word = header
                final_header = '\\n'.join(map(str, [first_word, *headers]))
            elif row_width is not None:
                final_header = self.get_fromatted_text(header, row_width, self.header_font)
            split_header = final_header.split('\\n')
            if row_height < self.header_font.get_height() * len(split_header) > header_height:
                header_height = self.header_font.get_height() * (len(split_header) - 1)

        self.get_split_data(row_height, max_row_height, header_height)
        table_height = row_height * (len(self.split_data[self.page]))
        table_width = width + max_header_width * len(self.columns)

        table_height += header_height + max_row_height
        if self.max_height is not None and table_height > self.max_height:
            table_height = self.max_height
        return table_width, table_height, row_width, row_height, header_height

    def get_fromatted_text(self, text, max_width, font):
        texts = []
        index = 0
        while font.size(text)[0] > max_width - self.margin_left:
            if font.size(text[:index])[0] >= max_width - self.margin_left:
                texts.append(text[:index - 2])
                text = text[index - 2:]
                index = 0
            else:
                index += 1
            if index > len(text):
                break
        return '\\n'.join(map(str, [*texts, text]))

    def get_split_data(self, row_height, max_row_height, header_height=None):
        if not header_height is None:
            self.header_heigth = header_height

        max_fields = self.max_rows
        if max_row_height > self.max_height:
            max_fields = math.floor((self.max_height - row_height) / row_height)
            if max_fields <= 1:
                max_fields = 1
                self.table_height = row_height * 2
            self.max_rows = max_fields
        result = [self.data[i:i + max_fields] for i in range(0, len(self.data), max_fields)]
        trimmed_data = [sublist for sublist in result if sublist]
        max_fields_old = max_fields
        val = 0
        old_size = len(trimmed_data)
        size = 0
        while size != old_size:
            old_size = len(trimmed_data)
            for index, page in zip(range(len(trimmed_data)), trimmed_data):

                max_fields = len(page)
                val += 1
                editing = True
                while editing:
                    total_height = 0
                    for row in page:
                        total_height += self.get_row_height(row)
                    if max_fields <= 1:
                        max_fields = 1
                        editing = False
                    elif total_height + self.header_heigth > self.max_height - 120:
                        max_fields -= 1
                        last = page[- 1]
                        del trimmed_data[index][- 1]
                        if index + 1 < len(trimmed_data):
                            trimmed_data[index + 1].insert(0, last)
                        else:
                            trimmed_data.append([last])
                    else:
                        editing = False
                        max_fields = max_fields_old
            size = len(trimmed_data)
        for page in trimmed_data:
            self.entries_per_page.append(len(page))
        self.split_data = trimmed_data

    def create_page_button(self, data):
        buttons = {}
        left_button = Button(
            self.pos_x + (((self.table_width + (len(self.columns) * self.margin_left)) // 100) * 37.5) - 20,
            self.table_height + self.row_height + 40,
            40,
            40, '<',
            lambda: self.page_update(False, data),
            border_radius=90)
        right_button = Button(
            self.pos_x + (((self.table_width + (len(self.columns) * self.margin_left)) // 100) * 67.5) - 20,
            self.table_height + self.row_height + 40,
            40,
            40, '>',
            lambda: self.page_update(True, data),
            border_radius=90)
        buttons['left_button'] = left_button
        buttons['right_button'] = right_button
        return buttons

    def page_update(self, increment, data):
        self.event_areas = {}
        if increment:
            self.page = (self.page + 1) % len(data)
        else:
            self.page = (self.page - 1) if self.page > 0 else len(data) - 1

    def get_row_height(self, row, row_width=None):
        if row_width:
            self.row_width = row_width
        row_height = self.row_height
        for cell in row:
            if isinstance(cell, dict):
                if 'key' in cell.keys() and self.translate_service is not None:
                    cell = self.translate_service.get_translation(cell['key'])
                else:
                    cell = cell['value']

            cell_copy = cell
            if ' ' in cell and self.row_width != None:
                cells = []
                split_text = None
                word_to_split = 1
                while self.font.size(cell_copy)[
                    0] > self.row_width - self.margin_left and ' ' in cell_copy:

                    split_text = cell.rsplit(' ', word_to_split)
                    cell_copy = split_text[0]
                    word_to_split += 1
                    if self.font.size(split_text[1])[0] + self.margin_left > self.row_width:
                        split_text[1] = self.get_fromatted_text(split_text[1], self.row_width, self.font)
                    if len(cells) > 0 and self.font.size(split_text[1] + ' ' + cells[-1])[
                        0] + self.margin_left < self.row_width:
                        split_text[1] = split_text[1] + ' ' + cells[-1]
                        del cells[len(cells) - 1]
                    cells.append(split_text[1])
                if split_text:
                    first_word = self.get_fromatted_text(split_text[0], self.row_width, self.font)
                else:
                    first_word = cell
                cells.reverse()
                final_cells = '\\n'.join(map(str, [first_word, *cells]))
            else:
                final_cells = self.get_fromatted_text(cell, self.row_width, self.font)
            split_cell = final_cells.split('\\n')

            text_height = len(split_cell) if len(split_cell) > 2 else 1
            if (text_height - 1) * row_height > self.row_height:
                row_height = row_height + (text_height - 1) * self.font.get_height()
        return row_height

    def get_max_row_height(self, row_width):
        max_height = 0
        for row in self.data:
            max_height += self.get_row_height(row, row_width)
        return max_height

    def handle_events(self, event):
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                for key, value in self.event_areas.items():
                    get_past_areas = self.entries_per_page[0:self.page]
                    entries = 0
                    for num in get_past_areas:
                        entries += num
                    row = int(key.split('-')[0]) + entries
                    value_index = int(key.split('-')[1])
                    if row >= len(self.data):
                        continue
                    self.action_data = self.data[row][value_index]
                    action_data_copy = self.action_data

                    if value.collidepoint(event.pos):
                        if len(self.actions) - 1 >= value_index and self.actions[value_index]:
                            self.actions[value_index]()

                            if self.action_data != action_data_copy:
                                self.data[row][value_index] = self.action_data
        if self.buttons is not None:
            for button in self.buttons.values():
                button.handle_event(event)

    def draw(self, screen):
        if len(self.data) > 0:
            # Render headers
            for index, header in enumerate(self.columns):
                word_to_split = 1
                final_header = header
                header_copy = header
                if ' ' in header and self.row_width != None:
                    headers = []
                    split_text = None
                    while self.header_font.size(header_copy)[0] > self.row_width - self.margin_left and ' ' in header_copy:
                        split_text = header.rsplit(' ', word_to_split)
                        header_copy = split_text[0]
                        word_to_split += 1
                        if self.header_font.size(split_text[1])[0] + self.margin_left > self.row_width:
                            split_text[1] = self.get_fromatted_text(split_text[1], self.row_width, self.header_font)
                        if len(headers) > 0 and self.header_font.size(split_text[1] + ' ' + headers[-1])[
                            0] + self.margin_left < self.row_width:
                            split_text[1] = split_text[1] + ' ' + headers[-1]
                            del headers[len(headers) - 1]
                        headers.append(split_text[1])
                    if split_text:
                        first_word = self.get_fromatted_text(split_text[0], self.row_width, self.header_font)
                    else:
                        first_word = header
                    headers.reverse()
                    final_header = '\\n'.join(map(str, [first_word, *headers]))
                elif self.row_width != None:
                    final_header = self.get_fromatted_text(header, self.row_width, self.header_font)
                split_header = final_header.split('\\n')

                header_surfaces = []
                for header_text in split_header:
                    header_surfaces.append(self.header_font.render(
                        header_text, True, self.primary_color
                    ))
                for i, surface in enumerate(header_surfaces):
                    screen.blit(surface,
                                (self.pos_x + self.margin_left + index * self.row_width,
                                 self.pos_y + self.margin_top + (i * self.header_font.get_linesize())))
                pygame.draw.line(screen, self.grid_color,
                                 (self.pos_x, self.pos_y),
                                 (self.pos_x + self.table_width, self.pos_y))
                pygame.draw.line(screen, self.grid_color,
                                 (self.pos_x, self.pos_y + self.row_height + self.header_heigth),
                                 (self.pos_x + self.table_width, self.pos_y + self.row_height + self.header_heigth))

            cell_y = self.pos_y + self.header_heigth

            # Render rows
            for count, row in enumerate(self.split_data[self.page]):
                row_height = self.get_row_height(row)
                cell_y += self.get_row_height(row)
                for index, cell in enumerate(row):
                    word_to_split = 1
                    if index >= len(self.columns):
                        continue

                    color = self.primary_color

                    if isinstance(cell, dict):
                        if 'color' in cell.keys():
                            color = cell['color']
                        if 'key' in cell.keys() and self.translate_service is not None:
                            cell = self.translate_service.get_translation(cell['key'])
                        else:
                            cell = cell['value']
                    cell_copy = cell
                    if ' ' in cell and self.row_width != None:
                        cells = []
                        split_text = None
                        while self.font.size(cell_copy)[
                            0] > self.row_width - self.margin_left and ' ' in cell_copy:

                            split_text = cell.rsplit(' ', word_to_split)
                            cell_copy = split_text[0]
                            word_to_split += 1
                            if self.font.size(split_text[1])[0] + self.margin_left > self.row_width:
                                split_text[1] = self.get_fromatted_text(split_text[1], self.row_width, self.font)
                            if len(cells) > 0 and self.font.size(split_text[1] + ' ' + cells[-1])[
                                0] + self.margin_left < self.row_width:
                                split_text[1] = split_text[1] + ' ' + cells[-1]
                                del cells[len(cells) - 1]
                            cells.append(split_text[1])
                        if split_text:
                            first_word = self.get_fromatted_text(split_text[0], self.row_width, self.font)
                        else:
                            first_word = cell
                        cells.reverse()
                        final_cells = '\\n'.join(map(str, [first_word, *cells]))
                    elif self.row_width != None:
                        final_cells = self.get_fromatted_text(cell, self.row_width, self.font)
                    split_cell = final_cells.split('\\n')
                    cell_surfaces = []
                    for cell_text in split_cell:
                        cell_surfaces.append(self.font.render(
                            cell_text, True, color
                        ))

                    for i, surface in enumerate(cell_surfaces):
                        screen.blit(surface,
                                    (self.pos_x + self.margin_left + index * self.row_width,
                                     self.margin_top + (cell_y - (row_height - self.row_height) + (
                                             i * self.font.get_linesize()))))
                    self.event_areas[str(count) + '-' + str(index)] = pygame.Rect(self.pos_x + index * self.row_width,
                                                                                  (cell_y - (row_height - self.row_height)),
                                                                                  self.row_width, row_height)
                    pygame.draw.line(screen, self.grid_color,
                                     (self.pos_x,
                                      cell_y + self.row_height),
                                     (self.pos_x + self.table_width,
                                      cell_y + self.row_height))

            for count in range(len(self.columns) + 1):
                pygame.draw.line(screen, self.grid_color, (self.pos_x + count * self.row_width, self.pos_y),
                                 (self.pos_x + count * self.row_width,
                                  cell_y + self.row_height))
            if len(self.split_data) > 1:
                self.buttons = self.create_page_button(self.split_data)
                if self.buttons is not None:
                    page_number_surface = self.font.render(str(self.page + 1) + '/' + str(len(self.split_data)),
                                                           True,
                                                           self.primary_color)
                    screen.blit(page_number_surface, (
                        self.pos_x + (((self.table_width + (len(self.columns) * self.margin_left)) // 100) * 50) - 20,
                        self.table_height + self.row_height + 60))
                    for button in self.buttons.values():
                        button.draw(screen)
        else:
            if self.translate_service:
                error_msg = self.translate_service.get_translation('noData')
            else:
                error_msg = "No Data"
            error_surface = self.font.render(error_msg, True, self.primary_color)
            error_rect = error_surface.get_rect()
            screen.blit(error_surface, (self.pos_x, self.pos_y))
