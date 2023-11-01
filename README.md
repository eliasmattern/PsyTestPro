# teststarter

ust open Command Palette (Ctrl-Shift-P) -> Markdown: Create Table of Contents

 ## Installation
To install Teststarter you can either download this GitHub projext as a ZIP and unpack it or you can clone the repository using git:

```git
git clone LINK
```

To use Teststarter python must be installed:
[Download here](https://www.python.org/downloads/)

There are also some dependencies that must be installed using pip:

```python
pip install pygame
pip install pandas
continue
```

## How to run Teststarter
To start Teststarter simply execute the `testarter.py` in the root directory.

### Setup experiments
To setup an experiment you will have to go to `Configure Experiment`.
From there you can do the following ections:

- Create experiment
- Delete experiment
- Create
- Create task
- Delete task
- Import experiments
- Export experiments

### Create experiment
Experiments consists of a name and a time of day.
The experiments you create will have a schedule with tasks for the user.
There are three time of day you can choose from: `morn / eve / full`. This allows you to create an experiment with diffrent schedules for diffrent times of the day.

### Delete experiment
Here you can delete your experiments. Once deleted, the experiment and its tasks will be removed.

### Add Task
A Task can be either a Screen with text or your own script. To create a task you have to assign a name and a time.
The time is relative to the start time wich you define when you start the teststarter. 
After you can decide if you want to show a screen with text or execute a command. 
Use the preview to see if everything is working