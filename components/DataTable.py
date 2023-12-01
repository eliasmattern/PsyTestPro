import pygame.font
from services import TeststarterConfig


class DataTable():

    def __init__(self, columns, max_rows, start_pos, data=None, max_cell_width=None, actions=[], translate_service=None):
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
        self.max_cell_width = max_cell_width - 10
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
        table_height = row_height * (len(self.data))
        table_width = width + max_header_width * len(self.columns)

        header_height = 0
        for header in self.columns:
            word_to_split = 1
            final_header = header
            header_copy = header

            if ' ' in header and self.max_cell_width != None:
                headers = []
                split_text = None
                while self.font.size(header_copy)[0] + self.margin_left > self.max_cell_width and ' ' in header_copy:
                    split_text = header.rsplit(' ', word_to_split)
                    header_copy = split_text[0]
                    word_to_split += 1
                    if self.font.size(split_text[1])[0] > self.max_cell_width:
                        split_text[1] = self.get_fromatted_text(split_text[1], self.max_cell_width)
                    if len(headers) > 0 and self.font.size(split_text[1] + ' ' + headers[-1])[
                        0] + self.margin_left < self.max_cell_width:
                        split_text[1] = split_text[1] + ' ' + headers[-1]
                        del headers[len(headers) - 1]
                    headers.append(split_text[1])
                if split_text:
                    first_word = self.get_fromatted_text(split_text[0], self.max_cell_width)
                else:
                    first_word = header
                final_header = '\\n'.join(map(str, [first_word, *headers]))
            elif self.max_cell_width is not None:
                final_header = self.get_fromatted_text(header, self.max_cell_width)
            split_header = final_header.split('\\n')
            if row_height < self.font.get_height() * len(split_header) > header_height:
                header_height = self.font.get_height() * (len(split_header) - 1)
        table_height += header_height
        return table_width, table_height, row_width, row_height, header_height

    def get_fromatted_text(self, text, max_width):
        texts = []
        index = 0
        while self.font.size(text)[0] > max_width - self.margin_left:
            if self.font.size(text[:index])[0] >= max_width - self.margin_left:
                texts.append(text[:index - 2])
                text = text[index - 2:]
                index = 0
            else:
                index += 1
            if index > len(text):
                break
        return '\\n'.join(map(str, [*texts, text]))

    def handle_events(self, event):
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                for key, value in self.event_areas.items():
                    row = int(key.split('-')[0])
                    value_index = int(key.split('-')[1])
                    self.action_data = self.data[row][value_index]
                    action_data_copy = self.action_data

                    if value.collidepoint(event.pos):
                        if len(self.actions) - 1 >= value_index and self.actions[value_index]:
                            self.actions[value_index]()

                            if self.action_data != action_data_copy:
                                self.data[row][value_index] = self.action_data

    def draw(self, screen):
        # Render headers
        for index, header in enumerate(self.columns):
            word_to_split = 1
            final_header = header
            header_copy = header
            if ' ' in header and self.max_cell_width != None:
                headers = []
                split_text = None
                while self.font.size(header_copy)[0] > self.max_cell_width - self.margin_left and ' ' in header_copy:
                    split_text = header.rsplit(' ', word_to_split)
                    header_copy = split_text[0]
                    word_to_split += 1
                    if self.font.size(split_text[1])[0] + self.margin_left > self.max_cell_width:
                        split_text[1] = self.get_fromatted_text(split_text[1], self.max_cell_width)
                    if len(headers) > 0 and self.font.size(split_text[1] + ' ' + headers[-1])[
                        0] + self.margin_left < self.max_cell_width:
                        split_text[1] = split_text[1] + ' ' + headers[-1]
                        del headers[len(headers) - 1]
                    headers.append(split_text[1])
                if split_text:
                    first_word = self.get_fromatted_text(split_text[0], self.max_cell_width)
                else:
                    first_word = header
                headers.reverse()
                final_header = '\\n'.join(map(str, [first_word, *headers]))
            elif self.max_cell_width != None:
                final_header = self.get_fromatted_text(header, self.max_cell_width)
            split_header = final_header.split('\\n')

            header_surfaces = []
            for header_text in split_header:
                header_surfaces.append(self.header_font.render(
                    header_text, True, self.primary_color
                ))
            for i, surface in enumerate(header_surfaces):
                screen.blit(surface,
                            (self.pos_x + self.margin_left + index * self.row_width,
                             self.pos_y + self.margin_top + (i * self.font.get_linesize())))
            pygame.draw.line(screen, self.grid_color,
                             (self.pos_x, self.pos_y),
                             (self.pos_x + self.table_width, self.pos_y))
            pygame.draw.line(screen, self.grid_color,
                             (self.pos_x, self.pos_y + self.row_height + self.header_heigth),
                             (self.pos_x + self.table_width, self.pos_y + self.row_height + self.header_heigth))

        # Render rows
        for count, row in enumerate(self.data):
            for index, cell in enumerate(row):
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


                cell_surface = self.font.render(
                    str(cell), True, color
                )
                screen.blit(cell_surface,
                            (self.pos_x + self.margin_left + index * self.row_width,
                             self.pos_y + self.margin_top + ((count + 1) * self.row_height + self.header_heigth)))
                self.event_areas[str(count) + '-' + str(index)] = pygame.Rect(self.pos_x + index * self.row_width,
                                                                              self.pos_y + (
                                                                                          count + 1) * self.row_height + self.header_heigth,
                                                                              self.row_width, self.row_height)
                pygame.draw.line(screen, self.grid_color,
                                 (self.pos_x,
                                  self.pos_y + self.row_height * (count + 1) + self.row_height + self.header_heigth),
                                 (self.pos_x + self.table_width,
                                  self.pos_y + self.row_height * (count + 1) + self.row_height + self.header_heigth))

        for count in range(len(self.columns) + 1):
            pygame.draw.line(screen, self.grid_color, (self.pos_x + count * self.row_width, self.pos_y),
                             (self.pos_x + count * self.row_width, self.pos_y + self.table_height + self.row_height))
