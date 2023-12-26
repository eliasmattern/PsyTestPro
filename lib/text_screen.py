import pygame
from services import PsyTestProConfig


def text_screen(title, description, info):
    psy_test_pro_config = PsyTestProConfig()
    settings = psy_test_pro_config.get_settings()
    title = title.replace(r' \n ', '\n')
    title = title.replace(r'\n', '\n')
    description = description.replace(r' \n ', '\n')
    description = description.replace(r'\n', '\n')
    # Initialize Pygame
    pygame.init()

    # Get the screen width and height
    screen_info = pygame.display.Info()
    screen_width = screen_info.current_w
    screen_height = screen_info.current_h

    # Open a fullscreen window
    window = pygame.display.get_surface()

    # Hide the mouse cursor
    pygame.mouse.set_visible(False)

    # Set the background color
    background_color = pygame.Color(settings["backgroundColor"])  # Black

    # Set text parameters
    title_font_size = 50
    font_size = 30
    title_font = pygame.font.Font(None, title_font_size)
    font = pygame.font.Font(None, font_size)
    font_color = pygame.Color(settings["primaryColor"])  # Gray

    # Define the text content

    # Create a list to store text surfaces and their respective rectangles
    text_surfaces = []
    text_rects = []

    # Calculate the position of each text
    text_x = screen_width // 2
    line_spacing = 40
    text_y = (screen_height // 3) - 50

    # Render and position the text
    title_lines = title.split('\n')
    for line in title_lines:
        title_surface = title_font.render(line, True, font_color)
        title_rect = title_surface.get_rect(center=(text_x, text_y))
        text_surfaces.append(title_surface)
        text_rects.append(title_rect)
        text_y += title_font.get_linesize()
    text_y = title_rect.bottom + title_font.get_linesize() * 2

    description_lines = description.split('\n')
    for line in description_lines:
        description_surface = font.render(line, True, font_color)
        description_rect = description_surface.get_rect(center=(text_x, text_y))
        text_surfaces.append(description_surface)
        text_rects.append((text_x - description_rect.width // 2, text_y))
        text_y += font.get_linesize()

    info_surface = font.render(info, True, font_color)
    info_rect = info_surface.get_rect(center=(text_x, screen_height - 250))
    text_surfaces.append(info_surface)
    text_rects.append(info_rect)

    # Main loop
    running = True
    while running:
        # Clear the screen
        window.fill(background_color)

        # Render and display the text
        for i in range(len(text_surfaces)):
            window.blit(text_surfaces[i], text_rects[i])

        # Update the display
        pygame.display.flip()

        # Process events
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a or pygame.K_ESCAPE:
                    running = False

    # Show the mouse cursor
    pygame.mouse.set_visible(True)

    # Close the window
    return
