import sys
import pygame
from pygame.locals import *
from components import InputBox, Button
from services import PsyTestProConfig
from services import TranslateService


class CreateVariablesView:
	def __init__(self, translate_service: TranslateService):
		self.running = True
		self.selected_multiple = False
		self.error = ''
		self.psy_test_pro_config = PsyTestProConfig()
		self.settings = self.psy_test_pro_config.get_settings()
		self.translate_service = translate_service

	def back_to_psy_test_pro(self, psy_test_pro):
		self.selected_multiple = False
		self.error = ''
		psy_test_pro()

	def back(self):
		self.running = False
		self.error = ''

	def save_var(self, psy_test_pro, var_name: str, input_boxes: list):
		psy_test_pro_config = PsyTestProConfig()
		result = psy_test_pro_config.save_var(var_name)

		if not result:
			self.error = self.translate_service.get_translation('variableError')
			return

		if self.selected_multiple:
			for input_box in input_boxes:
				input_box.text = ''
			return
		else:
			self.back_to_psy_test_pro(psy_test_pro)

	def create_input_boxes(self, psy_test_pro) -> tuple[list[InputBox], list[Button]]:
		input_boxes = []
		buttons = []
		labels = ['varName']
		spacing = 60
		width, height = pygame.display.Info().current_w, pygame.display.Info().current_h
		x = width // 2
		y = height // 2 - 100
		for label in labels:
			input_box = InputBox(x, y, 400, 40, label, self.translate_service, not_allowed_characters=['_'])
			input_boxes.append(input_box)
			y += spacing
		exit_button = Button(x - 75, y + 60, 100, 40, 'back', lambda: self.back(), self.translate_service)
		submit_button = Button(
			x + 75,
			y + 60,
			100,
			40,
			'submit',
			lambda: self.save_var(psy_test_pro, input_boxes[0].text, input_boxes),
			self.translate_service,
		)

		buttons.append(exit_button)
		buttons.append(submit_button)
		return input_boxes, buttons

	def validate_inputs(self, input_boxes: list[InputBox]):
		is_valid = False

		if (
				input_boxes[0].text
		):
			is_valid = True

		if is_valid:
			return True
		else:
			return False

	def display(self, psy_test_pro, create_continously=False):
		# Define colors
		black = pygame.Color(self.settings["backgroundColor"])
		light_grey = pygame.Color(self.settings["primaryColor"])

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
		pygame.display.set_caption('Create Variable')

		self.selected_multiple = create_continously

		input_boxes, buttons = self.create_input_boxes(psy_test_pro)

		def get_input_index():
			index = 0
			for input_box in input_boxes:
				index += 1
				if input_box.is_selected:
					input_boxes[index - 1].is_selected = False
					break
			if index < len(input_boxes):
				return index
			else:
				return 0

		width, height = pygame.display.Info().current_w, pygame.display.Info().current_h
		x = width // 2
		y = height // 2 - 150

		question_font = pygame.font.Font(
			None, int(24)
		)  # Create font object for header
		option_text_rendered = question_font.render(
			self.translate_service.get_translation('createMultipleVars'),
			True,
			light_grey,
		)
		option_text_rect = option_text_rendered.get_rect(left=x + 180, top=y + 180)
		tick_box_rect = pygame.Rect(
			x + 170 - 20 * height_scale_factor,
			y + 180,
			20 * width_scale_factor,
			20 * height_scale_factor,
		)

		font = pygame.font.Font(
			None, int(32)
		)  # Create font object for header
		text_surface = font.render(self.translate_service.get_translation('createVar'), True,
								   light_grey)  # Render the text 'Task' with the font and color light_grey
		text_rect = text_surface.get_rect()
		error_font = pygame.font.Font(None, 18)
		while self.running:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()
				if event.type == KEYDOWN:
					if event.key == K_TAB:
						index = get_input_index()
						input_boxes[index].is_selected = True
					if event.key == K_RETURN:
						if self.validate_inputs(input_boxes):
							self.save_var(psy_test_pro, input_boxes[0].text, input_boxes)
				elif event.type == pygame.MOUSEBUTTONDOWN:
					if event.button == 1:  # If the left mouse button clicked
						mouse_pos = (
							pygame.mouse.get_pos()
						)  # Store the position of the curser when the mouse was clicked to a variable mouse_pos
						if tick_box_rect.collidepoint(
								mouse_pos
						):  # If the cursor position has collided with the start timer button
							self.selected_multiple = not self.selected_multiple
				for box in input_boxes:
					box.handle_event(event)
				for button in buttons:
					button.handle_event(event)
			screen.fill(black)  # Fill the screen with the black color

			screen.blit(option_text_rendered, option_text_rect)
			screen.blit(text_surface, (x - text_rect.width // 2, y))

			if self.validate_inputs(input_boxes):
				buttons[1].set_active(True)
				buttons[1].set_color(pygame.Color(self.settings["buttonColor"]))
			else:
				buttons[1].set_active(False)
				buttons[1].set_color(pygame.Color(self.settings["inactiveButtonColor"]))

			for box in input_boxes:
				box.draw(screen)

			for button in buttons:
				button.draw(screen)

			if self.error:
				error_surface = error_font.render(self.error, True, pygame.Color(self.settings["dangerColor"]))
				error_rect = error_surface.get_rect()
				error_rect.center = (screen_width / 2, screen_height / 100 * 80)

				screen.blit(error_surface, error_rect)

			# draw the tick box rectangle on the window surface
			pygame.draw.rect(screen, light_grey, tick_box_rect, 2)
			# if the selected_multiple variable is equal to the option currently being processed in the loop
			if self.selected_multiple:
				# create a list of points that define the shape of the tick mark
				tick_mark_points = [
					(
						x + 180 - 25 * height_scale_factor,
						y + 180 + 10 * height_scale_factor,
					),
					(
						x + 180 - 20 * height_scale_factor,
						y + 180 + 15 * height_scale_factor,
					),
					(
						x + 180 - 15 * height_scale_factor,
						y + 180 + 5 * width_scale_factor,
					),
				]
				# draw lines connecting the points defined above (draw the tick)
				pygame.draw.lines(screen, light_grey, False, tick_mark_points, 2)

			pygame.display.flip()  # Flip the display to update the screen
		self.running = True
