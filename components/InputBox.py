from datetime import datetime

import pygame
from pygame.locals import *
from services import TeststarterConfig


class InputBox:
    def __init__(self, x, y, width, height, translation_key, translate_service=None, info='', initial_text='', desc='',
                 allow_new_line=False, not_allowed_characters=[], is_active=True):
        self.translate_service = translate_service
        self.rect = pygame.Rect(x - width // 2, y, width, height)
        self.teststarter_config = TeststarterConfig()
        self.settings = self.teststarter_config.get_settings()
        self.color = pygame.Color(self.settings["buttonColor"])
        self.active_color = pygame.Color(self.settings["activeButtonColor"])
        self.text_color = pygame.Color(self.settings["buttonTextColor"])
        self.label_color = pygame.Color(self.settings["buttonTextColor"])
        self.active_text_color = pygame.Color(self.settings["buttonTextColor"])
        self.text = initial_text
        self.font = pygame.font.SysFont('Arial', 24)
        self.translation_key = translation_key
        self.info = info
        self.desc = desc
        if self.translate_service:
            self.label = self.font.render(
                self.translate_service.get_translation(self.translation_key) + ' ' + self.info, True, self.label_color)
        else:
            self.label = self.font.render(self.translation_key + ' ' + self.info, True, self.label_color)
        self.is_selected = False
        self.cursor_visible = False
        self.cursor_timer = 0
        self.allow_new_line = allow_new_line
        self.not_allowed_characters = not_allowed_characters
        self.started_removing = False
        self.started_moving_r = False
        self.started_moving_l = False
        self.delay = None
        self.image = pygame.image.load('./img/copyIcon.png')
        self.posX = x
        self.posY = y
        self.imagePos = pygame.Rect(0, 0, self.image.get_rect().width, self.image.get_rect().height)
        self.delayMultiplier = 0.4
        self.cursor_blink = True
        self.offset = 0
        self.cursor_pos = (0, 0)
        self.is_highlighted = False
        self.started_del = False
        self.textPage = 0
        self.text_memory = []
        self.memory_index = 0
        self.is_active = is_active
        self.inactive_color = pygame.Color(self.settings["inactiveButtonColor"])

    def set_active(self, active):
        self.is_active = active

    def handle_event(self, event):
        if self.is_active:
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
                        self.delayMultiplier = 0.4
                    elif event.key == K_RIGHT:
                        self.started_moving_r = False
                        self.delay = None
                        self.delayMultiplier = 0.4
                    elif event.key == K_LEFT:
                        self.started_moving_l = False
                        self.delay = None
                        self.delayMultiplier = 0.4
                    elif event.key == K_DELETE:
                        self.started_del = False
                        self.delay = None
                        self.delayMultiplier = 0.4
            elif event.type == KEYDOWN:
                mods = pygame.key.get_mods()
                if self.is_selected:
                    if event.key == K_RETURN and self.allow_new_line:
                        self.text_memory.append(self.text)
                        self.memory_index = 0
                        self.text += ' \\n '
                    elif mods & KMOD_CTRL and event.key in {K_v, K_BACKSPACE, K_a, K_c, K_x, K_z, K_y, K_LEFT,
                                                            K_RIGHT}:  # Check if Ctrl is pressed
                        if event.key == K_v:
                            clipboard_content = pygame.scrap.get(pygame.SCRAP_TEXT)
                            if clipboard_content is not None:
                                try:
                                    decoded_content = clipboard_content.decode('utf-8')
                                    cleaned_content = decoded_content.replace('\x00', '')
                                    self.text_memory.append(self.text)
                                    self.memory_index = 0
                                    if self.is_highlighted:
                                        self.text = ''
                                        self.offset = 0
                                        self.cursor_pos = (0, 0)
                                    self.text += cleaned_content
                                    self.is_highlighted = False
                                except UnicodeDecodeError:
                                    print('Error: Unable to decode clipboard content.')
                            else:
                                print('Error: Unable to retrieve clipboard content.')
                        elif event.key == K_BACKSPACE:
                            self.text_memory.append(self.text)
                            self.memory_index = 0
                            text_length = len(self.text)
                            self.text = self.text[text_length - self.offset:text_length]
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
                                self.text_memory.append(self.text)
                                self.memory_index = 0
                                self.is_highlighted = False
                                pygame.scrap.put(pygame.SCRAP_TEXT, self.text.encode('utf-8'))
                                self.text = ''
                                self.offset = 0
                                self.cursor_pos = (0, 0)
                            else:
                                pass
                        elif event.key == K_RIGHT:
                            self.offset = 0
                            self.cursor_pos = (0, 0)
                        elif event.key == K_z:
                            if self.is_selected:
                                self.offset = 0
                                self.cursor_pos = (0, 0)
                                if self.memory_index == 0 and len(self.text_memory) > 0 and self.text != \
                                        self.text_memory[-1:][0]:
                                    self.text_memory.append(self.text)
                                memmory_copy = self.text_memory.copy()
                                memmory_copy.reverse()
                                if self.memory_index + 1 < len(memmory_copy):
                                    self.memory_index += 1
                                    self.text = memmory_copy[self.memory_index]
                        elif event.key == K_y:
                            if self.is_selected:
                                if self.memory_index != 0:
                                    self.offset = 0
                                    self.cursor_pos = (0, 0)
                                    memmory_copy = self.text_memory.copy()
                                    memmory_copy.reverse()
                                    self.memory_index -= 1
                                    self.text = memmory_copy[self.memory_index]
                    elif event.key == K_RETURN:
                        pass
                    elif event.key == K_LEFT:
                        text_length = len(self.text)
                        if self.offset < text_length:
                            self.offset += 1
                            self.cursor_pos = self.font.size(self.text[text_length - self.offset:text_length])
                        self.started_moving_l = True
                        self.delay = datetime.now().timestamp()
                        self.is_highlighted = False
                    elif event.key == K_RIGHT:
                        text_length = len(self.text)
                        if self.offset > 0:
                            self.offset -= 1
                            self.cursor_pos = self.font.size(self.text[text_length - self.offset:text_length])
                        self.started_moving_r = True
                        self.delay = datetime.now().timestamp()
                        self.is_highlighted = False
                    elif event.key == K_BACKSPACE:
                        memmory_copy = self.text_memory.copy()
                        if len(memmory_copy) > 0:
                            memmory_copy.reverse()
                            if len(memmory_copy[0]) > 1:
                                self.text_memory.append(self.text)
                        self.memory_index = 0
                        text_length = len(self.text)
                        if self.is_highlighted:
                            self.text = ''
                            self.cursor_pos = (0, 0)
                            self.offset = 0
                            pass
                        if (len(self.text[0:text_length - self.offset]) > 0):
                            self.text = self.text[0:text_length - self.offset - 1] + self.text[
                                                                                     text_length - self.offset:text_length]
                            self.started_removing = True
                            self.delay = datetime.now().timestamp()
                        self.is_highlighted = False
                    elif event.key == K_TAB:
                        self.is_highlighted = False
                    elif event.key == K_ESCAPE:
                        self.is_highlighted = False

                    elif event.key == K_DELETE:
                        memmory_copy = self.text_memory.copy()
                        if len(memmory_copy) > 0:
                            memmory_copy.reverse()
                            if len(memmory_copy[0]) > 1:
                                self.text_memory.append(self.text)
                        self.memory_index = 0
                        text_length = len(self.text)
                        if self.is_highlighted:
                            self.text = ''
                            self.cursor_pos = (0, 0)
                            self.offset = 0
                            pass
                        if (len(self.text[text_length - self.offset:text_length]) > 0):
                            self.text = self.text[0:text_length - self.offset] + self.text[(
                                                                                                   text_length - self.offset) + 1:text_length]
                            self.cursor_pos = self.font.size(self.text[text_length - self.offset:text_length])
                            self.offset -= 1
                            self.started_del = True
                            self.delay = datetime.now().timestamp()
                    else:
                        text_length = len(self.text)
                        if event.unicode not in self.not_allowed_characters:
                            self.text_memory.append(self.text)
                            self.memory_index = 0
                            if self.is_highlighted:
                                self.offset = 0
                                self.cursor_pos = (0, 0)
                                self.text = ''
                            self.text = self.text[0:text_length - self.offset] + event.unicode + self.text[
                                                                                                 text_length - self.offset:text_length]
                        self.is_highlighted = False

                    self.cursor_visible = True
                    self.cursor_timer = pygame.time.get_ticks() + 500

    def update_text(self):
        if self.translate_service:
            if self.is_selected:
                self.label = self.font.render(
                    self.translate_service.get_translation(self.translation_key) + ' ' + self.info, True,
                    self.active_text_color)
            else:
                self.label = self.font.render(
                    self.translate_service.get_translation(self.translation_key) + ' ' + self.info, True,
                    self.label_color)
        else:
            if self.is_selected:
                self.label = self.font.render(self.translation_key + ' ' + self.info, True, self.active_text_color)
            else:
                self.label = self.font.render(self.translation_key + ' ' + self.info, True, self.label_color)

    def draw(self, screen):
        if not self.is_selected:
            self.started_del = False
            self.started_moving_l = False
            self.started_removing = False
            self.started_moving_r = False
            self.delay = None
            self.delayMultiplier = 0.4
        if self.text == "" and self.is_selected and self.offset != 0:
            self.offset = 0
            self.cursor_pos = (0, 0)
        if self.is_active:
            pygame.draw.rect(screen, self.active_color if self.is_selected else self.color, self.rect, border_radius=8)
        else:
            pygame.draw.rect(screen, self.inactive_color, self.rect, border_radius=8)

        input_text = self.text
        text_bg_color = self.color
        if self.is_selected:
            text_bg_color = self.active_color
        if self.is_highlighted:
            text_bg_color = (102, 101, 221)
        if not self.is_active:
            text_bg_color = self.inactive_color

        text_surface = self.font.render(input_text, True,
                                        self.active_text_color if self.is_selected else self.text_color, text_bg_color)
        count = 0
        while text_surface.get_rect().width > self.rect.width // 100 * 85:
            input_text = input_text[1:]
            count += 1
            text_surface = self.font.render(input_text, True,
                                            self.active_text_color if self.is_selected else self.text_color,
                                            text_bg_color)
        diff = self.offset - (len(input_text) - 3)

        if count > 0 and self.offset > len(input_text) - 3:
            input_text = self.text
            input_text = input_text[count - diff if count - diff > 0 else 0: len(input_text) - abs(diff)]
            text_surface = self.font.render(input_text, True,
                                            self.active_text_color if self.is_selected else self.text_color,
                                            text_bg_color)

        if self.is_selected and self.delay is not None and self.started_removing:
            if float(datetime.now().timestamp()) - float(self.delay) > self.delayMultiplier:
                text_length = len(self.text)
                if len(self.text[0:text_length - self.offset]) > 0:
                    self.text = self.text[0:text_length - self.offset - 1] + self.text[
                                                                             text_length - self.offset:text_length]
                    self.delay = datetime.now().timestamp()
                    self.delayMultiplier = 0.1

        if self.is_selected and self.delay is not None and self.started_moving_r:
            if float(datetime.now().timestamp()) - float(self.delay) > self.delayMultiplier:
                text_length = len(self.text)
                if self.offset > 0:
                    self.offset -= 1
                    self.cursor_pos = self.font.size(self.text[text_length - self.offset:text_length])
                    self.delay = datetime.now().timestamp()
                    self.delayMultiplier = 0.1

        if self.is_selected and self.delay != None and self.started_moving_l:
            if float(datetime.now().timestamp()) - float(self.delay) > self.delayMultiplier:
                text_length = len(self.text)
                if self.offset < text_length:
                    self.offset += 1
                    self.cursor_pos = self.font.size(self.text[text_length - self.offset:text_length])
                    self.delay = datetime.now().timestamp()
                    self.delayMultiplier = 0.1

        if self.is_selected and self.delay != None and self.started_del:
            if float(datetime.now().timestamp()) - float(self.delay) > self.delayMultiplier:
                text_length = len(self.text)
                if len(self.text[text_length - self.offset:text_length]) > 0:
                    self.text = self.text[0:text_length - self.offset] + self.text[
                                                                         (text_length - self.offset) + 1:text_length]
                    self.cursor_pos = self.font.size(self.text[text_length - self.offset:text_length])
                    self.offset -= 1
                    self.delay = datetime.now().timestamp()
                    self.delayMultiplier = 0.1

        screen.blit(text_surface, (self.rect.x + 5, self.rect.y + 5))
        if count > 0 and count - diff >= 0:
            posX = (self.rect.x + text_surface.get_width() + 5 - self.cursor_pos[0]
                    if self.rect.x + text_surface.get_width() + 5 - self.cursor_pos[0] >= self.posX - (
                    self.rect.width // 2) + self.font.size(input_text[0:3])[0]
                    else self.posX - (self.rect.width // 2) + self.font.size(input_text[0:3])[0] + 5)
        elif count > 0 > count - diff:
            last_chars = abs(count - diff)
            posX = self.posX - (self.rect.width // 2) + self.font.size(input_text[0:3 - last_chars])[0] + 5
        else:
            posX = self.rect.x + text_surface.get_width() + 5 - self.cursor_pos[0]

        if self.is_selected:
            color = self.active_text_color if self.cursor_blink else self.active_color
            pygame.draw.line(screen, color, (posX, self.rect.y + 5),
                             (posX, self.rect.y + self.rect.height - 5))
        if self.cursor_visible:
            if pygame.time.get_ticks() >= self.cursor_timer:
                self.cursor_visible = False
            else:
                color = self.active_text_color if self.cursor_blink else self.active_color
                pygame.draw.line(screen, color,
                                 (posX, self.rect.y + 5),
                                 (posX, self.rect.y + self.rect.height - 5))
        self.imagePos = pygame.Rect(self.posX + (self.rect.width // 2) // 100 * 80, self.posY,
                                    self.image.get_rect().width, self.image.get_rect().height)
        screen.blit(self.image, (self.posX + (self.rect.width // 2) // 100 * 80, self.posY + 5))
        if self.is_selected:
            if ((pygame.time.get_ticks() // 500) % 2) == 0 or self.started_moving_r or self.started_moving_l:
                self.cursor_blink = True
            else:
                self.cursor_blink = False
        if len(self.text) == 0 and not self.is_selected:
            screen.blit(self.label, (self.rect.x + 5, self.rect.y + 5))
        if self.is_selected:
            info_font = pygame.font.SysFont('Arial', 12)
            info_label = info_font.render(self.info, True, self.active_color if self.is_active else self.inactive_color)
            screen.blit(info_label, (self.rect.x + 5, self.rect.y + 40))

        desc_font = pygame.font.SysFont('Arial', 12)
        desc_color = self.color
        if self.is_selected:
            desc_color = self.active_color
        elif not self.is_active:
            desc_color = self.inactive_color
        desc_label = desc_font.render(self.desc, True, desc_color)
        screen.blit(desc_label, (self.rect.x + 5, self.rect.y - 17))
