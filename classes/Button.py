import pygame
from pygame.locals import *

class Button:
    def __init__(self, x, y, width, height, label, action):
        self.rect = pygame.Rect(x - width // 2, y, width, height)
        self.color = pygame.Color("gray")
        self.label = pygame.font.SysFont("Arial", 24).render(label, True, pygame.Color("black"))
        self.action = action

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONUP and self.rect.collidepoint(event.pos):
            self.action()

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        label_width, label_height = self.label.get_size()
        label_x = self.rect.x + (self.rect.width - label_width) // 2
        label_y = self.rect.y + (self.rect.height - label_height) // 2
        screen.blit(self.label, (label_x, label_y))