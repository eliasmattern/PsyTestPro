import pygame

def waking_eeg():

    # Initialize Pygame
    pygame.init()

    # Get the screen width and height
    screen_info = pygame.display.Info()
    screen_width = screen_info.current_w
    screen_height = screen_info.current_h

    # Open a fullscreen window
    window = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)

    # Hide the mouse cursor
    pygame.mouse.set_visible(False)

    # Set the background color
    background_color = (0, 0, 0)  # Black

    # Set text parameters
    font_size = 30
    font = pygame.font.Font(None, font_size)
    font_color = (192, 192, 192)  # Gray

    # Define the text content
    texts = [
        'Wir werden jetzt ein Wach-EEG durchführen.',
        '',
        '',
        'Dabei wirst du für fünf Minuten auf ein Kreuz schauen.',
        '',
        'Legen Sie bitte ihre Hände auf ihre Knie,',
        'stellen Sie ihre Füße fest auf den Boden',
        ' und stützen sie sich mit dem Rücken auf ihren Stuhl.',
        '',
        'Versuch währenddessen möglichst wenig zu blinzeln.',
        '',
        '',
        'Drücke die Leertaste, sobald du bereit bist.'
    ]

    # Create a list to store text surfaces and their respective rectangles
    text_surfaces = []
    text_rects = []

    # Calculate the position of each text
    text_x = screen_width // 2
    line_spacing = 40
    total_height = len(texts) * line_spacing
    text_y = screen_height // 2 - total_height // 2

    # Render and position the text
    for text in texts:
        text_surface = font.render(text, True, font_color)
        text_rect = text_surface.get_rect(center=(text_x, text_y))
        text_surfaces.append(text_surface)
        text_rects.append(text_rect)
        text_y += line_spacing

    # Create a fixation cross surface
    cross_size = 70
    cross_surface = pygame.Surface((cross_size, cross_size), pygame.SRCALPHA)
    pygame.draw.line(cross_surface, (255, 255, 255), (cross_size // 2, 0), (cross_size // 2, cross_size), 5)
    pygame.draw.line(cross_surface, (255, 255, 255), (0, cross_size // 2), (cross_size, cross_size // 2), 5)
    cross_rect = cross_surface.get_rect(center=(screen_width // 2, screen_height // 2))

    # Main loop
    running = True
    display_cross = False
    while running:
        # Clear the screen
        window.fill(background_color)

        if display_cross:
            # Display the fixation cross
            window.blit(cross_surface, cross_rect)
        else:
            # Render and display the text
            for i in range(len(text_surfaces)):
                window.blit(text_surfaces[i], text_rects[i])

        # Update the display
        pygame.display.flip()

        # Process events
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    display_cross = True
                elif event.key == pygame.K_a or pygame.K_ESCAPE:
                    running = False

    # Show the mouse cursor
    pygame.mouse.set_visible(True)

    # Close the window
    return

