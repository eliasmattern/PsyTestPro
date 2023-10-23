import csv

class LanguageConfiguration:
    def __init__(self):
        self.lang = "en"
        self.config_file = "language_config.csv"
    
    def read_language_config(self):
        with open(self.config_file, 'r') as file:
            reader = csv.reader(file)
            next(reader, None)  # skip the headers
            for row in reader:
                for i, value in enumerate(row):
                    self.lang = value

    def update_language_config(self, new_language):
        with open(self.config_file, 'w') as file:
            writer = csv.writer(file)
            writer.writerow(["language"])
            writer.writerow([new_language])
            
    
    def get_language(self):
        return self.lang