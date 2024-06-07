import sys

import pygame
import tkinter as tk
import tkinter.filedialog

from components import Button, CheckBox
from services import PsyTestProConfig, ImportTasksService
import webbrowser
from services import TranslateService
from .task_create_view import AddTaskView
from .manage_task_view import ManageTasksView
from .task_delete_view import DeleteTaskView

class TaskManualImportView:
    def __init__(self, translate_service: TranslateService, task_create_view: AddTaskView):
        self.translate_service = translate_service
        self.add_task = task_create_view
        self.manage_tasks_view = ManageTasksView(translate_service)
        self.is_running = True
        self.psy_test_pro_config = PsyTestProConfig()
        self.settings = self.psy_test_pro_config.get_settings()
        self.primary_color = pygame.Color(self.settings["primaryColor"])
        self.danger_color = pygame.Color(self.settings["dangerColor"])
        self.successMsg = None
        self.errorMsg = None
        self.font = pygame.font.Font(None, 18)
        self.delete_task_view = DeleteTaskView(self.translate_service)

    def back(self):
        self.errorMsg = None
        self.successMsg = None
        self.is_running = False

    def show(self, psy_test_pro, create_continuously: bool, experiment_name: str):
        screen = pygame.display.get_surface()

        spacing = 60
        width, height = pygame.display.Info().current_w, pygame.display.Info().current_h
        x = width // 2
        y = height // 2 - 150

        font = pygame.font.Font(
            None, int(32)
        )  # Create font object for header
        formated_experiment_name = experiment_name.replace('_schedule', '').replace('_list', '').replace('_', ' ')
        title_text = ' '.join(
            [self.translate_service.get_translation('createTask'), self.translate_service.get_translation('for'),
             formated_experiment_name])
        text_surface = font.render(title_text, True,
                                   pygame.Color(self.settings["primaryColor"]))  # Render the text 'Task' with the font and color light_grey
        text_rect = text_surface.get_rect()

        buttons: list[Button] = []

        create_task_button = Button(
            x,
            y + spacing,
            400,
            40,
            'createTask',
            lambda: self.add_task.add(create_continuously, experiment_name),
            self.translate_service,
        )

        manage_tasks_button = Button(
            x,
            y + 2 * spacing,
            400,
            40,
            'manageTasks',
            lambda: self.manage_tasks_view.display(experiment_name),
            self.translate_service,
        )

        delete_tasks_button = Button(
            x,
            y + 3 * spacing,
            400,
            40,
            'deleteTasks',
            lambda: self.delete_task_view.delete_task(experiment_name),
            self.translate_service,
        )

        show_preview_check_box = CheckBox('showPreview', x, y + spacing * 5, active=True,
                                          translate_service=self.translate_service, font_size=24)

        import_task_button = Button(
            x,
            y + spacing * 4,
            400,
            40,
            'importTasks',
            lambda: self.import_task(experiment_name, show_preview_check_box.active),
            self.translate_service,
        )

        back_to_task_manual_import_button = Button(
            x,
            y + 6 * spacing,
            100,
            40,
            'back',
            lambda: self.back(),
            self.translate_service,
        )

        get_template_button = Button(
            screen.get_width() - 150,
            40,
            250,
            40,
            'getImportTemplate',
            lambda: self.download_template(),
            self.translate_service,
        )

        buttons.append(create_task_button)
        buttons.append(manage_tasks_button)
        buttons.append(import_task_button)
        buttons.append(delete_tasks_button)
        buttons.append(back_to_task_manual_import_button)
        buttons.append(get_template_button)

        while self.is_running:
            for event in pygame.event.get():
                for button in buttons:
                    button.handle_event(event)
                show_preview_check_box.handle_event(event)
            screen.fill(pygame.Color(self.settings["backgroundColor"]))

            screen.blit(text_surface, (x - text_rect.width // 2, y))

            for button in buttons:
                button.draw(screen)

            show_preview_check_box.draw(screen)

            if self.successMsg:
                message = self.font.render(self.successMsg, True, self.primary_color)
                message_rect = message.get_rect()
                message_rect.center = (x, y + spacing * 5 + self.font.get_linesize() * 2)
                screen.blit(message, message_rect)
            if self.errorMsg:
                message = self.font.render(self.errorMsg, True, self.danger_color)
                message_rect = message.get_rect()
                message_rect.center = (x, y + spacing * 5 + self.font.get_linesize() * 2)
                screen.blit(message, message_rect)

            pygame.display.flip()  # Flip the display to update the screen
        self.is_running = True

    def import_task(self, experiment_name: str, show_preview: bool):
        try:
            if sys.platform == "darwin":
                filepath = tk.filedialog.askopenfilename(initialdir='./',
                                                         title=self.translate_service.get_translation('selectFile'))
            else:
                filepath = tk.filedialog.askopenfilename(
                    initialdir='./',
                    title=self.translate_service.get_translation('selectFile'),
                    filetypes=(('Excel files', '*.xlsx;*.xls'), ('CSV files', '*.csv'), ('All files', '*.*'))
                )
            if filepath:
                import_tasks_service = ImportTasksService(self.translate_service)
                result = import_tasks_service.import_tasks(experiment_name, filepath, show_preview)
                self.successMsg = None
                self.errorMsg = None
                if result[0]:
                    self.successMsg = self.translate_service.get_translation(result[1])
                else:
                    self.errorMsg = self.translate_service.get_translation(result[1])
                    if len(result) == 3:
                        self.errorMsg = ' '.join((self.errorMsg, result[2]))

        except Exception as e:
            print(f'An error occurred: {e}')

    def download_template(self):
        webbrowser.open('https://github.com/eliasmattern/PsyTestPro/raw/main/information/taskImportTemplate.xlsx')
