import pygame
import os
import time
import csv

def saliva(subject, experiment,week_number, kss_number):
    current_time = time.strftime("%H:%M:%S")
    # prepare date and time to be saved
    splitted_time = current_time.split(":")
    start_hour = splitted_time[0]
    start_minute = splitted_time[1]
    start_second = splitted_time[2]
    # Open the pygame window at front of all windows open on screen
    os.environ['SDL_VIDEO_WINDOW_POS'] = '0,0'  # Set window position to top-left corner

    # Convert numerical inputs to strings to create the output_filename
    subject_str = str(subject)
    week_number_str = str(week_number)

    # Set title (for output folder)
    TITLE = 'KSS_Results'

    # Define output folder
    out_dir = './Logs'
    # If the output folder does not exist
    if not os.path.exists(out_dir):
        # Print that you are creating the output folder
        print(f"{out_dir} does not exist. Creating now...")
        # Create the output directory
        os.makedirs(out_dir)
                    
    # Define the folder storing kss results
    title_dir = os.path.join(out_dir, TITLE)
    # If the output folder does not exist
    if not os.path.exists(title_dir):
        # Print that you are creating the output folder
        print(f"{title_dir} does not exist. Creating now...")
        # Create the output directory
        os.makedirs(title_dir)    
        
    # Store output file name in variable output_filename
    output_filename = f"KSS_{subject_str}_{experiment}_{week_number_str}.csv"
    
    # Full path for the output file
    output_filename = os.path.join(title_dir, output_filename)

    # Get the screen width and height from the current device in use
    screen_info = pygame.display.Info()
    # Store the screen width in a new variable
    screen_width = screen_info.current_w
    # Store the screen width in a new variable
    screen_height = screen_info.current_h

    # Store the original screen dimensions used to design this program
    original_width = 1280
    original_height = 800

    # Calculate scaling factors for position and size adjustments (this is how we can make sure that the program adjusts to any screen it is executed on)
    width_scale_factor = screen_width / original_width
    height_scale_factor = screen_height / original_height

    # Define the fullscreen window based on current device
    window = pygame.display.get_surface()
    
    # Set the colours to be used
    light_grey = (192, 192, 192)
    black = (0, 0, 0)
    red = (255, 0, 0)
    
    # Set the base font size and calculate the scaled font size
    font_size = screen_width // 40
    font = pygame.font.Font(None, font_size)

    # Define the left side layout (scaled for different screen sizes)
    left_side_x = 100 * width_scale_factor

    # Set the text content
    text_content = "Zeit für die Speichelprobe."

    # Get the text dimensions
    speichelprobe_rendered_line = font.render(text_content, True, light_grey)
    speichelprobe_rendered_line_rect = speichelprobe_rendered_line.get_rect(left=left_side_x, centery=screen_height // 2)
    speichelprobe_text_rendered = [speichelprobe_rendered_line]
    speichelprobe_text_rects = [speichelprobe_rendered_line_rect]

    # Define the title font with underline
    title_font = pygame.font.Font(None, int(30 * min(width_scale_factor, height_scale_factor)))
    title_font.set_underline(True)

    # Set button parameters
    button_text = "Countdown starten"
    button_width = 300 * width_scale_factor
    button_height = 50 * height_scale_factor
    button_x = left_side_x
    button_y = screen_height // 2 + 50 * height_scale_factor
    button_color = light_grey
    button_text_color = black
    button_font = pygame.font.Font(None, (screen_width // 53))

    # Set timer parameters
    timer_duration = 120  # 2 minutes in seconds
    timer_start_time = None
    timer_x = left_side_x
    timer_y = button_y + button_height + 50 * height_scale_factor
    timer_color = red
    timer_font = pygame.font.Font(None, (screen_width // 21))

    # Define the questionnaire content
    title_text = "KSS Fragebogen"
    question_text = "Bitte bewerte deine Müdigkeit in den letzten 10 Minuten,\nindem du die entsprechende Zahl anklickst."
    submission_text_line1 = "Drücke die Leertaste, um deine Antworten an den KSS-Fragebogen zu senden."
    submission_text_line2 = "Dieses Fenster wird geschlossen, wenn der Timer Null erreicht."

    # Define the options
    options = [
        "1. Äusserst wach",
        "2. Sehr wach",
        "3. Normal wach",
        "4. Ziemlich wach",
        "5. Weder wach noch schläfrig",
        "6. Etwas schläfrig",
        "7. Schläfrig, ohne Mühe wach zu bleiben",
        "8. Schläfrig, grosse Mühe wach zu bleiben",
        "9. Äusserst schläfrig, kann nicht wach bleiben"
    ]

    # Define the right side layout
    right_side_x = screen_width // 2 - 40 * width_scale_factor

    # Calculate the position of the title text
    title_x = right_side_x + 70 * width_scale_factor
    title_y = screen_height // 2 - 300 * height_scale_factor

    # Calculate the position of the question text
    question_x = right_side_x + 70 * width_scale_factor
    question_y = screen_height // 2 - 200 * height_scale_factor

    # Calculate the position of the options
    option_x = right_side_x + 100 * width_scale_factor
    option_y = screen_height // 2 - 100 * height_scale_factor

    # Calculate the position of the first line of the submission text
    submission_text_line1_x = right_side_x
    submission_text_line1_y = screen_height - 90 * height_scale_factor

    # Calculate the position of the second line of the submission text
    submission_text_line2_x = right_side_x
    submission_text_line2_y = screen_height - 40 * height_scale_factor
    
    # Calculate the position of the timer
    timer_x = left_side_x + (screen_width // 5)
    timer_y = speichelprobe_text_rects[0].top - 100 * height_scale_factor  # Adjust the value based on your preference

    # Set the selected option to None initially
    selected_option = None

    # Initialize the KSS Fragebogen completion flag
    kss_completed = False

    # Main loop
    running = True # Flag to track the running of the main loop
    timer_started = False  # Flag to track if the timer has started
    display_speichelprobe_text = True  # Flag to control the display of the "Zeit für Speichelprobe" text
    
    while running:
        # Clear the screen
        window.fill(black)

        # Render and display the left side content
        # start a loop that iterates over each item in the speichelprobe_text_rendered list. The enumerate() function is used to retrieve both the index (i) and the corresponding value (text_rendered) for each element in the list.
        if display_speichelprobe_text and not timer_started:
            window.blit(speichelprobe_rendered_line, speichelprobe_rendered_line_rect)
    
        # Render and display the button
        if timer_start_time is None: # If the timer has not yet been started
            if not timer_started: # If the timer has not yet been started
                display_speichelprobe_text = True  # Show the text
                button_rect = pygame.Rect(button_x, button_y, button_width, button_height) # store the button rectangle dimensions in variable button_rect
                pygame.draw.rect(window, button_color, button_rect) # draw the button rectangle
                button_text_rendered = button_font.render(button_text, True, button_text_color) # draw the button text
                button_text_rect = button_text_rendered.get_rect(center=button_rect.center) # draw a rectangle around the button text and position the text in the middle of the button
                window.blit(button_text_rendered, button_text_rect) # Draw the button onto the window
            else:
                display_speichelprobe_text = False  # set the variable to hide the "Zeit für Speichelprobe" text
        else:
            # Render and display the timer
            elapsed_time = pygame.time.get_ticks() - timer_start_time
            remaining_time = max(timer_duration * 1000 - elapsed_time, 0)
            minutes = int(remaining_time / 1000 // 60)
            seconds = int(remaining_time / 1000 % 60)
            if elapsed_time < timer_duration * 1000:
                timer_text = f"{minutes:02d}:{seconds:02d}"
                timer_text_rendered = timer_font.render(timer_text, True, timer_color)
                timer_text_rect = timer_text_rendered.get_rect(center=(timer_x, timer_y))
                window.blit(timer_text_rendered, timer_text_rect)

            if elapsed_time >= timer_duration * 1000:
                if not kss_completed:
                    error = font.render('Bitte fülle den Fragebogen aus', True, timer_color)
                    error_rect = error.get_rect(center=(timer_x, timer_y))
                    window.blit(error, error_rect)
                    error = font.render('und drücke danach die Leertaste', True,
                                        timer_color)
                    error_rect = error.get_rect(center=(timer_x, timer_y + font.get_linesize()))
                    window.blit(error, error_rect)
                if kss_completed:
                    running = False  # Timer reached 0, end the program

        
        # Render and display the right side content
        if not kss_completed:  # Only render if KSS Fragebogen is not completed
            title_text_rendered = font.render(title_text, True, light_grey)
            title_text_rect = title_text_rendered.get_rect(left=title_x, top=title_y)
            window.blit(title_text_rendered, title_text_rect)
            submission_text_font = pygame.font.Font(None, int(20 * min(width_scale_factor, height_scale_factor)))
            submission_text_line1_rendered = submission_text_font.render(submission_text_line1, True, light_grey)
            submission_text_line1_rect = submission_text_line1_rendered.get_rect(center=(submission_text_line1_x, submission_text_line1_y))
            window.blit(submission_text_line1_rendered, submission_text_line1_rect)


            question_lines = question_text.split('\n')
            # start a loop that iterates over each item in the question_lines list. The enumerate() function is used to retrieve both the index (i) and the corresponding value (question_line) for each element in the list.
            for i, line in enumerate(question_lines):
                question_text_rendered = font.render(line, True, light_grey)
                question_text_rect = question_text_rendered.get_rect(left=question_x, top=question_y + i * 30 * height_scale_factor)
                window.blit(question_text_rendered, question_text_rect)

                # start a loop that iterates over the options list. It assigns the index of each item in the list to the variable j and the value of the item to the variable option
                for j, option in enumerate(options):
                    # render the text of each option using a specified font and assigns the rendered text surface to the variable
                    option_text_rendered = font.render(option, True, light_grey)
                    # create a rectangular bounding box for the rendered text
                    option_text_rect = option_text_rendered.get_rect(left=option_x, top=option_y + j * 30 * height_scale_factor)
                    # blit (i.e., draw) the rendered text surface onto the window surface
                    window.blit(option_text_rendered, option_text_rect)
                    # create a rectangle object that represents the tick box for each option
                    tick_box_rect = pygame.Rect(option_x - 30 * width_scale_factor, option_y + j * 30 * height_scale_factor, 20 * width_scale_factor, 20 * height_scale_factor)
                    # draw the tick box rectangle on the window surface
                    pygame.draw.rect(window, light_grey, tick_box_rect, 2)
                    # if the selected_option variable is equal to the option currently being processed in the loop
                    if selected_option == option:
                        # create a list of points that define the shape of the tick mark
                        tick_mark_points = [
                            (option_x - 25 * width_scale_factor, option_y + j * 30 * height_scale_factor + 10 * height_scale_factor),
                            (option_x - 20 * width_scale_factor, option_y + j * 30 * height_scale_factor + 15 * height_scale_factor),
                            (option_x - 15 * width_scale_factor, option_y + j * 30 * height_scale_factor + 5 * height_scale_factor)
                        ]
                        # draw lines connecting the points defined above (draw the tick)
                        pygame.draw.lines(window, light_grey, False, tick_mark_points, 2)

        # Set the font parameters for the submission text - adjust font size depending on which is the smallest factor
        submission_text_font = pygame.font.Font(None, int(20 * min(width_scale_factor, height_scale_factor)))

        # Render and display the submission text lines
        submission_text_line2_rendered = submission_text_font.render(submission_text_line2, True, light_grey)
        submission_text_line2_rect = submission_text_line2_rendered.get_rect(center=(submission_text_line2_x, submission_text_line2_y))
        window.blit(submission_text_line2_rendered, submission_text_line2_rect)

        # Update the display
        pygame.display.flip()

        # Process events
        for event in pygame.event.get(): # retrieve a list of events that have occurred since the last time the event queue was checked
            if event.type == pygame.QUIT: # check if the event is of type pygame.QUIT, which is triggered when the user attempts to close the game window (e.g., by clicking the close button)
                running = False # set the value of the running variable to False
            elif event.type == pygame.KEYDOWN: # check if the event is of type pygame.KEYDOWN, which is triggered when a keyboard key is pressed down
                if event.key == pygame.K_ESCAPE:  # check if the event.key corresponds to the pygame.K_ESCAPE constant, which represents the Escape key on the keyboard
                    running = False # set the value of the running variable to False
                elif event.key == pygame.K_SPACE:  # check if the space key is pressed
                    if selected_option is not None: # check if an option has been chosen to answer the KSS
                        if not kss_completed:  # if the KSS Fragebogen has not yet been completed
                            kss_result = selected_option.split('.')[0].strip() # Save the number (1st position) of the selected option to a variable kss_result
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
                            
                            csv_exists = os.path.isfile(output_filename)
                            # Open the CSV file
                            with open(output_filename, 'a', newline='') as csvfile:
                                writer = csv.writer(csvfile)
                                # Write the header row if this is the first kss (kss number 1) of the night
                                if not csv_exists:
                                    writer.writerow(["Day", "Month", "Year", "Start Hours", "Start Minutes", "Start Seconds", "End Hours", "End Minutes", "End Seconds", 'Subject ID', 'Block', 'KSS Number', 'müdigkeit'])
                                # Write the output to the csv
                                writer.writerow([day, month, year, start_hour, start_minute, start_second, hour, minute, second, subject, week_number_str, kss_number, kss_result])
                            kss_completed = True # Flag that the kss has now been completed
                            
            elif event.type == pygame.MOUSEBUTTONDOWN:  # Check for mouse button click
                if event.button == 1:  # If the left mouse button clicked
                    mouse_pos = pygame.mouse.get_pos() # Store the position of the curser when the mouse was clicked to a variable mouse_pos
                    if button_rect.collidepoint(mouse_pos): # If the cursor position has collided with the start timer button
                        timer_start_time = pygame.time.get_ticks() # log the current time as variable timer_start_time
                        timer_started = True # Flag that the timer has starter in variable timer_started
                        display_speichelprobe_text = False  # Flag that the display text should be set to false in variable display_speichelprobe_text
                    else: # If the cursor position has not collided with the start timer button
                        # start a loop that iterates over each item in the options list. The enumerate() function is used to retrieve both the index (i) and the corresponding value (option) for each element in the list
                        for i, option in enumerate(options):
                            # Create a pygame.Rect object that represents the bounding rectangle for the current option.
                            tick_box_rect = pygame.Rect(option_x - 30 * width_scale_factor, option_y + i * 30 * height_scale_factor, 20 * width_scale_factor, 20 * height_scale_factor)
                            # If the mouse position is within the bounding rectangle of the current option
                            if tick_box_rect.collidepoint(mouse_pos):
                                # Set the selected_option variable to the value of that option
                                selected_option = option

        # Remove the first line of the submission text if the KSS Fragebogen is completed
        if kss_completed:
            title_text_rendered = font.render(title_text, True, light_grey)
            title_text_rect = title_text_rendered.get_rect(left=title_x, top=title_y)
            pygame.draw.rect(window, black, title_text_rect)  # Clear the title text
            # Clear the first line of the submission text
            submission_text_line1_rendered = submission_text_font.render(submission_text_line1, True, light_grey)
            submission_text_line1_rect = submission_text_line1_rendered.get_rect(center=(submission_text_line1_x, submission_text_line1_y))
            pygame.draw.rect(window, black, submission_text_line1_rect)  # Clear the submission text line 1
            
            if timer_started:
                pygame.mouse.set_visible(False)

        # Remove the text content when the timer starts
        if timer_started:
            speichelprobe_text_rendered = []  # Clear the text content list

    # Close the window
    if not kss_completed and selected_option != None:  # if the KSS Fragebogen has not yet been completed
        kss_result = selected_option.split('.')[0].strip() # Save the number (1st position) of the selected option to a variable kss_result
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
        
        csv_exists = os.path.isfile(output_filename)
        # Open the CSV file
        with open(output_filename, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            # Write the header row if this is the first kss (kss number 1) of the night
            if not csv_exists:
                writer.writerow(["Day", "Month", "Year", "Start Hours", "Start Minutes", "Start Seconds", "End Hours", "End Minutes", "End Seconds", 'Subject ID', 'Block', 'KSS Number', 'müdigkeit'])
            # Write the output to the csv
            writer.writerow([day, month, year, start_hour, start_minute, start_second, hour, minute, second, subject, week_number_str, kss_number, kss_result])
        kss_completed = True # Flag that the kss has now been completed
    if not kss_completed and selected_option == None:
        return False
    return True