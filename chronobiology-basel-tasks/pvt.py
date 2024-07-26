import pygame
from pygame.locals import *
import csv
import random
import time
import os
import sys


def pvt(subject, experiment, block, number):
	# Convert numerical inputs to strings
	subject_str = str(subject)
	block_str = str(block)
	number_str = str(number)

	# Title (for outputs)
	TITLE = 'PVT_Results'

	# Check if output directory exists
	out_dir = './Logs'

	# Define the title directory (a folder in logs called "GoNoGo_Results")
	title_dir = os.path.join(out_dir, TITLE)
	if not os.path.exists(title_dir):
		print(f"{title_dir} does not exist. Creating now...")
		os.makedirs(title_dir)

		# Initialize Pygame
	pygame.init()

	# Hide the mouse cursor
	pygame.mouse.set_visible(False)

	# Get the screen dimensions
	screen_info = pygame.display.Info()
	screen_width = screen_info.current_w
	screen_height = screen_info.current_h

	# Always open the pygame window at front of all windows open on screen
	os.environ['SDL_VIDEO_WINDOW_POS'] = '0,0'  # Set window position to top-left corner

	# Set the screen size and create the Pygame window
	screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

	# Set the font properties
	font = pygame.font.Font(None, 30)

	# Set the position of the text
	text_pos = (screen_width // 2, screen_height // 2)

	# Load the beep sound
	beep_sound = pygame.mixer.Sound("./lib/beep.wav")

	# Set up custom event for stopping the sound
	STOP_SOUND_EVENT = pygame.USEREVENT + 1

	# Initialize variables
	counter = 0
	spacebar_pressed = False
	spacebar_press_time = 0
	beep_sound_playing = False

	# Start the counter
	clock = pygame.time.Clock()
	running = True

	# Set the duration of the fix/counter presentation in seconds
	duration = 600  # 10 minutes/600 seconds
	start_time = time.time()  # set the start_time as the current time

	# Output file name
	output_filename = f"PVT{subject_str}_{block_str}_{experiment}_{number_str}.csv"

	# Full path for the output file
	output_filename = os.path.join(title_dir, output_filename)

	# Open the output CSV file for writing
	with open(output_filename, 'w', newline='') as csvfile:
		# Create a CSV writer object
		writer = csv.writer(csvfile)
		# Write the header row
		writer.writerow(
			["Day", "Month", "Year", "Hours", "Minutes", "Seconds", 'Trial Number', 'Fixation Cross Duration (ms)',
			 'Reaction Time (ms)', 'Absolute Time'])

		trial_number = 1

		# Show introduction screen
		intro_text_1 = "Willkommen zum PVT"
		intro_text_2 = "Drücke die Leertaste so schnell wie möglich, wenn der Zähler beginnt"
		intro_text_3 = "zum Starten Leertaste drücken"
		intro_font = pygame.font.Font(None, 30)
		intro_text_1_surface = intro_font.render(intro_text_1, True, pygame.Color("white"))
		intro_text_2_surface = intro_font.render(intro_text_2, True, pygame.Color("white"))
		intro_text_3_surface = intro_font.render(intro_text_3, True, pygame.Color("white"))
		intro_text_1_rect = intro_text_1_surface.get_rect(center=(screen_width // 2, screen_height // 2 - 50))
		intro_text_2_rect = intro_text_2_surface.get_rect(center=(screen_width // 2, screen_height // 2))
		intro_text_3_rect = intro_text_3_surface.get_rect(center=(screen_width // 2, screen_height // 2 + 50))

		# Flag to track if the spacebar is pressed in the introduction screen
		intro_spacebar_pressed = False

		while True:
			screen.fill(pygame.Color("black"))  # Clear the screen
			screen.blit(intro_text_1_surface, intro_text_1_rect)
			screen.blit(intro_text_2_surface, intro_text_2_rect)
			screen.blit(intro_text_3_surface, intro_text_3_rect)
			pygame.display.flip()

			for event in pygame.event.get():
				if event.type == QUIT:
					return False
				elif event.type == KEYDOWN and event.key == K_ESCAPE:
					return False
				elif event.type == KEYDOWN and event.key == K_SPACE:
					intro_spacebar_pressed = True
					break

			if intro_spacebar_pressed:
				screen.fill(pygame.Color("black"))  # Clear the screen
				pygame.display.flip()
				break

		absolute_start_time = None
		while running:
			if absolute_start_time == None:
				absolute_start_time = time.time()
			# Check if the duration has elapsed
			if time.time() - start_time >= duration:
				running = False
				break

			# Display fixation cross for a random duration between 2 and 10 seconds
			fix_duration = random.randint(2000, 10000)
			fix_start_time = time.time()

			# Display the fixation cross
			font_size = 50
			font = pygame.font.Font(None, font_size)
			text_surface = font.render("+", True, pygame.Color("white"))
			text_rect = text_surface.get_rect(center=(screen_width // 2, screen_height // 2))
			screen.blit(text_surface, text_rect)
			pygame.display.flip()

			# Wait for the fixation duration to elapse
			while time.time() - fix_start_time < fix_duration / 1000:
				for event in pygame.event.get():
					if event.type == QUIT:
						running = False
						return False
					elif event.type == KEYDOWN and event.key == K_ESCAPE:
						running = False
						return False

			# Reset variables for the new counter
			counter = 0
			spacebar_pressed = False
			spacebar_press_time = 0
			beep_sound_playing = False

			counter_start_time = time.time()  # Start counting from the time the fixation cross disappears

			while running:
				for event in pygame.event.get():
					if event.type == QUIT:
						running = False
						return False
					elif event.type == KEYDOWN and event.key == K_SPACE:
						if not spacebar_pressed:
							spacebar_pressed = True
							spacebar_press_time = counter
					elif event.type == STOP_SOUND_EVENT:
						beep_sound.stop()
					elif event.type == KEYDOWN and event.key == K_ESCAPE:
						running = False
						return False

				screen.fill(pygame.Color("black"))  # Clear the screen

				if not spacebar_pressed:
					counter = int(
						(time.time() - counter_start_time) * 1000)  # Update the counter based on the elapsed time
				else:
					counter += clock.tick_busy_loop(1000)  # Update the counter based on the clock tick (60 FPS)

				if counter >= 10000:  # 10 seconds (10,000 milliseconds)
					counter = 10000  # Limit the counter to 10 seconds
					if not spacebar_pressed and not beep_sound_playing:
						beep_sound.play()
						beep_sound_playing = True
						pygame.time.set_timer(STOP_SOUND_EVENT, 1000)
						absolute_time = time.time() - absolute_start_time

				if counter >= 10000 or spacebar_pressed:
					if spacebar_pressed:
						counter_text = str(spacebar_press_time) + " ms"
						reaction_time = spacebar_press_time
						absolute_time = time.time() - absolute_start_time
					else:
						counter_text = "Zeit ist um!"
						reaction_time = counter
						absolute_time = time.time() - absolute_start_time
				else:
					counter_text = str(counter) + " ms"

				text_surface = font.render(counter_text, True, pygame.Color("white"))
				text_rect = text_surface.get_rect(center=text_pos)
				screen.blit(text_surface, text_rect)  # Blit the text onto the screen

				pygame.display.flip()  # Update the display

				if counter >= 10000 or spacebar_pressed:
					pygame.time.wait(500)  # Pause for 0.5 seconds before continuing to the next iteration
					# Clear the screen
					screen.fill(pygame.Color("black"))
					pygame.display.flip()

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
					writer.writerow([day, month, year, hour, minute, second, trial_number, fix_duration, reaction_time,
									 absolute_time])

					trial_number += 1

					break

	# Display the task end screen
	screen.fill(pygame.Color("black"))
	end_text = "Aufgabe beendet"
	end_font = pygame.font.Font(None, 40)
	end_text_surface = end_font.render(end_text, True, pygame.Color("white"))
	end_text_rect = end_text_surface.get_rect(center=(screen_width // 2, screen_height // 2))
	screen.blit(end_text_surface, end_text_rect)
	pygame.display.flip()
	time.sleep(3)  # Pause for 2 seconds

	# Quit Pygame
	return True


if len(sys.argv) >= 5:
	subject, experiment, block, number = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
	pvt(subject, experiment, block, number)
else:
	print("Usage: python gonogo.py subject experiment block number")
