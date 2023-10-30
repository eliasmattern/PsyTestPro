# Full working Version. PRACTICE AND REAL SESSIONS OF THE N-Back task saving and running properly. 
#Practice 1, Session 1, Practice 2, Session 2, Practice 3, Session 3


#make one new definition containing practice and real session! in this defintion I need to alterate it and practice session first. 
# the real can run 3 times but has to have the definition of the pracitce session in it. and needs to get the information from the real nback. 

import pygame
import random
import sys
import os
import csv
import time


#subject = 102
#week = 1
#study_night = 'Hab'

# This function calculates the fraction of matching letters in a given sequence, based on a specified number of letters to look back (num_back).
def calculate_match_fraction(sequence, num_back):
    match_count = 0

    # Iterating over the sequence starting from the num_back-th index.
    for i in range(num_back, len(sequence)):
        current_letter = sequence[i]
        previous_letter = sequence[i - num_back]

        # Checking if the current letter matches the letter num_back positions before it.
        if current_letter == previous_letter:
            match_count += 1

    # Calculating the match fraction by dividing the number of matches by the total number of comparisons.
    match_fraction = match_count / (len(sequence))

    print(match_fraction)
    return match_fraction

# This function generates a sequence of letters with specified parameters: num_trials (length of the sequence) and num_back (number of letters to look back).
def generate_nback_sequence(num_trials, num_back):
    letters = ['J', 'L', 'H', 'T', 'S', 'M', 'F', 'R', 'K']
    sequence = []

    while True:
        sequence = []

        # Generating a random sequence of letters with the specified length.
        for _ in range(num_trials):
            sequence.append(random.choice(letters))

        try:
            # Selecting a subset of indices in the sequence where matches will be inserted.
            match_indices = random.sample(range(num_trials - num_back + 1), num_trials // 3)

            # Making the selected indices match the letter num_back positions before them.
            for i in match_indices:
                target_index = i + num_back
                sequence[target_index] = sequence[i]

            # Calculating the match fraction for the generated sequence.
            match_fraction = calculate_match_fraction(sequence, num_back)

            # Checking if the match fraction falls within the desired range.
            if match_fraction == 0.3:
                break  # Break out of the loop if a valid sequence with the desired match_fraction is obtained

        except IndexError:
            pass  # Ignore the error and continue to generate a new sequence

    # Printing the generated sequence and returning it.
    print(sequence)
    return sequence



#########################################################################################
def practice_nback(subject, experiment, week, study_night, current_block, num_back, num_back_addition, num_back_performance_addition):
    # Initialise variables is going to be problematic when creating a loop later! putting it above the definition didnt' help.
    #num_back = 2
    #num_back_addition = None
    #num_back = num_back + num_back_performance_addition

    # Always open the pygame window at front of all windows open on screen
    os.environ['SDL_VIDEO_WINDOW_POS'] = '0,0'  # Set window position to top-left corner

    # Initialize Pygame
    pygame.init()

    # Set the display mode and get the screen dimensions
    screen_info = pygame.display.Info()
    screen_width = screen_info.current_w
    screen_height = screen_info.current_h

    # Define the colors
    black = (0, 0, 0)
    white = (255, 255, 255)

    # Initialize the game window
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN | pygame.NOFRAME)  # Use pygame.FULLSCREEN flag

    pygame.display.set_caption("N-Back Task")

    clock = pygame.time.Clock()

    # Hide the mouse cursor
    pygame.mouse.set_visible(False)


    # Define the experiment parameters
    letter_duration = 2000  # in milliseconds
    blank_duration = 1000  # in milliseconds
    num_trials = 10  # Number of letters to be presented (10)
    #total_num_blocks = 3  # Number of blocks to be run (3)
    #current_block = 1 # Initialise the current block (NEW)
    
    # Load the images
    correct_image = pygame.image.load("./lib/Correct.png")
    incorrect_image = pygame.image.load("./lib/Incorrect.png")
    
    # Create a saving mechanism
    
    # Create strings for file saving purposes
    subject_str = str(subject)
    week_str = str(week)
    study_night_str = str(study_night)
    
    # Title (for outputs)
    TITLE = 'N-Back_Practice_Results'

    # Check if output directory exists #'C:/Users/noemi/Desktop/teststarter_python/Logs'
    out_dir = './Logs'
    if not os.path.exists(out_dir):
        print("Output directory does not exist. Creating now...")
        os.makedirs(out_dir)

    # Define the title directory (a folder in logs called "NBack results")
    title_dir = os.path.join(out_dir, TITLE)
    if not os.path.exists(title_dir):
        print(f"{title_dir} does not exist. Creating now...")
        os.makedirs(title_dir)   

    # Output file name
    output_filename = f"NBackPractice_{subject_str}_{week_str}_{experiment}_{study_night_str}_{TITLE}.csv"

    # Full path for the output file
    output_filename = os.path.join(title_dir, output_filename)

    # Open the output CSV file for writing
    with open(output_filename, 'a', newline='') as csvfile:
        # Create a CSV writer object
        writer = csv.writer(csvfile, delimiter = ',')
        # Write the header row
        writer.writerow(['Subject ID', "Day", "Month", "Year", "Hours", "Minutes", "Seconds", 'Num-Back', 'Block', 'Current Trial', 'Current Letter', 'Back Letter', 'Response Time', 'User Input', 'Result'])
    

        #NC 27.7 commented out: while current_block <= total_num_blocks: (&inserted the following line)
        while True:
            # Define the introduction screen texts
            first_screen_intro_texts = [
                f"Du wirst nun eine Übungsaufgabe {num_back}-BACK durchführen.",
                "Das heißt, dass du den gerade gezeigten Buchstaben mit jenem vergleichst",
                f"den du {num_back} Buchstaben zuvor gesehen hast.",
                "Bitte beachte, dass du nach JEDEM Buchstaben eine Entscheidung treffen,",
                "also eine Taste drücken sollst.",
                'Drücke die Taste "A", wenn der aktuelle Buchstabe nicht derselbe ist',
                'und die Taste "L", wenn es derselbe Buchstabe ist,'f" den du {num_back} Buchstaben zuvor gesehen hast.",
                "Bitte platziere jetzt deine linken und rechten Zeigefinger auf diesen Tasten.",
                "",
                "",
                "Drücke Taste A oder L, um fortzufahren"
            ]

            second_screen_intro_texts = [
                "Die folgenden Durchgänge sollen dich mit der Aufgabe vertraut machen.",
                "Das heißt, dass weniger Buchstaben gezeigt werden und du länger Zeit hast,",
                "um eine Antwort abzugeben.",
                "Zudem wird es nach jeder Entscheidung eine kurze Rückmeldung geben.",
                "",
                "",
                "Drücke Taste A oder L, um mit den Übungsdurchgängen zu beginnen."
            ]
            # Render the text surfaces and create rectangles for each line of text
            font_size = 32
            intro_font = pygame.font.Font(None, 30)

            screen_text_surfaces = []
            screen_text_rects = []
            line_height = 50  # Adjust this value to control the vertical spacing between lines

            screen.fill(pygame.Color("black"))  # Clear the screen

            # Visualize first screen text
            for index, text in enumerate(first_screen_intro_texts):
                intro_text_surface = intro_font.render(text, True, pygame.Color("white"))
                intro_text_rect = intro_text_surface.get_rect(center=(screen_width // 2, (screen_height // 2 - 200) + (index * line_height)))
                screen_text_surfaces.append(intro_text_surface)
                screen_text_rects.append(intro_text_rect)

            for index in range(len(screen_text_surfaces)):
                screen.blit(screen_text_surfaces[index], screen_text_rects[index])

            pygame.display.flip()

            # Wait for a key press to continue
            key_pressed = False
            while not key_pressed:
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            return
                        elif event.key in [pygame.K_a, pygame.K_l]:
                            key_pressed = True

            # Clear the screen
            screen.fill(pygame.Color("black"))

            # Render the text surfaces and create rectangles for each line of text
            screen_text_surfaces = []
            screen_text_rects = []

            # Visualize second screen text
            for index, text in enumerate(second_screen_intro_texts):
                intro_text_surface = intro_font.render(text, True, pygame.Color("white"))
                intro_text_rect = intro_text_surface.get_rect(center=(screen_width // 2, (screen_height // 2 - 200) + (index * line_height)))
                screen_text_surfaces.append(intro_text_surface)
                screen_text_rects.append(intro_text_rect)

            for index in range(len(screen_text_surfaces)):
                screen.blit(screen_text_surfaces[index], screen_text_rects[index])

            pygame.display.flip()

            # Wait for a key press to continue
            key_pressed = False
            while not key_pressed:
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            return
                        elif event.key in [pygame.K_a, pygame.K_l]:
                            key_pressed = True

            # Clear the screen
            screen.fill(black)
            pygame.mouse.set_visible(False)
            pygame.display.flip()
            pygame.time.wait(500)

            # Define the sequence of letters
            sequence = generate_nback_sequence(num_trials, num_back)

            # Initialize variables for tracking letters and user input
            current_trial = 0
            previous_letters = []
            # user_input = None
            back_letter = None
            result = None
            result_list = []
            feedback = None
            feedback_image = None
            response_time = ""

            # Main game loop
            running = True
            while running:
                # Check for quit event
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            running = False

                # Play a new trial only if the total number of trials have not yet been reached
                if current_trial < num_trials:
                    # Store back_letter variable if there is a back_letter for the number of backs the trial is set for
                    if current_trial >= num_back:
                        back_letter = sequence[current_trial - num_back]
                    else:
                        back_letter = None  # Handle the case when not enough backs are available
                    # Clear user_input
                    user_input = None # (NEW)
                    # Select the next letter in the sequence
                    current_letter = sequence[current_trial]
                    # Clear the screen
                    screen.fill(black)
                    # Configure the letter visualisation
                    font = pygame.font.Font(None, int(screen_height / 5))
                    text = font.render(current_letter, True, white)
                    text_rect = text.get_rect(center=(screen_width // 2, screen_height // 2))
                    screen.blit(text, text_rect)
                    # Display the letter
                    pygame.display.flip()
                    # Set the start time for the letter display
                    start_time = pygame.time.get_ticks()
                    reaction_start_time = time.time()
                    # Process user input during letter display
                    while pygame.time.get_ticks() < start_time + letter_duration:
                        if current_trial >= num_back:
                            for event in pygame.event.get():
                                if event.type == pygame.KEYDOWN:
                                    if event.key == pygame.K_a:
                                        response_time = (time.time() - reaction_start_time) 
                                        user_input = "No Match"
                                    elif event.key == pygame.K_l:
                                        response_time = (time.time() - reaction_start_time)
                                        user_input = "Match"
                                        

                    # Set the start time for the letter display
                    start_time = pygame.time.get_ticks()
                    # Continue only once the letter duration has passed
                    if pygame.time.get_ticks() < start_time + blank_duration:
                        # Only process inputs if there are enough trials that a back_letter exists for comparison
                        if current_trial >= num_back:
                            # Compare the current_letter with the letter displayed n steps back
                            if current_letter == back_letter:  # If the current letter is the same as the n-back letter
                                if user_input == "Match":
                                    result = "Correct"
                                elif user_input == "No Match":
                                    result = "Incorrect"
                                else: 
                                    user_input == "No Input"
                                    result = "No Input"
                            else:  # If the current letter is different from the n-back letter
                                if user_input == "No Match":
                                    result = "Correct"
                                elif user_input == "Match":
                                    result = "Incorrect"
                                else:
                                    user_input == "No Input"
                                    result = "No Input"

                            result_list.append(result)
                            # Provide feedback based on the result

                            if result == "Correct":
                                feedback = "Richtig!"
                                feedback_image = correct_image
                            elif result == "Incorrect":
                                feedback = "Falsch!"
                                feedback_image = incorrect_image
                            else: 
                                feedback = "Keine Eingabe erfasst"
                                feedback_image = incorrect_image

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

                            # Write the data to the CSV file
                            writer.writerow([subject, day , month, year, hour, minute, second, num_back, current_block, current_trial, current_letter, back_letter, response_time, user_input, result])

                            # Print variables
                            print(f"current block: {current_block} |no of trials: {num_trials} |current trial: {current_trial} | current letter: {current_letter} | back letter: {back_letter} | user input: {user_input} | result: {result} ") 

                            # Clear the screen
                            screen.fill(black)
                            # Render the feedback text
                            font = pygame.font.Font(None, 72)
                            feedback_text = font.render(feedback, True, white)
                            feedback_text_rect = feedback_text.get_rect(center=(screen_width // 2, screen_height // 2))
                            screen.blit(feedback_text, feedback_text_rect)
                            # Blit the feedback image onto the screen
                            image_rect = feedback_image.get_rect(center=(screen_width // 2, screen_height // 2 - 150))
                            screen.blit(feedback_image, image_rect)
                            pygame.display.flip()
                            pygame.time.wait(blank_duration)
                            #if it is the last letter final letter in sequence then after feedback, 
                            if current_trial == num_trials - 1:
                            #if current_trial + num_back == num_trials :
                                # Evaluate performance
                                correct_count = result_list.count("Correct")
                                performance = correct_count/(num_trials - num_back)*100
                                print("result list: ", result_list)
                                print("correct count: ", correct_count)
                                print("performance: ", performance)
                                print("block: ", current_block)
                                #if performance >= 90:
                                #    num_back_performance_addition = 1
                                #elif performance < 70:
                                #    if num_back == 1:
                                #        num_back_performance_addition = 0
                                #    else:
                                #        num_back_performance_addition = -1
                                #else:
                                #    num_back_performance_addition = 0

                                #num_back = num_back + num_back_performance_addition
                                print("num_back: ", num_back)
                                # exit the letter-feedback loop to go to end of block feedback before beginning next block
                                running = False

                        # If current trial is < num_back (where feedback is not needed) just show a blank screen
                        else:
                            # Clear the screen
                            screen.fill(black)
                            pygame.display.flip()
                            pygame.time.wait(blank_duration)

                            # Get the current date and time
                            current_date = time.strftime("%Y-%m-%d")
                            current_time = time.strftime("%H:%M:%S")
                            print("date")
                            print(current_date)
                            # prepare date and time to be saved
                            splitted_date = current_date.split("-")
                            day = splitted_date[2]
                            month = splitted_date[1]
                            year = splitted_date[0]

                            splitted_time = current_time.split(":")
                            hour = splitted_time[0]
                            minute = splitted_time[1]
                            second = splitted_time[2]

                            # Write the data to the CSV file
                            writer.writerow([subject, day , month, year, hour, minute, second, num_back, current_block, current_trial, current_letter, back_letter, response_time, user_input, result])

                            # Print variables
                            print(f"current block: {current_block} |no of trials: {num_trials} |current trial: {current_trial} | current letter: {current_letter} | back letter: {back_letter} | user input: {user_input} | result: {result} ") 

                current_trial += 1    

                # NC changed from this: if current_block == total_num_blocks: to the one in the next line:
                if current_trial == 10:
                    # End of block feedback
                    screen.fill(black)
                    # Render the block feedback text
                    practice_feedback_text = "Übungsaufgabe abgeschlossen!"
                    practice_feedback_surface = intro_font.render(practice_feedback_text, True, pygame.Color("white"))
                    practice_feedback_rect = practice_feedback_surface.get_rect(center=(screen_width // 2, screen_height // 2 - 100))
                    screen.blit(practice_feedback_surface, practice_feedback_rect)

                    # Render the "Press A or L to continue" text
                    continue_text = "Weiter mit A oder L"
                    continue_surface = intro_font.render(continue_text, True, pygame.Color("white"))
                    continue_rect = continue_surface.get_rect(center=(screen_width // 2, screen_height // 2))
                    screen.blit(continue_surface, continue_rect)

                    pygame.display.flip()

                    # Wait for the 'A' or 'L' key to be pressed
                    key_pressed = False
                    while not key_pressed:
                        for event in pygame.event.get():
                            if event.type == pygame.KEYDOWN:
                                if event.key == pygame.K_ESCAPE:
                                    return
                                elif event.key in [pygame.K_a, pygame.K_l]:
                                    key_pressed = True
                                    #current_trial = 0
                                    return
                    # Clear the screen for the next block
                    screen.fill(black)
                    pygame.display.flip()
                    pygame.time.wait(blank_duration)
                    
                    
                                    

############################################################################################

def real_nback(subject, experiment, week, study_night, current_block, num_back, num_back_addition, num_back_performance_addition):

    # Always open the pygame window at front of all windows open on screen
    os.environ['SDL_VIDEO_WINDOW_POS'] = '0,0'  # Set window position to top-left corner

    # Initialize Pygame
    pygame.init()

    # Set the display mode and get the screen dimensions
    screen_info = pygame.display.Info()
    screen_width = screen_info.current_w
    screen_height = screen_info.current_h

    # Define the colors
    black = (0, 0, 0)
    white = (255, 255, 255)

    # Initialize the game window
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN | pygame.NOFRAME)  # Use pygame.FULLSCREEN flag

    pygame.display.set_caption("N-Back Task")

    clock = pygame.time.Clock()

    # Hide the mouse cursor
    pygame.mouse.set_visible(False)


    # Define the experiment parameters
    letter_duration = 500  # in milliseconds
    blank_duration = 1500  # in milliseconds
    num_trials = 20  # Number of letters to be presented (10)
    total_num_blocks = 3  # Number of blocks to be run (3)
    #current_block = 1 # Initialise the current block (NEW)
    
    
    # Create a saving mechanism
    
    # Create strings for file saving purposes
    subject_str = str(subject)
    week_str = str(week)
    study_night_str = str(study_night)
    
    # Title (for outputs)
    TITLE = 'N-Back_Real_Results'

    # Check if output directory exists #'C:/Users/noemi/Desktop/teststarter_python/Logs'
    out_dir = './Logs'
    if not os.path.exists(out_dir):
    #    print("Output directory does not exist. Exiting...")
    #    sys.exit()
        print(f"{title_dir} does not exist. Creating now...")
        os.makedirs(title_dir)   

    # Define the title directory (a folder in logs called "GoNoGo_Results")
    title_dir = os.path.join(out_dir, TITLE)
    if not os.path.exists(title_dir):
        print(f"{title_dir} does not exist. Creating now...")
        os.makedirs(title_dir)   

    # Output file name
    output_filename = f"NBack{subject_str}_{week_str}_{experiment}_{study_night_str}_{TITLE}.csv"

    # Full path for the output file
    output_filename = os.path.join(title_dir, output_filename)

    # Open the output CSV file for writing
    with open(output_filename, 'a', newline='') as csvfile:
        # Create a CSV writer object
        writer = csv.writer(csvfile, delimiter = ',')
        # Write the header row
        writer.writerow(['Subject ID', "Day", "Month", "Year", "Hours", "Minutes", "Seconds", 'Num-Back', 'Block', 'Current Trial', 'Current Letter', 'Back Letter', 'Response Time', 'User Input', 'Result'])
    

        while current_block <= total_num_blocks:
            while True:
                # Define the introduction screen texts
                first_screen_intro_texts = [
                    f"Du wirst nun die Aufgabe {num_back}-BACK durchführen.",
                    "Das heißt, dass du den gerade gezeigten Buchstaben mit jenem vergleichst",
                    f"den du {num_back} Buchstaben zuvor gesehen hast.",
                    "Bitte beachte, dass du nach JEDEM Buchstaben eine Entscheidung treffen,",
                    "also eine Taste drücken sollst.",
                    'Drücke die Taste "A", wenn der aktuelle Buchstabe nicht derselbe ist',
                    'und die Taste "L", wenn es derselbe Buchstabe ist,'f" den du {num_back} Buchstaben zuvor gesehen hast.",
                    "Bitte platziere jetzt deine linken und rechten Zeigefinger auf diesen Tasten.",
                    "",
                    "",
                    "Drücke Taste A oder L, um fortzufahren"
                ]

                second_screen_intro_texts = [
                    #"Die folgenden Durchgänge sollen dich mit der Aufgabe vertraut machen.",
                    #"Das heißt, dass weniger Buchstaben gezeigt werden und du länger Zeit hast,",
                    #"um eine Antwort abzugeben.",
                    #"Zudem wird es nach jeder Entscheidung eine kurze Rückmeldung geben.",
                    #"",
                    #"",
                    "Drücke Taste A oder L, um mit den richtigen Durchgängen zu beginnen."
                ]
                # Render the text surfaces and create rectangles for each line of text
                font_size = 32
                intro_font = pygame.font.Font(None, 30)

                screen_text_surfaces = []
                screen_text_rects = []
                line_height = 50  # Adjust this value to control the vertical spacing between lines
                #fill the background of the text black
                screen.fill(pygame.Color("black"))  # Clear the screen

                # Visualize first screen text
                for index, text in enumerate(first_screen_intro_texts):
                    intro_text_surface = intro_font.render(text, True, pygame.Color("white"))
                    intro_text_rect = intro_text_surface.get_rect(center=(screen_width // 2, (screen_height // 2 - 200) + (index * line_height)))
                    screen_text_surfaces.append(intro_text_surface)
                    screen_text_rects.append(intro_text_rect)

                for index in range(len(screen_text_surfaces)):
                    screen.blit(screen_text_surfaces[index], screen_text_rects[index])

                pygame.display.flip()

                # Wait for a key press to continue
                key_pressed = False
                while not key_pressed:
                    for event in pygame.event.get():
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_ESCAPE:
                                return
                            elif event.key in [pygame.K_a, pygame.K_l]:
                                key_pressed = True

                # Clear the screen
                screen.fill(pygame.Color("black"))

                # Render the text surfaces and create rectangles for each line of text
                screen_text_surfaces = []
                screen_text_rects = []

                # Visualize second screen text
                for index, text in enumerate(second_screen_intro_texts):
                    intro_text_surface = intro_font.render(text, True, pygame.Color("white"))
                    intro_text_rect = intro_text_surface.get_rect(center=(screen_width // 2, (screen_height // 2 - 200) + (index * line_height)))
                    screen_text_surfaces.append(intro_text_surface)
                    screen_text_rects.append(intro_text_rect)

                for index in range(len(screen_text_surfaces)):
                    screen.blit(screen_text_surfaces[index], screen_text_rects[index])

                pygame.display.flip()

                # Wait for a key press to continue
                key_pressed = False
                while not key_pressed:
                    for event in pygame.event.get():
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_ESCAPE:
                                return
                            elif event.key in [pygame.K_a, pygame.K_l]:
                                key_pressed = True

                # Clear the screen
                screen.fill(black)
                pygame.mouse.set_visible(False)
                pygame.display.flip()
                pygame.time.wait(500) #maybe change the time

                # Define the sequence of letters
                sequence = generate_nback_sequence(num_trials, num_back)

                # Initialize variables for tracking letters and user input
                current_trial = 0
                previous_letters = []
                # user_input = None
                back_letter = None
                result = None
                result_list = []
                response_time = ""
                
                # Main game loop
                running = True
                while running:
                    # Check for quit event
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            running = False
                        elif event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_ESCAPE:
                                running = False

                    # Play a new trial only if the total number of trials have not yet been reached
                    if current_trial < num_trials:
                        # Store back_letter variable if there is a back_letter for the number of backs the trial is set for
                        if current_trial >= num_back:
                            back_letter = sequence[current_trial - num_back]
                        else:
                            back_letter = None  # Handle the case when not enough backs are available
                        # Clear user_input
                        user_input = None # (NEW)
                        # Select the next letter in the sequence
                        current_letter = sequence[current_trial]
                        # Clear the screen
                        screen.fill(black)
                        # Configure the letter visualisation
                        font = pygame.font.Font(None, int(screen_height / 5))
                        text = font.render(current_letter, True, white)
                        text_rect = text.get_rect(center=(screen_width // 2, screen_height // 2))
                        screen.blit(text, text_rect)
                        # Display the letter
                        pygame.display.flip()
                        # Set the start time for the letter display
                        start_time = pygame.time.get_ticks()
                        reaction_start_time = time.time()
                        # Process user input during letter display
                        while pygame.time.get_ticks() < start_time + letter_duration:
                            if current_trial >= num_back:
                                for event in pygame.event.get():
                                    if event.type == pygame.KEYDOWN:
                                        if event.key == pygame.K_a:
                                            response_time = (time.time() - reaction_start_time)
                                            user_input = "No Match"
                                        elif event.key == pygame.K_l:
                                            response_time = (time.time() - reaction_start_time)
                                            user_input = "Match"
                        
                        # Clear the screen
                        screen.fill(black)
                        pygame.display.flip()
                        start_time = pygame.time.get_ticks()
                        # Process user input during blank display
                        while pygame.time.get_ticks() < start_time + blank_duration:
                            if current_trial >= num_back:
                                for event in pygame.event.get():
                                    if event.type == pygame.KEYDOWN:
                                        if event.key == pygame.K_a:
                                            user_input = "No Match"
                                        elif event.key == pygame.K_l:
                                            user_input = "Match"

                        if current_trial >= num_back:
                            # Compare the current_letter with the letter displayed n steps back
                            if current_letter == back_letter:  # If the current letter is the same as the n-back letter
                                if user_input == "Match":
                                    result = "Correct"
                                elif user_input == "No Match":
                                    result = "Incorrect"
                                else: 
                                    user_input == "No Input"
                                    result = "No Input"
                            else:  # If the current letter is different from the n-back letter
                                if user_input == "No Match":
                                    result = "Correct"
                                elif user_input == "Match":
                                    result = "Incorrect"
                                else:
                                    user_input == "No Input"
                                    result = "No Input"
                        
                           
                                
                        result_list.append(result)

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

                        # Write the data to the CSV file
                        writer.writerow([subject, day , month, year, hour, minute, second, num_back, current_block, current_trial, current_letter, back_letter, response_time, user_input, result])

                        # Print variables
                        print(f"current block: {current_block} |no of trials: {num_trials} |current trial: {current_trial} | current letter: {current_letter} | back letter: {back_letter} | user input: {user_input} | result: {result} ") 


                        #if it is the last letter final letter in sequence then after feedback, 
                        if current_trial == num_trials - 1:
                            # Evaluate performance
                            correct_count = result_list.count("Correct")
                            performance = correct_count/(num_trials - num_back)*100
                            print("result list: ", result_list)
                            print("correct count: ", correct_count)
                            print("performance: ", performance)
                            print("block: ", current_block)
                            print("num_back: ", num_back)
                            if performance > 90:
                                num_back_performance_addition = 1
                            elif performance < 70:
                                if num_back == 1:
                                    num_back_performance_addition = 0
                                else:
                                    num_back_performance_addition = -1
                            else:
                                num_back_performance_addition = 0
                            num_back = num_back + num_back_performance_addition
                            #print("num_back: ", num_back)
                            # exit the letter-feedback loop to go to end of block feedback before beginning next block
                            running = False

                            # Clear the screen
                            screen.fill(black)
                            pygame.display.flip()
                            pygame.time.wait(blank_duration)

                            # Get the current date and time
                            #current_date = time.strftime("%Y-%m-%d")
                            #current_time = time.strftime("%H:%M:%S")

                            # Write the data to the CSV file
                            #writer.writerow([current_date, current_time, num_back, current_block, current_trial, current_letter, back_letter, user_input, result])

                            # Print variables
                            #print(f"current block: {current_block} |no of trials: {num_trials} |current trial: {current_trial} | current letter: {current_letter} | back letter: {back_letter} | user input: {user_input} | result: {result} ") 

                    current_trial += 1    



                # Check if it's the last block
                if current_block == total_num_blocks:
                    # Clear screen
                    screen.fill(black)
                    # End of the task message
                    end_text = f"Block {current_block} abgeschlossen! Aufgabe beendet!"
                    end_surface = intro_font.render(end_text, True, pygame.Color("white"))
                    end_rect = end_surface.get_rect(center=(screen_width // 2, screen_height // 2))
                    screen.blit(end_surface, end_rect)
                    pygame.display.flip()
                    pygame.time.wait(2000)
                    return
                else:
                    # End of block feedback
                    screen.fill(black)
                    # Render the block feedback text
                    block_feedback_text = f"Block {current_block} abgeschlossen!"
                    block_feedback_surface = intro_font.render(block_feedback_text, True, pygame.Color("white"))
                    block_feedback_rect = block_feedback_surface.get_rect(center=(screen_width // 2, screen_height // 2 - 100))
                    screen.blit(block_feedback_surface, block_feedback_rect)

                    # Render the "Press A or L to continue" text
                    continue_text = "Weiter mit A oder L"
                    continue_surface = intro_font.render(continue_text, True, pygame.Color("white"))
                    continue_rect = continue_surface.get_rect(center=(screen_width // 2, screen_height // 2))
                    screen.blit(continue_surface, continue_rect)

                    pygame.display.flip()

                    # Wait for the 'A' or 'L' key to be pressed
                    key_pressed = False
                    while not key_pressed:
                        for event in pygame.event.get():
                            if event.type == pygame.KEYDOWN:
                                if event.key == pygame.K_ESCAPE:
                                    return
                                elif event.key in [pygame.K_a, pygame.K_l]:
                                    key_pressed = True
                    current_block += 1
                    #current_trial = 0
                    practice_nback(subject, week, study_night, current_block, num_back, num_back_addition, num_back_performance_addition)

                    # Clear the screen for the next block
                    #screen.fill(black)
                    #pygame.display.flip()
                    #pygame.time.wait(blank_duration)
                    
    
                    

#########################################################################################
def start_real_nback(subject, experiment, week, study_night):
    current_block = 1
    num_back = 2
    num_back_addition = None
    num_back_performance_addition = 0
    practice_nback(subject, experiment, week, study_night, current_block, num_back, num_back_addition, num_back_performance_addition)
    real_nback(subject, experiment ,week, study_night, current_block, num_back, num_back_addition, num_back_performance_addition)

#########################################################################################
                    