import pygame
from services import TeststarterConfig


class CheckBox():
    def __init__(self, label, posX, posY, active=False, translate_service=None, font_size=18) -> None:
        self.translate_service = translate_service
        self.font = pygame.font.Font(None, font_size)
        self.teststarter_config = TeststarterConfig()
        self.settings = self.teststarter_config.get_settings()
        self.primary_color = pygame.Color(self.settings["primaryColor"])
        if translate_service:
            self.label = self.font.render(
                self.translate_service.get_translation(label),
                True,
                self.primary_color,
            )
        else:
            self.label = self.font.render(
                label,
                True,
                self.primary_color,
            )
        self.posX = posX - (self.label.get_width() // 2)
        self.posY = posY
        self.active = active
        self.tick_box_rect = None
        self.label_rect = None
        pass

    def handle_event(self, event):
        if self.tick_box_rect:
            if event.type == pygame.MOUSEBUTTONUP:
                if self.tick_box_rect.collidepoint(event.pos) or self.label_rect.collidepoint(event.pos):
                    if event.button == 1:
                        self.active = not self.active

    def draw(self, screen):
        screen_info = pygame.display.Info()

        # Store the screen width in a new variable
        screen_width = screen_info.current_w
        # Store the screen height in a new variable
        screen_height = screen_info.current_h
        # Store the original screen dimensions used to design this program
        original_width = 1280
        original_height = 800

        # Calculate scaling factors for position and size adjustments (this is how we can make sure that the program adjusts to any screen it is executed on)
        width_scale_factor = screen_width / original_width
        height_scale_factor = screen_height / original_height
        self.tick_box_rect = pygame.Rect(
            self.posX - 25,
            self.posY - (self.label.get_rect().height // 4),
            20,
            20,
        )
        pygame.draw.rect(screen, self.primary_color, self.tick_box_rect, 2)
        if self.active:
            # create a list of points that define the shape of the tick mark
            tick_mark_points = [
                (
                    self.posX - 21,
                    self.posY + 7,
                ),
                (
                    self.posX - 17,
                    self.posY + 11,
                ),
                (
                    self.posX - 13,
                    self.posY + 1,
                ),
            ]
            # draw lines connecting the points defined above (draw the tick)
            pygame.draw.lines(screen, self.primary_color, False, tick_mark_points, 2)
        self.label_rect = self.label.get_rect(left=self.posX, top=self.posY)
        screen.blit(self.label, self.label_rect)
