import pygame
import sys
import math


class QuestionDialog:
    def __init__(self, width, height, window_key, title_key, desc_key, translate_service, action=None):
        left, top = pygame.mouse.get_pos()
        self.window_key, self.title_key, self.desc_key = window_key, title_key, desc_key
        self.translate_service = translate_service
        self.action = action
        self.width, self.height= width, height
        self.window = pygame.Rect(left - width // 2, top, width, height)
        self.title_bar = pygame.Rect(left - width // 2, top, width, 30)
        self.font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 30)
        self.background_color = (255, 255, 255)
        self.primary_color = (0, 0, 0)
        self.is_open = False
        self.move = False
        self.line_angle = 0
        self.quit_rect = None

    def open(self):
        self.is_open = True

    def close(self):
        self.is_open = False

    def handle_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.quit_rect and self.quit_rect.collidepoint(event.pos):
                    self.is_open = False
                if self.title_bar.collidepoint(event.pos):
                    self.move = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.move = False

    def draw(self, screen):
        if self.move:
            left, top = pygame.mouse.get_pos()
            if -10 < top < screen.get_height() + 10 and -10 < left < screen.get_width() + 10:
                self.title_bar.top = top - 15
                self.title_bar.left = left - self.width // 2
                self.window.top = top - 15
                self.window.left = left - self.width // 2

        pygame.draw.rect(screen, (0,0,0), self.window)
        pygame.draw.rect(screen, self.background_color, self.window, width=2)
        pygame.draw.rect(screen, (255, 0, 0) if not self.move else (0, 255, 0), self.title_bar)

        title_bar_surface = self.font.render(self.translate_service.get_translation(self.window_key), True, (0, 0, 0))
        title_bar_pos = (self.title_bar.x + 10, self.title_bar.y + (self.title_bar.height // 4))

        quit_surface = self.font.render('X', True, (0, 0, 0))
        quit_bar_pos = (self.title_bar.x + self.width - 10, self.title_bar.y + (self.title_bar.height // 4))
        self.quit_rect = quit_surface.get_rect()
        title_surface = self.title_font.render(self.translate_service.get_translation(self.title_key), True, (0, 0, 0))
        title_pos = (self.window.x + 10, self.window.y + (self.window.height // 4))

        desc_surface = self.font.render(self.translate_service.get_translation(self.desc_key), True, (0, 0, 0))
        desc_pos = (self.window.x + 10, self.window.y + (self.window.height // 4) + self.title_font.get_linesize())

        screen.blit(title_bar_surface, title_bar_pos)
        screen.blit(title_surface, title_pos)
        screen.blit(desc_surface, desc_pos)
        screen.blit(quit_surface, quit_bar_pos)
        # TODO: add X button