import pygame.font
from services import TeststarterConfig


class DataTable():

    def __init__(self, columns, max_rows, start_pos, data=None, max_cell_width=None):
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
        self.max_cell_width = max_cell_width
        self.grid_color = pygame.Color(self.settings['gridColor'])
        self.table_width, self.table_height, self.row_width, self.row_height = self.get_table_proportions()


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
        table_height = row_height * (len(self.data) + 1)
        table_width = width + max_header_width * len(self.columns)
        return table_width, table_height, row_width, row_height

    def handle_events(self):
        pass

    def draw(self, screen):
        # Render headers
        for index, header in enumerate(self.columns):
            header_surface = self.header_font.render(
                header, True, self.grid_color
            )
            word_to_split = 1
            final_header = header
            header_copy = header
            if ' ' in header:
                while self.font.size(header_copy)[0] > self.max_cell_width:
                    split_text = header.rsplit(' ', word_to_split)
                    header_copy = split_text[0]
                    word_to_split += 1
                    final_header = ''.join('\\n', split_text)
            screen.blit(header_surface,
                        (self.pos_x + self.margin_left + index * self.row_width, self.pos_y + self.margin_top))
            pygame.draw.line(screen, self.grid_color,
                             (self.pos_x, self.pos_y),
                             (self.pos_x + self.table_width, self.pos_y))
            pygame.draw.line(screen, self.grid_color,
                             (self.pos_x, self.pos_y + self.row_height),
                             (self.pos_x + self.table_width, self.pos_y + self.row_height))

        # Render rows
        for count, row in enumerate(self.data):
            for index, cell in enumerate(row):
                if index >= len(self.columns):
                    continue
                cell_surface = self.font.render(
                    cell, True, self.grid_color
                )
                screen.blit(cell_surface,
                            (self.pos_x + self.margin_left + index * self.row_width,
                             self.pos_y + self.margin_top + ((count + 1) * self.row_height)))
                pygame.draw.line(screen, self.grid_color,
                                 (self.pos_x, self.pos_y + self.row_height * (count + 1) + self.row_height),
                                 (self.pos_x + self.table_width,
                                  self.pos_y + self.row_height * (count + 1) + self.row_height))

        for count in range(len(self.columns) + 1):
            pygame.draw.line(screen, self.grid_color, (self.pos_x + count * self.row_width, self.pos_y),
                             (self.pos_x + count * self.row_width, self.pos_y + self.table_height))
