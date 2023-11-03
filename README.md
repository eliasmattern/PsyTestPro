# Teststarter

Teststarter is a Python program developed using the Pygame library that allows users to create and manage experiments. With Teststarter, users can define experiments, each of which consists of a series of tasks. These tasks can be customized to suit specific requirements.

The user interface of Teststarter is intentionally designed to be predominantly black. This deliberate choice is driven by its primary application in sleep studies. By minimizing light emission, Teststarter ensures a conducive environment for conducting experiments, where even the slightest disruptions from external sources of light are mitigated.

## Key Features
### Experiment Creation: 
Users can easily create experiments by specifying the tasks they want to include and setting up a schedule for when each task should be executed.

### Customizable Tasks: 
For each task within an experiment, users have the flexibility to select their own scripts, allowing for a wide range of experimental designs and functionalities.

### Schedule Management: 
Teststarter provides a scheduling system that displays the upcoming tasks and their respective execution times. This allows users to have a clear overview of the experiment's timeline.

### Automated Execution: 
Once an experiment is started, Teststarter will automatically manage the execution of tasks according to the predefined schedule. When a task's scheduled time arrives, Teststarter will launch the corresponding script.

## Table of Contens

- [Teststarter](#teststarter)
  - [Key Features](#key-features)
    - [Experiment Creation:](#experiment-creation)
    - [Customizable Tasks:](#customizable-tasks)
    - [Schedule Management:](#schedule-management)
    - [Automated Execution:](#automated-execution)
  - [Table of Contens](#table-of-contens)
  - [Installation](#installation)
  - [How to run Teststarter](#how-to-run-teststarter)
    - [Start Settings](#start-settings)
    - [Schedule](#schedule)
    - [Run tasks](#run-tasks)
  - [Configure Teststarter](#configure-teststarter)
    - [Create experiment](#create-experiment)
    - [Delete experiment](#delete-experiment)
    - [Add Task](#add-task)
    - [Delete task](#delete-task)
    - [Export experiments](#export-experiments)
    - [Import experiments](#import-experiments)
  - [FAQ](#faq)

## Installation
To install Teststarter you can either download this GitHub project as a ZIP and unpack it, or you can clone the repository using git:

```git
git clone LINK
```

To use Teststarter python must be installed:
[Download here](https://www.python.org/downloads/)

There are also some dependencies that must be installed using pip:

```python
pip install pygame
pip install pygame_widgets
pip install tk
pip install tktimepicker
pip install tkcalendar
pip install pandas
```

## How to run Teststarter
To start Teststarter simply execute the `testarter.py` in the root directory.

### Start Settings
To start an experiment, and its schedule, you have to put in the following values:
| Name  | Description |
| ------------- | ------------- |
| Participant ID  | Name of the task  |
| Time of Day  | Starting time of the task.<br />Relative to the start time  |
| Week Number  | Command to execute your own script*  |
| Start Time  | Time, when the experiment should start |

When everything is filled out correctly, you can press submit

### Schedule
After you start an experiment, you will see a table with all the tasks and their start time and state. There you can modify to each task. 

You can change the Date, Time and State. The State shows if a Task is todo, should be skipped, or is done. 

### Run tasks
Use the button `Run Teststarter` to start the Teststarter with your schedule.
When it started, there will be a timer until the next Task. When it reaches 0 it 
plays the task and sets it to `done`.

You can always press `Play next task` to start the next task without waiting for the timer to run out.

If a task is `todo` but in the past, teststarter will immediately start it. 
This ensures that no task is being skipped when another task is taking longer or
the teststarter was started too late.
If you do not want this, set the tasks, which are in the past, to `skip` or `done`. 

## Configure Teststarter

To set up an experiment, you will have to go to `Configure Experiment`.
From there, you can do the following actions:

- Create experiment
- Delete experiment
- Create task
- Delete task
- Import experiments
- Export experiments

### Create experiment
Experiments consist of a name and a time of day.
The experiments you create will have a schedule with tasks for the user.
There are three time of day you can choose from: `morn / eve / full`. This allows you to create an experiment with different schedules for different times of the day.

### Delete experiment
Here you can delete your experiments. Once deleted, the experiment and its tasks will be removed.

### Add Task
A task can be either a screen with text or your own script. To create a task, you have to assign a name and a time.
The time is relative to the start time which you define when you start the teststarter. 

Task properties

| Name  | Description |
| ------------- | ------------- |
| Name  | Name of the task  |
| Time  | Starting time of the task.<br />Relative to the start time  |
| Command  | Command to execute your own script*  |
| Title  | Title of the screen with text  |
| Description  | Description of the screen with text  |

<p style="color: #d7ba7d; font-size: 0.8em; line-height: 1.1em;">
* Use relative paths instead of absolute paths to execute a file. <br /> 
A relative path starts in the directory you are in. An absolute path has the entire file path. This can be a problem when you use the schedule on a different computer. <br />
Example: <br />
 C:\users\[username]\Desktop\teststarter\scripts\your_own.script <br />
 Because of the username in your path, it will only work on your computer. <br>
 instead use: <br />
 .\scripts\your_own.script <br />
 This will go from the teststarter folder into the script folder to access your script. 
 Therefore, it would work on any computer which has the script at this location.</p>

Before you save a task, use the preview to see if everything is working.

### Delete task
Here, you can delete tasks from experiments. Once deleted, the task will be removed.

### Export experiments
This will export all your experiments, their tasks and schedule.
It will create a CSV in the `./exports/` folder.
You can use this CSV to Import the experiments again.
<p style="color: #CC7F7F; font-size: 0.8em; line-height: 1.1em;">
NOTE: This will not export your own scripts. You will have to transfer these by yourself.</p>

### Import experiments
This allows you to choose a CSV on your computer to import Experiments and their tasks

## FAQ
<strong>What scripts are supported?</strong><br /> Any scripts, which you can execute from the console are supported by Teststarter