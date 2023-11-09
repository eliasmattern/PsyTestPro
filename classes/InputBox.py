import pygame
from pygame.locals import *

class InputBox:
    def __init__(self, x, y, width, height, translation_key, translate_service, info="", initial_text="", allow_new_line = False, not_allowed_characters = []):
        self.translate_service = translate_service
        self.rect = pygame.Rect(x - width // 2, y, width, height)
        self.color = pygame.Color("gray")
        self.active_color = pygame.Color("gray")
        self.text_color = pygame.Color("black")
        self.label_color = pygame.Color("gray")
        self.active_text_color = pygame.Color("black")
        self.text = initial_text
        self.font = pygame.font.SysFont("Arial", 24)
        self.translation_key = translation_key
        self.info = info
        self.label = self.font.render(self.translate_service.get_translation(self.translation_key)  + " " + self.info, True, self.label_color)
        self.is_selected = False
        self.cursor_visible = False
        self.cursor_timer = 0
        self.allow_new_line = allow_new_line
        self.not_allowed_characters = not_allowed_characters

    def handle_event(self, event):
        if event.type == MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos) and event.button == 1:
                self.is_selected = True
            else:
                self.is_selected = False
        elif event.type == KEYDOWN:
            mods = pygame.key.get_mods()
            if self.is_selected:
                if event.key == K_RETURN and self.allow_new_line:
                    self.text += " \\n "
                elif mods & KMOD_CTRL:  # Check if Ctrl is pressed
                    if event.key == K_v:
                        clipboard_content = pygame.scrap.get(pygame.SCRAP_TEXT)
                        if clipboard_content is not None:
                            try:
                                decoded_content = clipboard_content.decode('utf-8')
                                cleaned_content = decoded_content.replace('\x00', '')
                                self.text += cleaned_content
                            except UnicodeDecodeError:
                                print("Error: Unable to decode clipboard content.")
                        else:
                            print("Error: Unable to retrieve clipboard content.")

                elif event.key == K_RETURN:
                    pass
                elif event.key == K_BACKSPACE:
                    self.text = self.text[:-1]
                elif event.key == K_TAB:
                    pass
                else:
                    if event.unicode not in self.not_allowed_characters:
                        self.text += event.unicode
                self.cursor_visible = True
                self.cursor_timer = pygame.time.get_ticks() + 500
    
    def update_text(self):
        self.label = self.font.render(self.translate_service.get_translation(self.translation_key)  + " " + self.info, True, self.label_color)

    def draw(self, screen):
        pygame.draw.rect(screen, self.active_color if self.is_selected else self.color, self.rect)
        input_text = self.text
        text_surface = self.font.render(input_text, True, self.active_text_color if self.is_selected else self.text_color)
        while text_surface.get_rect().width > self.rect.width -10:
            input_text = input_text[1:]
            text_surface = self.font.render(input_text, True, self.active_text_color if self.is_selected else self.text_color)

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