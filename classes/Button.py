import pygame
from pygame.locals import *

class Button:
    def __init__(self, x, y, width, height, translation_key, action, translate_service, color = "gray"):
        self.translate_service = translate_service
        self.rect = pygame.Rect(x - width // 2, y, width, height)
        self.color = pygame.Color(color)
        self.translation_key = translation_key
        self.label = pygame.font.SysFont("Arial", 24).render(self.translate_service.get_translation(self.translation_key), True, pygame.Color("black"))
        self.action = action
        self.is_active = True

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONUP and self.rect.collidepoint(event.pos):
            if self.is_active:
                self.action()
    
    def set_active(self, active):
        self.is_active = active

    def update_text(self):
        self.label = pygame.font.SysFont("Arial", 24).render(self.translate_service.get_translation(self.translation_key), True, pygame.Color("black"))

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        label_width, label_height = self.label.get_size()
        label_x = self.rect.x + (self.rect.width - label_width) // 2
        label_y = self.rect.y + (self.rect.height - label_height) // 2
        screen.blit(self.label, (label_x, label_y))
    def set_color(self, color):
        self.color = color