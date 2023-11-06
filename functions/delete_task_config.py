import pygame
import sys
from pygame.locals import *
from classes import Button
from services import TeststarterConfig
from services import TeststarterConfig
import tkinter as tk
from tkinter import messagebox

class DeleteTaskConfig():
    def __init__(self):
           self.running = True
           self.page = 0
           self.removing = True
           self.experiment_name = ""
           self.time_of_day = ""
    
    def backToConfig(self):
        self.running = False

    def backToAddTask(self):
        self.removing = False

    def split_dict(self, input_dict, chunk_size):
        result = []
        current_chunk = {}
        count = 0

        for key, value in input_dict.items():
            current_chunk[key] = value
            count += 1

            if count == chunk_size:
                result.append(current_chunk)
                current_chunk = {}
                count = 0

        if current_chunk:
            result.append(current_chunk)

        return result

    def page_update(self, increment, splitted_tasks):
        if increment:
            self.page = (self.page + 1) % len(splitted_tasks)
        else:
            self.page = (
                (self.page - 1) if self.page > 0 else len(splitted_tasks) - 1
            )

    def delete_task_from_config(self, translate_service, experiment, task):
        config = TeststarterConfig()
        root = tk.Tk()
        root.withdraw()

        # Show a messagebox asking for confirmation
        response = messagebox.askyesno(
            translate_service.get_translation("delete"),
            translate_service.get_translation("deleteTaskMsg") + task,
        )

        # If the user clicked 'Yes', then open browser
        if response == True:
            config.delete_task(experiment, task)
        
        root.destroy()
        self.delete_task(translate_service, self.experiment_name, self.time_of_day)

    def delete_task(self, translate_service, experiment_name, time_of_day):
        self.experiment_name = experiment_name
        self.time_of_day = time_of_day
        self.page = 0
        self.running = True

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
        pygame.display.set_caption("Delete task")
        full_experiment_name = time_of_day + "_" + experiment_name + "_variable"
        tasks = (
            teststarter_config.load_tasks_of_experiment(full_experiment_name)
        )
        chunk_size = 5
        splitted_tasks = [tasks[i:i+chunk_size] for i in range(0, len(tasks), chunk_size)]

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
            if len(splitted_tasks) > 0:
                for task in splitted_tasks[self.page]:
                    exp_button = Button(
                        x,
                        y + 60 + spacing,
                        400,
                        40,
                        task,
                        lambda t=task: self.delete_task_from_config(
                            translate_service,
                            full_experiment_name,
                            t
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
                lambda: self.backToConfig(),
                translate_service,
            )
            buttons.append(back_button)

            if len(splitted_tasks) > 1:
                page_font = pygame.font.Font(None, int(24 * width_scale_factor))
                page_text_surface = page_font.render(
                    str(self.page + 1) + "/" + str(len(splitted_tasks)),
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
                    lambda: self.page_update(False, splitted_tasks),
                )
                next_page_back_button = Button(
                    x + 40,
                    y + 100 + spacing - 60,
                    25,
                    25,
                    ">",
                    lambda: self.page_update(True, splitted_tasks),
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
                translate_service.get_translation("deleteTaskFrom") + " " + experiment_name + " " + time_of_day , True, light_grey
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


    def delete_task_config_display(self, translate_service):
        self.page = 0
        self.running = True

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
        pygame.display.set_caption("Delete task")

        experiments_and_day_of_times = (
            teststarter_config.get_experiment_and_time_of_day()
        )
        splitted_experiments = self.split_dict(experiments_and_day_of_times, 5)

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

            for key, experiment in splitted_experiments[self.page].items():
                exp_button = Button(
                    x,
                    y + 60 + spacing,
                    400,
                    40,
                    experiment.get("experiment") + " " + experiment.get("time_of_day"),
                    lambda exp=experiment: self.delete_task(
                        translate_service,
                        exp.get("experiment"),
                        exp.get("time_of_day"),
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
                lambda: self.backToConfig(),
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
                translate_service.get_translation("chooseExperiment"), True, light_grey
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
