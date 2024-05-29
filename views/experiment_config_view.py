import os
import sys
from datetime import datetime
from tkinter import filedialog
import pygame
from components import Button
from services import CSVToJSONConverter, JSONToCSVConverter
from .experiment_create_view import CreateExperimentView
from .variable_create_view import CreateVariablesView
from .experiment_delete_view import DeleteExperimentView
from .task_delete_view import DeleteTaskView
from .variable_delete_view import DeleteVariableView
from .task_config_view import TaskConfig
from services import PsyTestProConfig
from services import TranslateService


class ExperimentConfig():
    def __init__(self, translate_service: TranslateService):
        self.info_text = ''
        self.translate_service = translate_service
        self.psy_test_pro_config = PsyTestProConfig()
        self.settings = self.psy_test_pro_config.get_settings()

    def back_to_psy_test_pro(self, psy_test_pro):
        psy_test_pro()

    def back(self, psy_test_pro):
        self.display(psy_test_pro, self.translate_service)

    def import_config(self):
        try:
            filepath = filedialog.askopenfilename(
                initialdir='./',  # The initial directory (you can change this)
                title=self.translate_service.get_translation('selectFile'),
                filetypes=(('Excel files', '*.xlsx'), ('All files', '*.*'))  # Add more file types if needed
            )
            if filepath:
                converter = CSVToJSONConverter(filepath)
                converter.convert_to_json()
                self.info_text = 'importSuccessfully'
        except Exception as e:
            self.info_text = 'importFailed'
            print(f'An error occurred: {e}')

    def export_config(self):
        try:
            # Get current timestamp
            current_time = datetime.now()

            # Format the timestamp as yyyy-mm-ddThhmmss
            formatted_time = current_time.strftime('%Y-%m-%dT%H%M%S')

            # Usage
            converter = JSONToCSVConverter('./exports/Experiments_export_' + formatted_time + '.xlsx')
            converter.export_to_csv()
            self.info_text = 'exportSuccessfully'

        except Exception as e:
            self.info_text = 'exportFailed'
            print(f'An error occurred: {e}')

    def display(self, psy_test_pro, create_continously=False):
        self.info_text = ''
        # Open the pygame window at front of all windows open on screen
        os.environ['SDL_VIDEO_WINDOW_POS'] = '0,0'  # Set window position to top-left corner

        # Define colors
        black = pygame.Color(self.settings["backgroundColor"])
        light_grey = pygame.Color(self.settings["primaryColor"])

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
        screen = pygame.display.get_surface()

        # Setting the window caption
        pygame.display.set_caption('Configure Experiment')

        create_experiment_config = CreateExperimentView(self.translate_service)
        delete_experiment_config = DeleteExperimentView(self.translate_service)
        task_config = TaskConfig(self.translate_service)
        delte_task_config = DeleteTaskView(self.translate_service)
        create_variables_config = CreateVariablesView(self.translate_service)
        delete_variables_config = DeleteVariableView(self.translate_service)

        buttons = []
        experiment_buttons = []
        task_buttons = []
        import_export_buttons = []
        var_buttons = []
        spacing = 60
        width, height = pygame.display.Info().current_w, pygame.display.Info().current_h

        x = width // 2
        y = height // 2 - 150

        create_experiment_button = Button(
            x,
            y + spacing,
            400,
            40,
            'createExperiment',
            lambda: create_experiment_config.create_experiment_config_display(
                psy_test_pro, create_continously
            ),
            self.translate_service,
        )
        delete_button = Button(
            x,
            y + spacing * 2,
            400,
            40,
            'deleteExperiment',
            lambda: delete_experiment_config.delete_experiment_config_display(
                psy_test_pro
            ),
            self.translate_service,
        )
        create_task_button = Button(
            x,
            y + spacing,
            400,
            40,
            'createTask',
            lambda: task_config.add_task_config_display(psy_test_pro),
            self.translate_service,
        )
        delete_task_button = Button(
            x,
            y + spacing * 2,
            400,
            40,
            'deleteTask',
            lambda: delte_task_config.delete_task_config_display(),
            self.translate_service,
        )

        export_button = Button(
            x,
            y + spacing * 2,
            400,
            40,
            'exportExperiments',
            lambda: self.export_config(),
            self.translate_service,
        )

        import_button = Button(
            x,
            y + spacing,
            400,
            40,
            'importExperiments',
            lambda: self.import_config(),
            self.translate_service,
        )

        create_var_button = Button(
            x,
            y + spacing,
            400,
            40,
            'createVar',
            lambda: create_variables_config.display(psy_test_pro, self.translate_service),
            self.translate_service,
        )

        delete_var_button = Button(
            x,
            y + spacing * 2,
            400,
            40,
            'deleteVar',
            lambda: delete_variables_config.display(),
            self.translate_service,
        )

        back_to_config_button = Button(
            x,
            y + 60 + 3 * spacing,
            100,
            40,
            'back',
            lambda: self.display(psy_test_pro, create_continously),
            self.translate_service,
        )

        experiment_buttons.append(create_experiment_button)
        experiment_buttons.append(delete_button)
        experiment_buttons.append(back_to_config_button)
        import_export_buttons.append(import_button)
        import_export_buttons.append(export_button)
        import_export_buttons.append(back_to_config_button)
        task_buttons.append(create_task_button)
        task_buttons.append(delete_task_button)
        task_buttons.append(back_to_config_button)
        var_buttons.append(create_var_button)
        var_buttons.append(delete_var_button)
        var_buttons.append(back_to_config_button)

        experiment_config_button = Button(
            x,
            y + 60,
            400,
            40,
            'configureExperiment',
            lambda: self.show_setting_buttons(screen, experiment_buttons, 'configureExperiment'),
            self.translate_service,
        )
        y += spacing

        task_config_button = Button(
            x,
            y + 60,
            400,
            40,
            'configureTasks',
            lambda: self.show_setting_buttons(screen, task_buttons, 'configureTasks'),
            self.translate_service,
        )
        y += spacing
        variable_config_button = Button(
            x,
            y + 60,
            400,
            40,
            'configureVariable',
            lambda: self.show_setting_buttons(screen, var_buttons, 'configureVariable'),
            self.translate_service,
        )
        y += spacing
        import_export_config_button = Button(
            x,
            y + 60,
            400,
            40,
            'importExport',
            lambda: self.show_setting_buttons(screen, import_export_buttons, 'importExport'),
            self.translate_service,
        )

        y += spacing
        back_button = Button(
            x,
            y + 60,
            100,
            40,
            'back',
            lambda: self.back_to_psy_test_pro(psy_test_pro),
            self.translate_service,
        )
        buttons.append(experiment_config_button)
        buttons.append(variable_config_button)
        buttons.append(import_export_config_button)
        buttons.append(task_config_button)
        buttons.append(back_button)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                for button in buttons:
                    button.handle_event(event)
            screen.fill(black)  # Fill the screen with the black color

            for button in buttons:
                button.draw(screen)

            font = pygame.font.Font(
                None, int(30 * width_scale_factor)
            )  # Create font object for header
            text_surface = font.render(
                self.translate_service.get_translation('configureExperiment'), True, light_grey
            )  # Render the text 'Task' with the font and color light_grey
            text_rect = text_surface.get_rect()
            screen.blit(text_surface, (x - text_rect.width // 2, height // 2 - 150))

            font = pygame.font.Font(
                None, int(18 * width_scale_factor)
            )

            info_surface = font.render(
                self.translate_service.get_translation(self.info_text), True, light_grey
            )  # Render the text 'Task' with the font and color light_grey
            info_rect = text_surface.get_rect()
            screen.blit(info_surface, (x - info_rect.width // 2, screen_height - 90))

            pygame.display.flip()  # Flip the display to update the screen

    def show_setting_buttons(self, screen: pygame.Surface, buttons: list[Button], label: str):
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
        width, height = pygame.display.get_surface().get_rect().size

        x = width // 2
        y = height // 2 - 150

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                for button in buttons:
                    button.handle_event(event)
            screen.fill(black)  # Fill the screen with the black color

            for button in buttons:
                button.draw(screen)

            font = pygame.font.Font(
                None, int(30 * width_scale_factor)
            )  # Create font object for header
            text_surface = font.render(
                self.translate_service.get_translation(label), True, light_grey
            )  # Render the text 'Task' with the font and color light_grey
            text_rect = text_surface.get_rect()
            screen.blit(text_surface, (x - text_rect.width // 2, y))

            font = pygame.font.Font(
                None, int(18 * width_scale_factor)
            )

            info_surface = font.render(
                self.translate_service.get_translation(self.info_text), True, light_grey
            )  # Render the text 'Task' with the font and color light_grey
            info_rect = text_surface.get_rect()
            screen.blit(info_surface, (x - info_rect.width // 2, screen_height - 90))

            pygame.display.flip()  # Flip the display to update the screen
