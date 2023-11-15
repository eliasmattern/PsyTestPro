import pygame
from pygame.locals import *
from datetime import datetime
class InputBox:
    def __init__(self, x, y, width, height, translation_key, translate_service=None, info="", initial_text="", allow_new_line = False, not_allowed_characters = []):
        self.translate_service = translate_service
        self.rect = pygame.Rect(x - width // 2, y, width, height)
        self.color = pygame.Color("gray")
        self.active_color = (218, 221, 220)
        self.text_color = pygame.Color("black")
        self.label_color = pygame.Color("gray")
        self.active_text_color = pygame.Color("black")
        self.text = initial_text
        self.font = pygame.font.SysFont("Arial", 24)
        self.translation_key = translation_key
        self.info = info
        if self.translate_service:
            self.label = self.font.render(self.translate_service.get_translation(self.translation_key)  + " " + self.info, True, self.label_color)
        else:
            self.label = self.font.render(self.translation_key  + " " + self.info, True, self.label_color)
        self.is_selected = False
        self.cursor_visible = False
        self.cursor_timer = 0
        self.allow_new_line = allow_new_line
        self.not_allowed_characters = not_allowed_characters
        self.started_removing = False
        self.started_moving_r = False
        self.started_moving_l = False
        self.delay = None
        self.image = pygame.image.load("./img/copyIcon.png")
        self.posX = x
        self.posY = y
        self.imagePos = pygame.Rect(0,0, self.image.get_rect().width, self.image.get_rect().height)
        self.delayMultiplicator = 0.4
        self.cursor_blink = True
        self.offset = 0
        self.cursor_pos = (0,0)
        self.is_highlighted = False
        self.started_del = False
        self.textPage = 0
        self.text_memmory = []
        self.memmory_index = 0

    def handle_event(self, event):
        if event.type == MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos) and event.button == 1:
                self.is_selected = True
            else:
                self.is_selected = False
                self.is_highlighted = False
            if self.imagePos.collidepoint(pygame.mouse.get_pos()) and event.button == 1:
                pygame.scrap.put(pygame.SCRAP_TEXT, self.text.encode('utf-8'))
        elif event.type == KEYUP:
            if self.is_selected:
                if event.key == K_BACKSPACE:
                    self.started_removing = False
                    self.delay = None
                    self.delayMultiplicator = 0.4
                elif event.key == K_RIGHT:
                    self.started_moving_r = False
                    self.delay = None
                    self.delayMultiplicator = 0.4
                elif event.key == K_LEFT:
                    self.started_moving_l = False
                    self.delay = None
                    self.delayMultiplicator = 0.4
                elif event.key == K_DELETE:
                    self.started_del = False
                    self.delay = None
                    self.delayMultiplicator = 0.4
        elif event.type == KEYDOWN:
            mods = pygame.key.get_mods()
            if self.is_selected:
                if event.key == K_RETURN and self.allow_new_line:
                    self.text_memmory.append(self.text)
                    self.memmory_index = 0
                    self.text += " \\n "
                elif mods & KMOD_CTRL:  # Check if Ctrl is pressed
                    if event.key == K_v:
                        clipboard_content = pygame.scrap.get(pygame.SCRAP_TEXT)
                        if clipboard_content is not None:
                            try:
                                decoded_content = clipboard_content.decode('utf-8')
                                cleaned_content = decoded_content.replace('\x00', '')
                                self.text_memmory.append(self.text)
                                self.memmory_index = 0
                                self.text += cleaned_content
                            except UnicodeDecodeError:
                                print("Error: Unable to decode clipboard content.")
                        else:
                            print("Error: Unable to retrieve clipboard content.")
                    elif event.key == K_BACKSPACE:
                        self.text_memmory.append(self.text)
                        self.memmory_index = 0
                        text_length = len(self.text)
                        self.text = self.text[text_length-self.offset:text_length]
                    elif event.key == K_a:
                        self.is_highlighted = True
                    elif event.key == K_c:
                        if self.is_highlighted:
                            self.is_highlighted = False
                            pygame.scrap.put(pygame.SCRAP_TEXT, self.text.encode('utf-8'))
                        else: 
                            pass
                    elif event.key == K_x:
                        if self.is_highlighted:
                            self.text_memmory.append(self.text)
                            self.memmory_index = 0
                            self.is_highlighted = False
                            pygame.scrap.put(pygame.SCRAP_TEXT, self.text.encode('utf-8'))
                            self.text = ""
                        else: 
                            pass
                    elif event.key == K_z:
                        if self.is_selected:
                            if self.memmory_index == 0 and len(self.text_memmory) > 0 and self.text != self.text_memmory[-1:][0]:
                                self.text_memmory.append(self.text)
                            memmory_copy = self.text_memmory.copy()
                            memmory_copy.reverse()
                            if self.memmory_index + 1 < len(memmory_copy):
                                self.memmory_index += 1
                                self.text = memmory_copy[self.memmory_index]
                    elif event.key == K_y:
                        if self.is_selected:
                            if self.memmory_index != 0:
                                memmory_copy = self.text_memmory.copy()
                                memmory_copy.reverse()
                                self.memmory_index -= 1
                                self.text = memmory_copy[self.memmory_index]

                elif event.key == K_RETURN:
                    pass
                elif event.key == K_LEFT:
                    text_length = len(self.text)
                    if self.offset < text_length:
                        self.offset += 1
                        self.cursor_pos = self.font.size(self.text[text_length-self.offset:text_length])
                    self.started_moving_l = True
                    self.delay = datetime.now().timestamp()
                    self.is_highlighted = False
                elif event.key == K_RIGHT:
                    text_length = len(self.text)
                    if self.offset > 0:
                        self.offset -= 1
                        self.cursor_pos = self.font.size(self.text[text_length-self.offset:text_length])
                    self.started_moving_r = True
                    self.delay = datetime.now().timestamp()
                    self.is_highlighted = False
                elif event.key == K_BACKSPACE:
                    memmory_copy = self.text_memmory.copy()
                    if len(memmory_copy) > 0:
                        memmory_copy.reverse()
                        if len(memmory_copy[0]) > 1:
                            self.text_memmory.append(self.text)
                    self.memmory_index = 0
                    text_length = len(self.text)
                    if self.is_highlighted:
                        self.text = ""
                        self.cursor_pos = (0,0)
                        self.offset = 0
                        pass
                    if (len(self.text[0:text_length-self.offset]) > 0):
                        self.text = self.text[0:text_length-self.offset-1] + self.text[text_length-self.offset:text_length]
                        self.started_removing = True
                        self.delay = datetime.now().timestamp()
                    self.is_highlighted = False
                elif event.key == K_TAB:
                    self.is_highlighted = False
                elif event.key == K_ESCAPE:
                    self.is_highlighted = False
                elif event.key == K_DELETE:
                    memmory_copy = self.text_memmory.copy()
                    if len(memmory_copy) > 0:
                        memmory_copy.reverse()
                        if len(memmory_copy[0]) > 1:
                            self.text_memmory.append(self.text)
                    self.memmory_index = 0
                    text_length = len(self.text)
                    if self.is_highlighted:
                        self.text = ""
                        self.cursor_pos = (0,0)
                        self.offset = 0
                        pass
                    if (len(self.text[text_length-self.offset:text_length]) > 0):
                        self.text = self.text[0:text_length-self.offset] + self.text[(text_length-self.offset)+1:text_length]
                        self.cursor_pos = self.font.size(self.text[text_length-self.offset:text_length])
                        self.offset -= 1
                        self.started_del = True
                        self.delay = datetime.now().timestamp()
                else:
                    text_length = len(self.text)
                    if event.unicode not in self.not_allowed_characters:
                        self.text_memmory.append(self.text)
                        self.memmory_index = 0
                        self.text = self.text[0:text_length-self.offset] + event.unicode + self.text[text_length-self.offset:text_length]
                    self.is_highlighted = False

                self.cursor_visible = True
                self.cursor_timer = pygame.time.get_ticks() + 500
    
    def update_text(self):
        if self.translate_service:
            self.label = self.font.render(self.translate_service.get_translation(self.translation_key)  + " " + self.info, True, self.label_color)

    def draw(self, screen):
        if self.is_selected:
            print(self.text_memmory)
        pygame.draw.rect(screen, self.active_color if self.is_selected else self.color, self.rect)
        input_text = self.text
        text_bg_color = self.color
        if self.is_selected:
            text_bg_color = self.active_color
        if self.is_highlighted:
            text_bg_color = (102, 101, 221)

        text_surface = self.font.render(input_text, True, self.active_text_color if self.is_selected else self.text_color, text_bg_color)
        while text_surface.get_rect().width > self.rect.width // 100 * 88:
            input_text = input_text[1:]
            text_surface = self.font.render(input_text, True, self.active_text_color if self.is_selected else self.text_color, text_bg_color)
        if self.is_selected and self.delay != None and self.started_removing:
            if float(datetime.now().timestamp()) - float(self.delay) > self.delayMultiplicator:
                text_length = len(self.text)
                if (len(self.text[0:text_length-self.offset]) > 0):
                    self.text = self.text[0:text_length-self.offset-1] + self.text[text_length-self.offset:text_length]
                    self.delay = datetime.now().timestamp()
                    self.delayMultiplicator = 0.1
        
        if self.is_selected and self.delay != None and self.started_moving_r:
            if float(datetime.now().timestamp()) - float(self.delay) > self.delayMultiplicator:
                text_length = len(self.text)
                if self.offset > 0:
                    self.offset -= 1
                    self.cursor_pos = self.font.size(self.text[text_length-self.offset:text_length])
                    self.delay = datetime.now().timestamp()
                    self.delayMultiplicator = 0.1
        
        if self.is_selected and self.delay != None and self.started_moving_l:
            if float(datetime.now().timestamp()) - float(self.delay) > self.delayMultiplicator:
                text_length = len(self.text)
                if self.offset < text_length:
                    self.offset += 1
                    self.cursor_pos = self.font.size(self.text[text_length-self.offset:text_length])
                    self.delay = datetime.now().timestamp()
                    self.delayMultiplicator = 0.1
        
        if self.is_selected and self.delay != None and self.started_del:
            if float(datetime.now().timestamp()) - float(self.delay) > self.delayMultiplicator:
                text_length = len(self.text)
                if (len(self.text[text_length-self.offset:text_length]) > 0):
                    self.text = self.text[0:text_length-self.offset] + self.text[(text_length-self.offset)+1:text_length]
                    self.cursor_pos = self.font.size(self.text[text_length-self.offset:text_length])
                    self.offset -= 1
                    self.delay = datetime.now().timestamp()
                    self.delayMultiplicator = 0.1

        screen.blit(text_surface, (self.rect.x + 5, self.rect.y + 5))
        screen.blit(self.label, (self.rect.x - self.label.get_width() - 10, self.rect.y + 5))
        if self.is_selected:
            color = pygame.Color("black") if self.cursor_blink else self.active_color
            pygame.draw.line(screen, color, (self.rect.x + text_surface.get_width() + 5 - self.cursor_pos[0], self.rect.y + 5),
                             (self.rect.x + text_surface.get_width() + 5 - self.cursor_pos[0], self.rect.y + self.rect.height - 5))
        if self.cursor_visible:
            if pygame.time.get_ticks() >= self.cursor_timer:
                self.cursor_visible = False
            else:
                color = pygame.Color("black") if self.cursor_blink else self.active_color
                pygame.draw.line(screen, color,
                                 (self.rect.x + text_surface.get_width() + 5 - self.cursor_pos[0], self.rect.y + 5),
                                 (self.rect.x + text_surface.get_width() + 5 - self.cursor_pos[0], self.rect.y + self.rect.height - 5))
        self.imagePos = pygame.Rect(self.posX + (self.rect.width// 2) // 100 * 80, self.posY, self.image.get_rect().width, self.image.get_rect().height)
        screen.blit(self.image, (self.posX + (self.rect.width// 2) // 100 * 80, self.posY ))
        if self.is_selected:
            if ((pygame.time.get_ticks()// 500) % 2) == 0 or self.started_moving_r or self.started_moving_l:
                self.cursor_blink = True
            else:
                self.cursor_blink = False
        