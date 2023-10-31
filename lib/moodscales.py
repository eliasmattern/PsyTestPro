import pygame
import pygame_widgets
from pygame.locals import *
import csv
import os
import time
from pygame_widgets.slider import Slider

def moodscales(subject, block, experiment):

    # Get the screen width and height
    screen_info = pygame.display.Info()
    screen_width = screen_info.current_w
    screen_height = screen_info.current_h

    # Open a fullscreen window
    window = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)

    # Hide the mouse cursor
    pygame.mouse.set_visible(True)

    # Set the background color
    background_color = (0, 0, 0)  # Black

    # Set text parameters
    font_size = 50
    font = pygame.font.Font(None, font_size)
    font_color = (192, 192, 192) 
    grey = (80, 80, 80)  # Gray

    # text padding
    text_x = screen_width // 2
    line_spacing = 100
    text_y = (screen_height // 6)

    # 1 percent of the screen with
    percent_screen_width = screen_width / 100

    # Slider 
    slider = Slider(window, percent_screen_width * 20, text_y + 2 * line_spacing, percent_screen_width * 60, 40, min=0, max=100, step=1, handleColour = grey)
    
    slider_data = []
    rows = []
    filename = os.path.join("./lib", "MoodscaleSlider.csv")
    outdir = "./Logs/Moodscale_Results/Moodscales_" + u'%s_%s_%s_.csv' % (subject, block, experiment)
    headers = []
    # get all rows except for the header
    with open(filename, 'r', encoding="utf8") as csvfile:
        datareader = csv.reader(csvfile)
        row_count = 0
        for row in datareader:
            if row_count == 0:
                for header in row:
                    headers.append(header)
            if row_count > 1:
               rows.append(row)
            row_count += 1

    count = 0
    # Main loop
    running = True
    isTouched = False
    while count < len(rows) and running:
        if not isTouched and slider.getValue() != 50:
            isTouched = True
        # Clear the screen
        window.fill(background_color)

        # Render question
        title_surface = font.render(rows[count][1], True, font_color)
        title_rect = title_surface.get_rect(center=(text_x, text_y))

        # render slider text
        left_text = rows[count][2].split(",")[0]
        left_surface = font.render(left_text, True, font_color)

        right_text = rows[count][2].split(",")[1]
        right_surface = font.render(right_text, True, font_color)
        
        # rener continue buttion
        button_surface = font.render("  Weiter  ", True, (0,0,0))
        button_rect = button_surface.get_rect(center=(percent_screen_width * 50,
                            screen_height /100 * 80))
        

        window.blit(title_surface, title_rect)
        if isTouched:
            pygame.draw.rect(window, font_color, button_rect)
            window.blit(button_surface, button_rect)
        window.blit(left_surface, (percent_screen_width * 10, text_y + line_spacing))
        window.blit(right_surface, (percent_screen_width * 70, text_y + line_spacing))

        # update screen
        slider.draw()
        pygame.display.flip()

        # Process events
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if button_rect.collidepoint(mouse_pos):
                    slider_data.append(slider.getValue())
                    count += 1
                    isTouched = False
                    slider.hide()
                    # update screen
                    slider = Slider(window, percent_screen_width * 20, text_y + 2 * line_spacing, percent_screen_width * 60, 40, min=0, max=100, step=1, handleColour = grey)
            slider.listen(event)
            # Calculate slider position
            if event.type == pygame.MOUSEMOTION and event.buttons[0] == 1:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                relative_x = max(min(mouse_x - slider.getX(), slider.getWidth()), 0)
                normalized_x = relative_x / slider.getWidth()
                new_value = int(normalized_x * (slider.max - slider.min) + slider.min)
                slider.setValue(new_value)
    # save if user filled out at least one 1 question
    if len(slider_data) > 0:    
        csv_exists = os.path.isfile(outdir)

        with open(outdir, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            if not csv_exists:
                writer.writerow(["Day", "Month", "Year", "Hours", "Minutes", "Seconds", 'SubjectID', 'Block', *headers])
            # Get the current date and time
            current_date = time.strftime("%Y-%m-%d")
            current_time = time.strftime("%H:%M:%S")
            # prepare date and time to be saved
            splitted_date = current_date.split("-")
            day = splitted_date[2]
            month = splitted_date[1]
            year = splitted_date[0]
            splitted_time = current_time.split(":")
            hour = splitted_time[0]
            minute = splitted_time[1]
            second = splitted_time[2]

            writer.writerow([day , month, year, hour, minute, second, subject, block, *slider_data])
    slider.hide()
        

