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

selected_multiple = False
page = 0

def backToTeststarter(teststarter):
    teststarter()
    global selected_multiple
    selected_multiple = False

def back(teststarter, translate_service):
    experiment_config_display(teststarter, translate_service)
    global selected_multiple
    selected_multiple = False

def save_experiment(teststarter, experiment_name, experiment_time_of_day, translate_service):
    global selected_multiple
    
    teststarter_config = TeststarterConfig()
    teststarter_config.save_experiment(experiment_name, experiment_time_of_day)

    if selected_multiple:
        create_experiment_config_display(teststarter, translate_service, selected_multiple)
    else:    
        backToTeststarter(teststarter)
    
def delete_experiment(teststarter, translate_service, experiment_name):

    root = tk.Tk()
    root.withdraw()

    # Show a messagebox asking for confirmation
    response = messagebox.askyesno(translate_service.get_translation("delete"), translate_service.get_translation("deleteExperimentMsg") + experiment_name)

    # If the user clicked 'Yes', then open browser
    if response == True:
        # Load the original JSON from the file
        with open('json/taskConfig.json', 'r') as file:
            original_tasks = json.load(file)

        # Add a new variable with an empty task object
        exp_keys = [key for key in original_tasks.keys() if experiment_name in key]

        if len(exp_keys) > 1:
            root = tk.Tk()
            root.withdraw()

            # Show a messagebox asking for confirmation
            response = messagebox.askyesno(translate_service.get_translation("delete"), translate_service.get_translation("deleteMultipleExperimentMsg"))

            # If the user clicked 'Yes', then open browser
            if response == True:
                with open('json/experimentConfig.json', 'r') as file:
                    original_experiments = json.load(file)

                # Add a new value to the array
        
                original_experiments.remove(experiment_name)

                # Save the updated array back to the file
                with open('json/experimentConfig.json', 'w') as file:
                    json.dump(original_experiments, file)
                for key in exp_keys:
                    del original_tasks[key]
            
            else:
                times_said_yes = 0
                for exp in exp_keys:
                    root = tk.Tk()
                    root.withdraw()

                    splitted_exp_name = exp.split("_")
                    exp_name = splitted_exp_name[1]
                    time_of_day = splitted_exp_name[0]
                    # Show a messagebox asking for confirmation
                    response = messagebox.askyesno(translate_service.get_translation("delete"), 
                                                   translate_service.get_translation("deleteExperimentMsg") + exp_name + " " 
                                                   + translate_service.get_translation("timeOfDayShort") + ": " + time_of_day)
        
                    # If the user clicked 'Yes', then open browser
                    if response == True:
                        del original_tasks[exp]
                        times_said_yes += 1
                if times_said_yes == len(exp_keys):
                    with open('json/experimentConfig.json', 'r') as file:
                        original_experiments = json.load(file)

                    # Add a new value to the array

                    original_experiments.remove(experiment_name)

                    # Save the updated array back to the file
                    with open('json/experimentConfig.json', 'w') as file:
                        json.dump(original_experiments, file)
                   
        else:
            del original_tasks[exp_keys[0]]
            with open('json/experimentConfig.json', 'r') as file:
                original_experiments = json.load(file)

            # Add a new value to the array
        
            original_experiments.remove(experiment_name)

            # Save the updated array back to the file
            with open('json/experimentConfig.json', 'w') as file:
                json.dump(original_experiments, file)

        # Save the updated JSON back to the file
        with open('json/taskConfig.json', 'w') as file:
            json.dump(original_tasks, file, indent=4)
        # Destroy the root window
        root.destroy()
        delete_experiment_config_display(teststarter, translate_service)
    else:
        root.destroy()

def create_input_boxes(teststarter, translate_service, selected_multiple):
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

    exit_button = Button(x - 75, y + 60, 100, 40, "back", lambda: back(teststarter, translate_service), translate_service)
    submit_button = Button(x + 75, y + 60, 100, 40, "submit", lambda: save_experiment(teststarter, input_boxes[0].text, input_boxes[1].text, translate_service), translate_service)
   
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

def validate_task_inputs(input_boxes, time_input, command_inputs, text_screen_inputs, is_command):
    is_valid = False
    
    if input_boxes[0].text and time_input.time:
        if command_inputs and  command_inputs[0].text:
            is_valid = True

        if not command_inputs and text_screen_inputs[0].text and text_screen_inputs[1].text:
            is_valid = False

    return is_valid

def create_experiment_config_display(teststarter, translate_service, create_continously = False):
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
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
    
    # Setting the window caption
    pygame.display.set_caption('Create Experiment')

    global selected_multiple
    selected_multiple = create_continously

    input_boxes, buttons = create_input_boxes(teststarter, translate_service, selected_multiple)

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
    width, height =pygame.display.Info().current_w, pygame.display.Info().current_h
    x = width // 2
    y = height // 2 - 150

    question_font = pygame.font.Font(None, int(24 * width_scale_factor)) # Create font object for header
    option_text_rendered = question_font.render(translate_service.get_translation("createMultipleExperiments"), True, light_grey)
    option_text_rect = option_text_rendered.get_rect(left=x + 180, top=y + 240 )
    tick_box_rect = pygame.Rect(x + 170 - 20 * height_scale_factor , y + 240 , 20 * width_scale_factor, 20 * height_scale_factor)

    font = pygame.font.Font(None, int(30 * width_scale_factor)) # Create font object for header
    text_surface = font.render(translate_service.get_translation("createExperiment"), True, light_grey) # Render the text 'Task' with the font and color light_grey
    text_rect = text_surface.get_rect()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_TAB:
                    index = get_input_index()
                    input_boxes[index].is_selected = True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # If the left mouse button clicked
                    mouse_pos = pygame.mouse.get_pos() # Store the position of the curser when the mouse was clicked to a variable mouse_pos
                    if tick_box_rect.collidepoint(mouse_pos): # If the cursor position has collided with the start timer button
                        selected_multiple = not selected_multiple
            for box in input_boxes:
                box.handle_event(event)
            for button in buttons:
                button.handle_event(event)
        screen.fill(black) # Fill the screen with the black color
        
        screen.blit(option_text_rendered, option_text_rect)
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
        
        # draw the tick box rectangle on the window surface
        pygame.draw.rect(screen, light_grey, tick_box_rect, 2)
        # if the selected_multiple variable is equal to the option currently being processed in the loop
        if selected_multiple:
            # create a list of points that define the shape of the tick mark
            tick_mark_points = [
                (x + 180 - 25* height_scale_factor , y + 240  + 10* height_scale_factor ),
                (x + 180 - 20* height_scale_factor , y + 240  + 15* height_scale_factor ),
                (x + 180 - 15* height_scale_factor , y + 240  + 5 * width_scale_factor )
            ]
            # draw lines connecting the points defined above (draw the tick)
            pygame.draw.lines(screen, light_grey, False, tick_mark_points, 2)

        pygame.display.flip()  # Flip the display to update the screen

def delete_experiment_config_display(teststarter, translate_service):

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
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
    
    # Setting the window caption
    pygame.display.set_caption('Delete Experiment')

    teststarter_config.load_experiments()
    experiments = teststarter_config.experiments    
    splitted_experiments = [experiments[i:i+5] for i in range(0, len(experiments), 5)]

    global page
    page = 0

    def page_update(increment): 
        global page
        if increment:
            page = (page + 1) % len(splitted_experiments)
        else:
            page = (page - 1) if page > 0 else len(splitted_experiments) - 1

    while True:
        screen.fill(black) # Fill the screen with the black color

        buttons = []
    
        spacing = 0
        width, height =pygame.display.Info().current_w, pygame.display.Info().current_h

        x = width // 2
        y = height // 2 - 150

        for experiment in splitted_experiments[page]:
            exp_button = Button(x, y + 60 + spacing, 400, 40, experiment, lambda exp = experiment: delete_experiment(teststarter, translate_service, exp))
            buttons.append(exp_button)
            spacing += 60

        spacing = 5 * 60
        spacing += 60
        back_button = Button(x, y + spacing + 100, 100, 40, "back", lambda: back(teststarter, translate_service), translate_service)
        buttons.append(back_button)

        if len(splitted_experiments) > 1:
            page_font = pygame.font.Font(None, int(24 * width_scale_factor)) 
            page_text_surface = page_font.render(str(page + 1) + "/" + str(len(splitted_experiments)), True, light_grey)
            page_rect = page_text_surface.get_rect()
            screen.blit(page_text_surface, (x - page_rect.width // 2, y + 100 + spacing - 60))
            previous_page_button = Button(x-40, y + 100 + spacing - 60 , 25, 25, "<", lambda: page_update(False))
            next_page_back_button = Button(x+40, y + 100 + spacing - 60, 25, 25, ">", lambda: page_update(True))
            buttons.append(previous_page_button)
            buttons.append(next_page_back_button)
        
        # This invokes the function draw_button

        # Display column headers with adjusted font size
        width, height =pygame.display.Info().current_w, pygame.display.Info().current_h
        x = width // 2
        y = height // 2 - 150
        font = pygame.font.Font(None, int(30 * width_scale_factor)) # Create font object for header
        text_surface = font.render(translate_service.get_translation("deleteExperiment"), True, light_grey) # Render the text 'Task' with the font and color light_grey
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

def save_task(teststarter, translate_service, create_continously, experiment, time_of_day, variable, name, time, command = None, title = None, description = None, is_command= False):
    type = "text" if not is_command else "command"
    value = {"title": title, "description": description} if not is_command else command
    teststarter_Config = TeststarterConfig()
    teststarter_Config.save_task(variable, name, time, type, value)
    if create_continously:
        add_task(teststarter, translate_service, create_continously, experiment, time_of_day)
    else:
        add_task_config_display(teststarter, translate_service)

def add_task(teststarter, translate_service, create_continously, experiment, time_of_day):
    variable = time_of_day + "_" + experiment + "_variable"
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
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
    
    # Setting the window caption
    pygame.display.set_caption('Create Task')

    global selected_multiple
    selected_multiple = create_continously

    input_boxes = []
    buttons = []
    text_screen_inputs = []
    command_inputs = []
    command_labels = ["command"]
    text_labels = ["title", "description"]
    spacing = 60
    width, height =pygame.display.Info().current_w, pygame.display.Info().current_h
    x = width // 2
    y = height // 2 - 100
    input_box = InputBox(x, y, 400, 40, "taskName", translate_service, allow_new_line=False)
    input_boxes.append(input_box)
    y += spacing
    time_input = TimeInput(x, y, 400, 40, "timeForTask", translate_service)
    y += spacing + spacing
    for label in text_labels:
        input_box = InputBox(x, y, 400, 40, label, translate_service, allow_new_line=True)
        text_screen_inputs.append(input_box)
        y += spacing
    y = height // 2 - 100 + 3 * spacing
    for label in command_labels:
        input_box = InputBox(x, y, 400, 40, label, translate_service, allow_new_line=False)
        command_inputs.append(input_box)
        y += spacing
    y += spacing
    exit_button = Button(x - 75, y + 60, 100, 40, "back", lambda: back(teststarter, translate_service), translate_service)
    submit_button = Button(x + 75, y + 60, 100, 40, "submit", lambda: save_task(teststarter, translate_service, selected_multiple, experiment, time_of_day, variable, input_boxes[0].text, time_input.time, command_inputs[0].text, text_screen_inputs[0].text, text_screen_inputs[1].text, command), translate_service)
   
    buttons.append(time_input)
    buttons.append(exit_button)
    buttons.append(submit_button)

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
    width, height =pygame.display.Info().current_w, pygame.display.Info().current_h
    x = width // 2
    y = height // 2 - 150

    question_font = pygame.font.Font(None, int(24 * width_scale_factor)) # Create font object for header
    option_text_rendered = question_font.render(translate_service.get_translation("createMultipleTasks"), True, light_grey)
    option_text_rect = option_text_rendered.get_rect(left=x + 180, top=y + 360 )
    tick_box_rect = pygame.Rect(x + 170 - 20 * height_scale_factor , y + 360 , 20 * width_scale_factor, 20 * height_scale_factor)

    font = pygame.font.Font(None, int(30 * width_scale_factor)) # Create font object for header
    text_surface = font.render(translate_service.get_translation("createTask") + " for " + experiment + " " + time_of_day, True, light_grey) # Render the text 'Task' with the font and color light_grey
    text_rect = text_surface.get_rect()

    text_screen = True
    command = False

    text_screen_rendered = question_font.render(translate_service.get_translation("textScreen"), True, light_grey)
    text_screen_rect = text_screen_rendered.get_rect(left=x - 300, top=y + 180 )
    text_tick_box_rect = pygame.Rect(x - 315 - 20 * height_scale_factor , y + 180 , 20 * width_scale_factor, 20 * height_scale_factor)

    command_screen_rendered = question_font.render(translate_service.get_translation("command"), True, light_grey)
    command_screen_rect = command_screen_rendered.get_rect(left=x + 100, top=y + 180 )
    command_tick_box_rect = pygame.Rect(x + 85 - 20 * height_scale_factor , y + 180 , 20 * width_scale_factor, 20 * height_scale_factor)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_TAB:
                    index = get_input_index()
                    input_boxes[index].is_selected = True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # If the left mouse button clicked
                    mouse_pos = pygame.mouse.get_pos() # Store the position of the curser when the mouse was clicked to a variable mouse_pos
                    if tick_box_rect.collidepoint(mouse_pos): # If the cursor position has collided with the start timer button
                        selected_multiple = not selected_multiple
                    if text_tick_box_rect.collidepoint(mouse_pos): # If the cursor position has collided with the start timer button
                        text_screen = not text_screen
                        command = not command
                    if command_tick_box_rect.collidepoint(mouse_pos): # If the cursor position has collided with the start timer button
                        text_screen = not text_screen
                        command = not command
            for box in input_boxes:
                box.handle_event(event)
            for box in text_screen_inputs:
                box.handle_event(event)
            for box in command_inputs:
                box.handle_event(event)
            for button in buttons:
                button.handle_event(event)
        screen.fill(black) # Fill the screen with the black color
        
        screen.blit(option_text_rendered, option_text_rect)
        screen.blit(text_surface, (x - text_rect.width // 2, y))
        
        if validate_task_inputs(input_boxes, time_input, command_inputs, text_screen_inputs, command):
            buttons[2].set_active(True)
            buttons[2].set_color("gray")
        else:
            buttons[2].set_active(False)
            buttons[2].set_color((100, 100, 100))

        for box in input_boxes:
            box.draw(screen)
        if command:
            for box in command_inputs:
                box.draw(screen)
        if text_screen:
            for box in text_screen_inputs:
                box.draw(screen)

        for button in buttons:
            button.draw(screen)
        
        # draw the tick box rectangle on the window surface
        pygame.draw.rect(screen, light_grey, tick_box_rect, 2)
        pygame.draw.rect(screen, light_grey, text_tick_box_rect, 2)
        pygame.draw.rect(screen, light_grey, command_tick_box_rect, 2)
        # if the selected_multiple variable is equal to the option currently being processed in the loop
        if selected_multiple:
            # create a list of points that define the shape of the tick mark
            tick_mark_points = [
                (x + 180 - 25* height_scale_factor , y + 360  + 10* height_scale_factor ),
                (x + 180 - 20* height_scale_factor , y + 360  + 15* height_scale_factor ),
                (x + 180 - 15* height_scale_factor , y + 360  + 5 * width_scale_factor )
            ]
            # draw lines connecting the points defined above (draw the tick)
            pygame.draw.lines(screen, light_grey, False, tick_mark_points, 2)


        screen.blit(text_screen_rendered, text_screen_rect)

        if text_screen:
            # create a list of points that define the shape of the tick mark
            text_tick_mark_points = [
                (x - 300 - 25* height_scale_factor , y + 180  + 10* height_scale_factor ),
                (x - 300 - 20* height_scale_factor , y + 180  + 15* height_scale_factor ),
                (x - 300 - 15* height_scale_factor , y + 180  + 5 * width_scale_factor )
            ]

            # draw lines connecting the points defined above (draw the tick)
            pygame.draw.lines(screen, light_grey, False, text_tick_mark_points, 2)
        
        screen.blit(command_screen_rendered, command_screen_rect)

        if command:
            # create a list of points that define the shape of the tick mark
            command_tick_mark_points = [
                (x + 100 - 25* height_scale_factor , y + 180  + 10* height_scale_factor ),
                (x + 100 - 20* height_scale_factor , y + 180  + 15* height_scale_factor ),
                (x + 100 - 15* height_scale_factor , y + 180  + 5 * width_scale_factor )
            ]

            # draw lines connecting the points defined above (draw the tick)
            pygame.draw.lines(screen, light_grey, False, command_tick_mark_points, 2)

        pygame.display.flip()  # Flip the display to update the screen

def add_task_config_display(teststarter, translate_service):
    global page
    page = 0
    def split_dict(input_dict, chunk_size):
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
    def page_update(increment): 
        global page
        if increment:
            page = (page + 1) % len(splitted_experiments)
        else:
            page = (page - 1) if page > 0 else len(splitted_experiments) - 1

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
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
    
    # Setting the window caption
    pygame.display.set_caption('Add task')

    experiments_and_day_of_times = teststarter_config.get_experiment_and_time_of_day() 
    splitted_experiments = split_dict(experiments_and_day_of_times, 5)

    

    while True:
        screen.fill(black) # Fill the screen with the black color

        buttons = []
    
        spacing = 0
        width, height =pygame.display.Info().current_w, pygame.display.Info().current_h

        x = width // 2
        y = height // 2 - 150

        for key, experiment in splitted_experiments[page].items():
            exp_button = Button(x, y + 60 + spacing, 400, 40, experiment.get("experiment") + " " + experiment.get("time_of_day"), 
                                lambda exp = experiment: add_task(teststarter, translate_service, False, exp.get("experiment"),  exp.get("time_of_day")))
            buttons.append(exp_button)
            spacing += 60

        spacing = 5 * 60
        spacing += 60
        back_button = Button(x, y + spacing + 100, 100, 40, "back", lambda: back(teststarter, translate_service), translate_service)
        buttons.append(back_button)

        if len(splitted_experiments) > 1:
            page_font = pygame.font.Font(None, int(24 * width_scale_factor)) 
            page_text_surface = page_font.render(str(page + 1) + "/" + str(len(splitted_experiments)), True, light_grey)
            page_rect = page_text_surface.get_rect()
            screen.blit(page_text_surface, (x - page_rect.width // 2, y + 100 + spacing - 60))
            previous_page_button = Button(x-40, y + 100 + spacing - 60 , 25, 25, "<", lambda: page_update(False))
            next_page_back_button = Button(x+40, y + 100 + spacing - 60, 25, 25, ">", lambda: page_update(True))
            buttons.append(previous_page_button)
            buttons.append(next_page_back_button)
        
        # This invokes the function draw_button

        # Display column headers with adjusted font size
        width, height =pygame.display.Info().current_w, pygame.display.Info().current_h
        x = width // 2
        y = height // 2 - 150
        font = pygame.font.Font(None, int(30 * width_scale_factor)) # Create font object for header
        text_surface = font.render(translate_service.get_translation("createTask"), True, light_grey) # Render the text 'Task' with the font and color light_grey
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

def experiment_config_display(teststarter, translate_service, create_continously = False):
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
    pygame.display.set_caption('Configure Experiment')

    buttons = []
    spacing = 0
    width, height =pygame.display.Info().current_w, pygame.display.Info().current_h

    x = width // 2
    y = height // 2 - 150

    back_button = Button(x, y + 240, 100, 40, "back", lambda: backToTeststarter(teststarter), translate_service)
    create_experiment_button = Button(x, y + 60 + spacing, 400, 40, "createExperiment", lambda: create_experiment_config_display(teststarter, translate_service, create_continously), translate_service)
    spacing += 60
    delete_button = Button(x, y + 60 + spacing, 400, 40, "deleteExperiment", lambda: delete_experiment_config_display(teststarter, translate_service), translate_service)
    spacing += 60
    create_task_button = Button(x, y + 60 + spacing, 400, 40, "createTask", lambda: add_task_config_display(teststarter, translate_service), translate_service)

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
        screen.fill(black) # Fill the screen with the black color

        for button in buttons:
            button.draw(screen)

        font = pygame.font.Font(None, int(30 * width_scale_factor)) # Create font object for header
        text_surface = font.render(translate_service.get_translation("configureExperiment"), True, light_grey) # Render the text 'Task' with the font and color light_grey
        text_rect = text_surface.get_rect()
        screen.blit(text_surface, (x - text_rect.width // 2, y))
        

        pygame.display.flip()  # Flip the display to update the screen
