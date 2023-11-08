import pygame
import sys
from pygame.locals import *
from classes import Button
import json
from services import TeststarterConfig
import tkinter as tk
from tkinter import messagebox
from services import TeststarterConfig


class DeleteExperimentConfig:
    def __init__(self):
        self.page = 0
        self.running = True

    def back(self):
        self.running = False

    def delete_experiment(self, teststarter, translate_service, experiment_name):
        root = tk.Tk()
        root.withdraw()

        # Show a messagebox asking for confirmation
        response = messagebox.askyesno(
            translate_service.get_translation("delete"),
            translate_service.get_translation("deleteExperimentMsg") + experiment_name,
        )

        # If the user clicked 'Yes', then open browser
        if response == True:
            # Load the original JSON from the file
            with open("json/taskConfig.json", "r") as file:
                original_tasks = json.load(file)

            exp_keys = [key for key in original_tasks.keys() if experiment_name in key]

            del original_tasks[exp_keys[0]]
            with open("json/experimentConfig.json", "r") as file:
                original_experiments = json.load(file)

            # Add a new value to the array

            original_experiments.remove(experiment_name)

            # Save the updated array back to the file
            with open("json/experimentConfig.json", "w") as file:
                json.dump(original_experiments, file)

            # Save the updated JSON back to the file
            with open("json/taskConfig.json", "w") as file:
                json.dump(original_tasks, file, indent=4)
            # Destroy the root window
            root.destroy()
            self.delete_experiment_config_display(teststarter, translate_service)
        else:
            root.destroy()

    def page_update(self, increment, splitted_experiments):
        if increment:
            self.page = (self.page + 1) % len(splitted_experiments)
        else:
            self.page = (
                (self.page - 1) if self.page > 0 else len(splitted_experiments) - 1
            )

    def delete_experiment_config_display(self, teststarter, translate_service):
        teststarter_config = TeststarterConfig()

        # Define colors
        black = (0, 0, 0)
        light_grey = (192, 192, 192)

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
        pygame.display.set_caption("Delete Experiment")

        teststarter_config.load_experiments()
        experiments = teststarter_config.experiments
        
        if "hab" in experiments:
            experiments.remove("hab")

        splitted_experiments = [
            experiments[i : i + 5] for i in range(0, len(experiments), 5)
        ]

        self.page = 0

        while self.running:
            screen.fill(black)  # Fill the screen with the black color

            buttons = []

            spacing = 0
            width, height = (
                pygame.display.Info().current_w,
                pygame.display.Info().current_h,
            )

            x = width // 2
            y = height // 2 - 150

            if len(splitted_experiments) > 0:
                for experiment in splitted_experiments[self.page]:
                    exp_button = Button(
                        x,
                        y + 60 + spacing,
                        400,
                        40,
                        experiment,
                        lambda exp=experiment: self.delete_experiment(
                            teststarter, translate_service, exp
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
                "back",
                lambda: self.back(),
                translate_service,
            )
            buttons.append(back_button)

            if len(splitted_experiments) > 1:
                page_font = pygame.font.Font(None, int(24 * width_scale_factor))
                page_text_surface = page_font.render(
                    str(self.page + 1) + "/" + str(len(splitted_experiments)),
                    True,
                    light_grey,
                )
                page_rect = page_text_surface.get_rect()
                screen.blit(
                    page_text_surface,
                    (x - page_rect.width // 2, y + 100 + spacing - 60),
                )
                previous_page_button = Button(
                    x - 40,
                    y + 100 + spacing - 60,
                    25,
                    25,
                    "<",
                    lambda: self.page_update(False, splitted_experiments),
                )
                next_page_back_button = Button(
                    x + 40,
                    y + 100 + spacing - 60,
                    25,
                    25,
                    ">",
                    lambda: self.page_update(True, splitted_experiments),
                )
                buttons.append(previous_page_button)
                buttons.append(next_page_back_button)

            # This invokes the function draw_button

            # Display column headers with adjusted font size
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
                translate_service.get_translation("deleteExperiment"), True, light_grey
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
