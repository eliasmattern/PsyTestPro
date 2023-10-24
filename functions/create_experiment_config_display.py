import pygame
import sys
import os
from pygame.locals import *
import re
from .create_time_picker import create_time_picker
from classes import InputBox, Button
import json


def back(teststarter):
    teststarter()

def save_experiment(teststarter, experiment_name, experiment_time_of_day):
    with open('json/experimentConfig.json', 'r') as file:
        original_experiments = json.load(file)

        # Add a new value to the array
        original_experiments.append(experiment_name)

    # Save the updated array back to the file
    with open('json/experimentConfig.json', 'w') as file:
        json.dump(original_experiments, file)

    # Load the original JSON from the file
    with open('json/taskConfig.json', 'r') as file:
        original_tasks = json.load(file)

    # Add a new variable with an empty task object
    original_tasks[experiment_time_of_day + "_" + experiment_name + "_variable"] = {"tasks": {}}

    # Save the updated JSON back to the file
    with open('json/taskConfig.json', 'w') as file:
        json.dump(original_tasks, file, indent=4)

    back(teststarter)
    

def create_input_boxes(teststarter, translate_service):
    input_boxes = []
    buttons = []
    labels = ["experimentName", "timeOfDay"]
    spacing = 60
    width, height =pygame.display.Info().current_w, pygame.display.Info().current_h
    x = width // 2
    y = height // 2 - 100
    for label in labels:
        input_box = InputBox(x, y, 400, 40, label, translate_service)
        input_boxes.append(input_box)
        y += spacing

    exit_button = Button(x - 75, y + 60, 100, 40, "back", lambda: back(teststarter), translate_service)
    submit_button = Button(x + 75, y + 60, 100, 40, "submit", lambda: save_experiment(teststarter, input_boxes[0].text, input_boxes[1].text), translate_service)

    buttons.append(exit_button)
    buttons.append(submit_button)
    return input_boxes, buttons

def validate_inputs(input_boxes):
    is_valid = False
    
    if input_boxes[0].text and input_boxes[1].text == "morn" or input_boxes[1].text == "eve" or input_boxes[1].text == "full":
        is_valid = True

    if is_valid:
        return True
    else:
        return False

def create_experiment_config_display(teststarter, translate_service, create_continously = False):

    # Open the pygame window at front of all windows open on screen
    os.environ['SDL_VIDEO_WINDOW_POS'] = '0,0'  # Set window position to top-left corner

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
    pygame.display.set_caption('Create Experiment')

    input_boxes, buttons = create_input_boxes(teststarter, translate_service)

    def get_input_index():
            index = 0 
            for input_box in input_boxes:
                index += 1
                if input_box.is_selected:
                    input_boxes[index -1].is_selected = False
                    break
            if index < len(input_boxes):
                return index
            else:
                return 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_TAB:
                    index = get_input_index()
                    input_boxes[index].is_selected = True
            for box in input_boxes:
                box.handle_event(event)
            for button in buttons:
                button.handle_event(event)
        screen.fill(black) # Fill the screen with the black color
        
        # This invokes the function draw_button

        # Display column headers with adjusted font size
        width, height =pygame.display.Info().current_w, pygame.display.Info().current_h
        x = width // 2
        y = height // 2 - 150
        font = pygame.font.Font(None, int(30 * width_scale_factor)) # Create font object for header
        text_surface = font.render(' ' + translate_service.get_translation("configureExperiment"), True, light_grey) # Render the text 'Task' with the font and color light_grey
        text_rect = text_surface.get_rect()
        screen.blit(text_surface, (x - text_rect.width // 2, y))
        
        if validate_inputs(input_boxes):
            buttons[1].set_active(True)
            buttons[1].set_color("gray")
        else:
            buttons[1].set_active(False)
            buttons[1].set_color((100, 100, 100))

        for box in input_boxes:
            box.draw(screen)

        for button in buttons:
            button.draw(screen)

        pygame.display.flip()  # Flip the display to update the screen