import pygame.font

from components import Button
from services import TeststarterConfig


class DataTable():

    def __init__(self, columns, max_rows, start_pos, data=None, max_cell_width=None, actions=[],
                 translate_service=None):
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
        self.table_width, self.table_height, self.row_width, self.row_height, self.header_heigth = self.get_table_proportions()
        self.event_areas = {}
        self.actions = actions
        self.action_data = None
        self.translate_service = translate_service

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
        split_data = self.get_split_data()
        table_height = row_height * (len(split_data[self.page]))
        table_width = width + max_header_width * len(self.columns)

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
        table_height += header_height + row_height
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

    def get_split_data(self):
        result = [self.data[i:i + self.max_rows] for i in range(0, len(self.data), self.max_rows)]
        return [sublist for sublist in result if sublist]

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
        if increment:
            self.page = (self.page + 1) % len(data)
        else:
            self.page = (self.page - 1) if self.page > 0 else len(data) - 1

    def handle_events(self, event):
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                print(self.event_areas)
                for key, value in self.event_areas.items():
                    row = int(key.split('-')[0]) + self.page * self.max_rows
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
        split_data = self.get_split_data()
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

        # Render rows
        for count, row in enumerate(split_data[self.page]):
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
                                 self.pos_y + self.margin_top + ((count + 1) * self.row_height + self.header_heigth + (
                                         i * self.font.get_linesize()))))
                self.event_areas[str(count) + '-' + str(index)] = pygame.Rect(self.pos_x + index * self.row_width,
                                                                              self.pos_y + (
                                                                                      count + 1) * self.row_height + self.header_heigth,
                                                                              self.row_width, self.row_height)
                print(count)
                pygame.draw.line(screen, self.grid_color,
                                 (self.pos_x,
                                  self.pos_y + self.row_height * (count + 1) + self.row_height + self.header_heigth),
                                 (self.pos_x + self.table_width,
                                  self.pos_y + self.row_height * (count + 1) + self.row_height + self.header_heigth))

        for count in range(len(self.columns) + 1):
            pygame.draw.line(screen, self.grid_color, (self.pos_x + count * self.row_width, self.pos_y),
                             (self.pos_x + count * self.row_width,
                              self.pos_y + self.row_height * (len(split_data[self.page]) + 1)))

        if len(split_data) > 1:
            self.buttons = self.create_page_button(split_data)
            if self.buttons is not None:
                page_number_surface = self.font.render(str(self.page + 1) + '/' + str(len(split_data)),
                                                       True,
                                                       self.primary_color)
                screen.blit(page_number_surface, (
                    self.pos_x + (((self.table_width + (len(self.columns) * self.margin_left)) // 100) * 50) - 20,
                    self.table_height + self.row_height + 60))
                for button in self.buttons.values():
                    button.draw(screen)
