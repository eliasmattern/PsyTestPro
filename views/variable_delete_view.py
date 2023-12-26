import sys
import tkinter as tk
from tkinter import messagebox
import pygame
from components import Button
from services import PsyTestProConfig


class DeleteVariableView:
    def __init__(self):
        self.running = True
        self.update = False
        self.psy_test_pro_config = PsyTestProConfig()
        self.settings = self.psy_test_pro_config.get_settings()

    def back(self):
        self.running = False

    def delete_var(self, psy_test_pro, translate_service, name):
        root = tk.Tk()
        root.withdraw()

        # Show a messagebox asking for confirmation
        response = messagebox.askyesno(
            translate_service.get_translation('delete'),
            translate_service.get_translation('deleteVarMsg') + name,
        )

        # If the user clicked 'Yes', then open browser
        if response == True:
            PsyTestProConfig().delete_var(name)
        else:
            root.destroy()

    def display(self, psy_test_pro, translate_service):
        psy_test_pro_config = PsyTestProConfig()

        # Define colors
        black = pygame.Color(self.settings["backgroundColor"])
        light_grey = pygame.Color(self.settings["primaryColor"])

        # Get the screen width and height from the current device in use
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

        # Creating a fullscreen display surface
        screen = pygame.display.get_surface()

        # Setting the window caption
        pygame.display.set_caption('Delete Variable')

        while self.running:
            screen.fill(black)

            buttons = []

            spacing = 0
            width, height = (
                pygame.display.Info().current_w,
                pygame.display.Info().current_h,
            )

            x = width // 2
            y = height // 2 - 150
            variables = psy_test_pro_config.load_custom_variables()

            if len(variables) > 0:
                for var in variables:
                    exp_button = Button(
                        x,
                        y + 60 + spacing,
                        400,
                        40,
                        var,
                        lambda var=var: self.delete_var(
                            psy_test_pro, translate_service, var
                        ),
                    )
                    buttons.append(exp_button)
                    spacing += 60

            spacing = 5 * 60
            spacing += 60
            back_button = Button(
                x,
                y + spacing + 100,
                100,
                40,
                'back',
                lambda: self.back(),
                translate_service,
            )
            buttons.append(back_button)

            width, height = (
                pygame.display.Info().current_w,
                pygame.display.Info().current_h,
            )
            x = width // 2
            y = height // 2 - 150
            font = pygame.font.Font(
                None, int(30 * width_scale_factor)
            )  # Create font object for header
            text_surface = font.render(
                translate_service.get_translation('deleteVar'), True, light_grey
            )  # Render the text 'Task' with the font and color light_grey
            text_rect = text_surface.get_rect()
            screen.blit(text_surface, (x - text_rect.width // 2, y))

            for button in buttons:
                button.draw(screen)

            pygame.display.flip()  # Flip the display to update the screen
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                for button in buttons:
                    button.handle_event(event)
        self.running = True
