import json

class TeststarterConfig:
    def __init__(self):
        self.experiments = None
        self.current_experiment = None
        self.current_tasks = None
        self.error_msg = ""

    def load_experiments(self):
        try:
            with open(f"json/experimentConfig.json", "r", encoding="utf-8") as file:
                self.experiments = json.load(file)
        except FileNotFoundError:
            raise Exception(f"File Error: ./json/experimentConfig.json not found ")

    def load_experiment_tasks(self, experiment, time_of_day = ""):
        self.current_experiment = experiment
        self.error_msg = ""
        try:
            with open(f"json/taskConfig.json", "r", encoding="utf-8") as file:
                tasks = json.load(file)
                tim_of_day_and_experiment = time_of_day + "_" + experiment
                if tasks.get(tim_of_day_and_experiment + "_variable") != None:
                    self.current_tasks = tasks.get(tim_of_day_and_experiment + "_variable").get("tasks")
                elif tasks.get("full_" + experiment + "_variable") != None:
                    self.current_tasks = tasks.get("full_" + experiment + "_variable").get("tasks")
                elif tasks.get(experiment + "_variable") != None:
                    self.current_tasks = tasks.get(experiment + "_variable").get("tasks")
                else:
                    self.error_msg = "experimentNotFound"
        except FileNotFoundError:
            raise Exception(f"File Error: ./json/taskConfig.json not found")

