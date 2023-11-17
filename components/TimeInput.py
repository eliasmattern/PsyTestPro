import tkinter as tk
import pygame
from pygame.locals import *
from tktimepicker import AnalogPicker, AnalogThemes
from tktimepicker import constants


def create_time_picker(hour, minute, translate_service):
    def save_time():
        root.quit()  # Close the window
        root.destroy()

    def close_window(event):
        root.quit()
        root.destroy()

    root = tk.Tk()

    screenIndex = pygame.display.get_desktop_sizes().index(pygame.display.get_surface().get_size())
    count = 0
    posX, posY = pygame.mouse.get_pos()
    for display in pygame.display.get_desktop_sizes():
        if count == screenIndex:
            break
        posX += display[0]
        count += 1
    print(posY)
    root.geometry('+' + str(posX) + '+' + str(posY))
    root.configure(background='black')

    time_picker = AnalogPicker(root, type=constants.HOURS24)
    time_picker.setHours(hour)
    time_picker.setMinutes(minute)

    time_picker.hours_picker.setHours(int(hour))
    time_picker.minutes_picker.setMinutes(int(minute))

    time_picker.pack(expand=True, fill='both')

    theme = AnalogThemes(time_picker)
    theme.setDracula()

    save_button = tk.Button(root, text=translate_service.get_translation('saveTime'), command=save_time)
    save_button.pack()

    root.bind('<Escape>', close_window)  # Bind the Escape key to the close_window function

    root.mainloop()
    return time_picker


class TimeInput:
    def __init__(self, x, y, width, height, translation_key, translate_service, info='', initial_time=''):
        self.translate_service = translate_service
        self.rect = pygame.Rect(x - width // 2, y, width, height)
        self.color = pygame.Color('gray')
        self.active_color = pygame.Color('gray')
        self.text_color = pygame.Color('black')
        self.label_color = pygame.Color('gray')
        self.active_text_color = pygame.Color('black')
        self.time = initial_time
        self.font = pygame.font.SysFont('Arial', 24)
        self.translation_key = translation_key
        self.info = info
        self.label = self.font.render(self.translate_service.get_translation(self.translation_key) + ' ' + self.info,
                                      True, self.label_color)
        self.is_selected = False
        self.cursor_visible = False
        self.cursor_timer = 0

    def handle_event(self, event):
        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                splitted_time = self.time.split(':') if self.time else '00:00'
                time_picker = create_time_picker(splitted_time[0], splitted_time[1], self.translate_service)
                self.time = str(time_picker.time()[0]).rjust(2, '0') + ':' + str(time_picker.time()[1]).rjust(2, '0')

    def update_text(self):
        self.label = self.font.render(self.translate_service.get_translation(self.translation_key) + ' ' + self.info,
                                      True, self.label_color)

    def draw(self, screen):
        pygame.draw.rect(screen, self.active_color if self.is_selected else self.color, self.rect)
        input_text = self.time
        text_surface = self.font.render(input_text, True,
                                        self.active_text_color if self.is_selected else self.text_color)

        screen.blit(text_surface, (self.rect.x + 5, self.rect.y + 5))
        screen.blit(self.label, (self.rect.x - self.label.get_width() - 10, self.rect.y + 5))
