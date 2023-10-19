import pygame
import pygame_widgets
from pygame.locals import *
import csv
import os
import time
from pygame_widgets.slider import Slider


def leeds(subject, block):
    pygame.init()

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
    
    slider_data = []
    keyboard_data = []
    keyboard_rows = []
    slider_rows = []
    questions = []
    headers = []
    keyboard_filename = os.path.join("./lib", "LeedsKeyboard.csv")
    slider_filename = os.path.join("./lib", "LeedsSlider.csv")
    outdir = "./Logs/Leeds/" + u'%s_%s_leeds.csv' % (subject, block)

    # get all rows except for the header
    with open(keyboard_filename, 'r', encoding="utf8") as csvfile:
        datareader = csv.reader(csvfile)
        row_count = 0
        for row in datareader:
            if row_count == 0:
                for header in row:
                    headers.append(header)
            if row_count > 1:
               keyboard_rows.append(row)
               questions.append(row[1])
            row_count += 1


    keyboard_count = 0
    # keyboard loop
    answer = ""
    second_answer = ""
    is_input_active = False
    is_input2_active = False
    for row in keyboard_rows:
        words = row[1].split(" ")
        labels = [" ".join(words[i:i + 5]) for i in range(0, len(words), 5)]
        text_surfaces = []
        text_rects = []

        multiplicator = 1
        for text in labels:
            text_surface = font.render(text, True, font_color)
            text_rect = text_surface.get_rect(center=(text_x, multiplicator * 40 + text_y))
            text_surfaces.append(text_surface)
            text_rects.append(text_rect)
            multiplicator += 1

        inputs = row[2].split("/")

        input_x = percent_screen_width * 50
        input2_x = percent_screen_width * 60
        if len(inputs) > 1:
            input_x = percent_screen_width * 40

        # render continue buttion
        button_surface = font.render("  Weiter  ", True, (0,0,0))
        button_rect = button_surface.get_rect(center=(percent_screen_width * 50, screen_height /100 * 80))
        
        running = True
    
        while running:
            # Clear the screen
            window.fill(background_color)

            
            if answer:
                answer_input_surface = font.render(answer + " " + (inputs[0][3:]), True, font_color)
            else:
                answer_input_surface = font.render(inputs[0], True, font_color)
            # render continue buttion
            answer_input_rect = answer_input_surface.get_rect(center=(input_x, screen_height /100 * 50))
            
            window.blit(answer_input_surface, answer_input_rect)
            pygame.draw.rect(window, font_color, answer_input_rect, 3)
            pygame.draw.rect(window, font_color, button_rect)
            
            if len(inputs) > 1:
                if second_answer:
                    answer2_input_surface = font.render(second_answer + " " + (inputs[1][3:]), True, font_color)
                else:
                    answer2_input_surface = font.render(inputs[1], True, font_color)
                answer2_input_rect = answer2_input_surface.get_rect(center=(input2_x, screen_height /100 * 50))
                pygame.draw.rect(window, font_color, answer2_input_rect, 3)
                window.blit(answer2_input_surface, answer2_input_rect)
            for i in range(len(text_surfaces)):
                window.blit(text_surfaces[i], text_rects[i])

            window.blit(button_surface, button_rect)

            # update screen
            pygame.display.flip()
            # Process events
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                        return
                    elif event.key == K_BACKSPACE:
                        answer = answer[:-1]
                    elif event.key == K_TAB or event.key == K_KP_ENTER or event.key == K_RETURN:
                        pass
                    elif is_input_active:
                        answer += event.unicode
                    elif is_input2_active:
                        second_answer += event.unicode
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if button_rect.collidepoint(mouse_pos):
                        final_answer = answer
                        if second_answer:
                            final_answer = final_answer + ":" + second_answer
                        keyboard_data.append(final_answer)
                        keyboard_count += 1
                        answer = ""
                        second_answer = ""
                        next_loop = True
                        running = False
                    elif answer_input_rect.collidepoint(mouse_pos):
                        is_input_active = True
                        is_input2_active = False
                    elif len(inputs) > 1:
                        if answer2_input_rect.collidepoint(mouse_pos):
                            is_input2_active = True
                            is_input_active = False
                    else:
                        is_input_active = False
                        is_input2_active = False
            
    # get all rows except for the header
    with open(slider_filename, 'r', encoding="utf8") as csvfile:
        datareader = csv.reader(csvfile)
        row_count = 0
        for row in datareader:
            if row_count == 0:
                for header in row:
                    headers.append(header)
            if row_count > 1:
               slider_rows.append(row)
               questions.append(row[1])
            row_count += 1

    # Slider 
    text_x = screen_width // 2
    line_spacing = 100
    text_y = (screen_height // 6)

    slider = Slider(window, percent_screen_width * 20, round(screen_height / 2), percent_screen_width * 60, 40, min=0, max=100, step=1, handleColour = grey)
    isTouched = False

    # Main loop
    for row in slider_rows:
        words = row[1].split(" ")
        labels = [" ".join(words[i:i + 5]) for i in range(0, len(words), 5)]
        text_surfaces = []
        text_rects = []

        multiplicator = 1
        for text in labels:
            text_surface = font.render(text, True, font_color)
            text_rect = text_surface.get_rect(center=(text_x, multiplicator * 40 + text_y))
            text_surfaces.append(text_surface)
            text_rects.append(text_rect)
            multiplicator += 1

        left_text = row[2]
        left_surface = font.render(left_text, True, font_color)

        right_text = row[3]
        right_surface = font.render(right_text, True, font_color)
        # rener continue buttion
        button_surface = font.render("  " + row[4] + "  ", True, (0,0,0))
        button_rect = button_surface.get_rect(center=(percent_screen_width * 50,
                            screen_height /100 * 80))
        
        running = True

        left_pos = percent_screen_width * 10 + left_surface.get_width() if left_surface.get_width() < percent_screen_width * 10 else percent_screen_width * 10
        right_pos = percent_screen_width * 60 if right_surface.get_width() > percent_screen_width * 10 else percent_screen_width * 80


        while running:
            if not isTouched and slider.getValue() != 50:
                isTouched = True
            # Clear the screen
            window.fill(background_color)
            
            for i in range(len(text_surfaces)):
                window.blit(text_surfaces[i], text_rects[i])
            if isTouched:
                pygame.draw.rect(window, font_color, button_rect)
                window.blit(button_surface, button_rect)
            window.blit(left_surface, (left_pos, screen_height / 2 - line_spacing))
            window.blit(right_surface, (right_pos, screen_height / 2 - line_spacing))

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
                        slider.hide()
                        isTouched = False
                        running = False
                        # update screen
                        slider = Slider(window, percent_screen_width * 20, round(screen_height / 2), percent_screen_width * 60, 40, min=0, max=100, step=1, handleColour = grey)
                slider.listen(event)
                # Calculate slider position
                if event.type == pygame.MOUSEMOTION and event.buttons[0] == 1:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    relative_x = max(min(mouse_x - slider.getX(), slider.getWidth()), 0)
                    normalized_x = relative_x / slider.getWidth()
                    new_value = int(normalized_x * (slider.max - slider.min) + slider.min)
                    slider.setValue(new_value)

    # save if user filled out at least one 1 question
    if len(keyboard_data) > 0:    
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

            writer.writerow([day , month, year, hour, minute, second, subject, block, *keyboard_data, *slider_data])
        
    slider.hide()
