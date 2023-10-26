import pygame
import sys
import os
from pygame.locals import *
from classes import InputBox, Button, TimeInput
import json
from services import TeststarterConfig
import tkinter as tk
from tkinter import messagebox
from services import TeststarterConfig
from .task_config import TaskConfig
from .delete_experiment_config import DeleteExperimentConfig
from .create_experiment_config import CreateExperimentConfig


def backToTeststarter(teststarter):
    teststarter()


def back(teststarter, translate_service):
    experiment_config_display(teststarter, translate_service)


def experiment_config_display(teststarter, translate_service, create_continously=False):
    # Open the pygame window at front of all windows open on screen
    os.environ["SDL_VIDEO_WINDOW_POS"] = "0,0"  # Set window position to top-left corner

    # Define colors
    black = (0, 0, 0)
    light_grey = (192, 192, 192)

    # Initializing Pygame
    pygame.init()

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
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)

    # Setting the window caption
    pygame.display.set_caption("Configure Experiment")

    create_experiment_config = CreateExperimentConfig()
    delete_experiment_config = DeleteExperimentConfig()
    taskConfig = TaskConfig()

    buttons = []
    spacing = 0
    width, height = pygame.display.Info().current_w, pygame.display.Info().current_h

    x = width // 2
    y = height // 2 - 150

    back_button = Button(
        x,
        y + 240,
        100,
        40,
        "back",
        lambda: backToTeststarter(teststarter),
        translate_service,
    )
    create_experiment_button = Button(
        x,
        y + 60 + spacing,
        400,
        40,
        "createExperiment",
        lambda: create_experiment_config.create_experiment_config_display(
            teststarter, translate_service, create_continously
        ),
        translate_service,
    )
    spacing += 60
    delete_button = Button(
        x,
        y + 60 + spacing,
        400,
        40,
        "deleteExperiment",
        lambda: delete_experiment_config.delete_experiment_config_display(
            teststarter, translate_service
        ),
        translate_service,
    )
    spacing += 60
    create_task_button = Button(
        x,
        y + 60 + spacing,
        400,
        40,
        "createTask",
        lambda: taskConfig.add_task_config_display(teststarter, translate_service),
        translate_service,
    )

    buttons.append(back_button)
    buttons.append(create_experiment_button)
    buttons.append(delete_button)
    buttons.append(create_task_button)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            for button in buttons:
                button.handle_event(event)
        screen.fill(black)  # Fill the screen with the black color

        for button in buttons:
            button.draw(screen)

        font = pygame.font.Font(
            None, int(30 * width_scale_factor)
        )  # Create font object for header
        text_surface = font.render(
            translate_service.get_translation("configureExperiment"), True, light_grey
        )  # Render the text 'Task' with the font and color light_grey
        text_rect = text_surface.get_rect()
        screen.blit(text_surface, (x - text_rect.width // 2, y))

        pygame.display.flip()  # Flip the display to update the screen
