import pygame
from pygame.locals import *

class InputBox:
    def __init__(self, x, y, width, height, label, initial_text=""):
        self.rect = pygame.Rect(x - width // 2, y, width, height)
        self.color = pygame.Color("gray")
        self.active_color = pygame.Color("gray")
        self.text_color = pygame.Color("black")
        self.label_color = pygame.Color("gray")
        self.active_text_color = pygame.Color("black")
        self.text = initial_text
        self.font = pygame.font.SysFont("Arial", 24)
        self.label = self.font.render(label, True, self.label_color)
        self.is_selected = False
        self.cursor_visible = False
        self.cursor_timer = 0

    def handle_event(self, event):
        if event.type == MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.is_selected = True
            else:
                self.is_selected = False
        elif event.type == KEYDOWN:
            if self.is_selected:
                if event.key == K_BACKSPACE:
                    self.text = self.text[:-1]
                elif event.key == K_TAB:
                    pass
                else:
                    self.text += event.unicode
                self.cursor_visible = True
                self.cursor_timer = pygame.time.get_ticks() + 500

    def draw(self, screen):
        pygame.draw.rect(screen, self.active_color if self.is_selected else self.color, self.rect)
        text_surface = self.font.render(self.text, True, self.active_text_color if self.is_selected else self.text_color)
        screen.blit(text_surface, (self.rect.x + 5, self.rect.y + 5))
        screen.blit(self.label, (self.rect.x - self.label.get_width() - 10, self.rect.y + 5))
        if self.is_selected:
            pygame.draw.line(screen, pygame.Color("black"), (self.rect.x + text_surface.get_width() + 5, self.rect.y + 5),
                             (self.rect.x + text_surface.get_width() + 5, self.rect.y + self.rect.height - 5))
        if self.cursor_visible:
            if pygame.time.get_ticks() >= self.cursor_timer:
                self.cursor_visible = False
            else:
                pygame.draw.line(screen, pygame.Color("black"),
                                 (self.rect.x + text_surface.get_width() + 5, self.rect.y + 5),
                                 (self.rect.x + text_surface.get_width() + 5, self.rect.y + self.rect.height - 5))