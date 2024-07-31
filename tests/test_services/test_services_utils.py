from app_types import Task

TASK_CONFIG_JSON = {
	"globalTasks": {
		"tasks": {
			"0": {
				"is_group": False,
				"name": "TESTTASK",
				"position": 1,
				"time": "00:05:00",
				"state": "todo",
				"type": "text",
				"value": {
					"title": "Title",
					"description": "Description"
				}
			}
		}
	},
	"suite_schedule": {
		"tasks": {
			"0": {
				"is_group": False,
				"name": "TESTTASK",
				"position": 1,
				"time": "00:05:00",
				"state": "todo",
				"type": "text",
				"value": {
					"title": "Title",
					"description": "Description"
				}
			}
		}
	}
}

TASK_FROM_CONFIG = Task('0', 'TESTTASK', '00:05:00', 'text', {"title": "Title", "description": "Description"}, 1)
