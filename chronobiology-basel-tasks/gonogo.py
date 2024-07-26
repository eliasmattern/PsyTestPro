# Final gonogo task

import csv
import datetime
import os
import random
import sys
import pygame


# Function to perform the gonogo
def GoNoGo_Real(subject, experiment, block, number):
	# Initialize Pygame
	pygame.init()

	# Constants
	BACKGROUND_COLOR = (0, 0, 0)  # Black
	TEXT_COLOR = (255, 255, 255)  # White
	D_STIM_GO_COL = (30, 144, 255)  # Blue
	D_STIM_NOGO_COL = (255, 223, 0)  # Yellow

	# Always open the pygame window at front of all windows open on screen
	os.environ['SDL_VIDEO_WINDOW_POS'] = '0,0'  # Set window position to top-left corner

	# Title (for outputs)
	TITLE = 'GoNoGo_Results'

	# Check if output directory exists
	out_dir = './Logs'

	# Define the title directory (a folder in logs called "GoNoGo_Results")
	title_dir = os.path.join(out_dir, TITLE)  # asks if a folder called GoNoGo_Results exists
	if not os.path.exists(title_dir):  # if the folder doesn't exist
		print(f"{title_dir} does not exist. Creating now...")
		os.makedirs(title_dir)  # create a new directory (folder) called GoNoGo_Results (title_dir)

	# Function to write data to a CSV file
	def write_data(subject, experiment, block, number, data):
		date = datetime.datetime.now()
		filename = os.path.join(title_dir,
								f"Gonogo_{subject}_{experiment}_{block}_{number}_{date.day}_{date.month}_{date.year}.csv")
		with open(filename, 'a', newline='') as file:
			writer = csv.writer(file)
			writer.writerow(data)

	# Data Headers for Output
	D_HEADERS = ['Subject ID', 'Block', 'Number', 'Day', 'Month', 'Year', 'Hours', 'Minutes', 'Seconds', 'TrialNumber',
				 'Stimulus Onset Time', 'TrialType', 'Spacebar Press Time',
				 'Response Time', 'Response', 'Feedback']

	# Write the headers to the CSV file
	write_data(str(subject), str(experiment), str(block), str(number), D_HEADERS)

	# Set screen dimensions
	screen_width, screen_height = pygame.display.Info().current_w, pygame.display.Info().current_h

	# Set up the screen
	screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
	pygame.display.set_caption("GoNoGo Task")
	clock = pygame.time.Clock()
	screen.fill(BACKGROUND_COLOR)

	# Instruction screen
	font = pygame.font.Font(None, 24)
	text = "Drücke die Leertaste mit deiner dominanten Hand, wenn du ein blaues Quadrat siehst.\nDrücke nicht, wenn es gelb ist.\n\nDrücke die Leertaste, um zu starten."
	lines = text.split('\n')
	line_height = 30
	for i, line in enumerate(lines):
		text_surface = font.render(line, True, TEXT_COLOR)
		text_rect = text_surface.get_rect(center=(screen_width // 2, screen_height // 2 + i * line_height))
		screen.blit(text_surface, text_rect)
		# Hide mouse cursor
		pygame.mouse.set_visible(False)

	pygame.display.flip()

	# Wait for spacebar press to start the task
	waiting = True
	while waiting:
		for event in pygame.event.get():
			if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
				waiting = False
			elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
				return False

	# Experiment parameters
	n_trials = 100  # to be set to 100
	trial_type = [''] * n_trials

	# Hide mouse cursor
	pygame.mouse.set_visible(False)

	# Main experiment loop
	for trial in range(n_trials):
		# Display fixation dot for 450ms
		fixation_dot_present = True
		screen.fill(BACKGROUND_COLOR)
		fixation_dot_radius = 5
		fixation_dot_color = TEXT_COLOR
		fixation_dot_position = (screen_width // 2, screen_height // 2)
		pygame.draw.circle(screen, fixation_dot_color, fixation_dot_position, fixation_dot_radius)
		pygame.display.flip()
		pygame.time.wait(450)  # Fixation dot duration
		fixation_dot_present = False
		# Clear the screen before drawing the stimulus
		screen.fill(BACKGROUND_COLOR)
		pygame.display.flip()

		# Draw stimulus
		if random.random() < 0.75:  # randomly determines whether the stimulus should be "GO" or a "NOGO"
			stimulus_color = D_STIM_GO_COL  # Blue
			trial_type[trial] = 'GO'  # The trial type is updated accordingly in the trial_type list
		else:
			stimulus_color = D_STIM_NOGO_COL  # Yellow
			trial_type[trial] = 'NOGO'  # The trial type is updated accordingly in the trial_type list
		stimulus_rect = pygame.Rect(screen_width // 2 - 50, screen_height // 2 - 50, 100,
									100)  # calculate shape of stimulus
		screen.fill(BACKGROUND_COLOR)  # fill window with black background
		pygame.draw.rect(screen, stimulus_color, stimulus_rect)  # draw stimulus
		pygame.display.flip()  # make stimulus visable

		# Start timing
		stimulus_duration = 0
		stimulus_onset_time = pygame.time.get_ticks()  # records the start time of the stimulus presentation

		# Initialise variables
		response = ''
		feedback = ''
		spacebar_press_time = None

		# Loop to capture responses and handle stimulus duration
		while response == '':
			stimulus_duration = pygame.time.get_ticks() - stimulus_onset_time  # calculate the elapsed time since the start of the trial
			if stimulus_duration >= 1000:  # If the stimulus duration reaches 1 sec
				if response == '':
					response = 'NO RESPONSE'  # Log the response as "NO RESPONSE"
					response_time = None
				if trial_type[trial] == 'NOGO':  # If the trial type is 'NOGO'...
					feedback = 'correct'  # log response as correct
				elif trial_type[trial] == 'GO':  # If the trial type is 'GO'...
					feedback = 'incorrect'  # log response as no response
				break

			for event in pygame.event.get():
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_SPACE:  # If there is a spacebar press
						spacebar_press_time = pygame.time.get_ticks()
						response_time = (spacebar_press_time - stimulus_onset_time) / 1000
						response = 'GO'  # Log the response as "GO"
						if trial_type[trial] == 'GO':  # If the trial type is 'GO'...
							feedback = 'correct'  # log response as correct
						elif trial_type[trial] == 'NOGO':  # If the trial type is 'NOGO'...
							feedback = 'incorrect'  # log response as incorrect
						# Continue displaying the stimulus for the remaining duration (one second in total)
						remaining_duration = 1000 - stimulus_duration
						if remaining_duration > 0:
							pygame.time.wait(remaining_duration)
						break
					elif event.key == pygame.K_ESCAPE:  # If there is an Esc key press
						return False

		# Clear the screen
		screen.fill(BACKGROUND_COLOR)
		pygame.display.flip()

		# Record trial data
		date = datetime.datetime.now()
		if response_time == None:
			response_time = "Keine Eingabe"
		data = [
			subject,
			block,
			number,
			date.day,
			date.month,
			date.year,
			date.hour,
			date.minute,
			date.second,
			trial + 1,
			stimulus_onset_time,
			trial_type[trial],
			spacebar_press_time,
			response_time,
			response,
			feedback
		]
		write_data(str(subject), str(experiment), str(block), str(number), data)

		# Clear the screen
		screen.fill(BACKGROUND_COLOR)
		pygame.display.flip()

	# End of the experiment
	return True


if len(sys.argv) >= 5:
	subject, experiment, block, number = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
	GoNoGo_Real(subject, experiment, block, number)
else:
	print("Usage: python gonogo.py subject experiment block number")
