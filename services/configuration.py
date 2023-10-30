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

    def save_experiment(self, experiment_name, experiment_time_of_day):
        with open('json/experimentConfig.json', 'r') as file:
            original_experiments = json.load(file)

            if not experiment_name in original_experiments:
                # Add a new value to the array
                original_experiments.append(experiment_name)

        # Save the updated array back to the file
        with open('json/experimentConfig.json', 'w') as file:
            json.dump(original_experiments, file)

        # Load the original JSON from the file
        with open('json/taskConfig.json', 'r') as file:
            original_tasks = json.load(file)

        if not experiment_time_of_day + "_" + experiment_name + "_variable" in original_tasks:
            # Add a new variable with an empty task object
            original_tasks[experiment_time_of_day + "_" + experiment_name + "_variable"] = {"tasks": {}}

        # Save the updated JSON back to the file
        with open('json/taskConfig.json', 'w') as file:
            json.dump(original_tasks, file, indent=4)

    def get_experiment_and_time_of_day(self):
        with open('json/taskConfig.json', 'r') as file:
            data = json.load(file)
        variable_names = data.keys()
        result = {}
        for variable in variable_names:
            splitted_variable = variable.split("_")
            result[variable] = {"experiment": splitted_variable[1], "time_of_day": splitted_variable[0]}

        return result

    def load_tasks_of_experiment(self, experiment):
        if experiment == "hab_variable_variable":
            experiment = "hab_variable"

        with open('json/taskConfig.json', 'r') as file:
            data = json.load(file)
        tasks = list(data[experiment]["tasks"].keys())

        return tasks
    
    def delete_task(self, experiment, task):
        if experiment == "hab_variable_variable":
            experiment = "hab_variable"
            
        with open('json/taskConfig.json', 'r') as file:
            data = json.load(file)
        del data[experiment]["tasks"][task]
        # Save the updated array back to the file
        with open('json/taskConfig.json', 'w') as file:
            json.dump(data, file, indent=4)

    def save_task(self, variable, name, time, type, value):
        if variable == "hab_variable_variable":
            variable = "hab_variable"

        # Load the JSON data from a file
        with open('json/taskConfig.json', 'r') as file:
            json_data = json.load(file)

        # Function to add a new task to a specific object
        def add_task_to_object(json_data, object_name, task_name, time, type, value):
            new_task = {
                "time": time,
                "state": "todo",
                "type": type,
                "value": value
            }
            json_data[object_name]["tasks"][task_name] = new_task

        # Example usage
        add_task_to_object(json_data, variable, name, time, type, value)

        # Save the updated JSON data back to the file
        with open('json/taskConfig.json', 'w') as file:
            json.dump(json_data, file, indent=4)