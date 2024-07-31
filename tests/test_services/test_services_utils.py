from app_types import Task, TaskGroup

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
			},
			"1": {
				"is_group": True,
				"name": "GROUP",
				"pause": "00:02:00",
				"loops": 2,
				"tasks": {
					"0": {
						"is_group": False,
						"name": "TASKOFGROUP",
						"time": "00:10:00",
						"state": "todo",
						"type": "text",
						"value": {
							"title": "TITLE",
							"description": "DESCRIPTION"
						},
						"position": 1
					}
				},
				"position": 2
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

			},
			"1": {
				"is_group": True,
				"name": "GROUP",
				"pause": "00:02:00",
				"loops": 2,
				"tasks": {
					"0": {
						"is_group": False,
						"name": "TASKOFGROUP",
						"time": "00:10:00",
						"state": "todo",
						"type": "text",
						"value": {
							"title": "TITLE",
							"description": "DESCRIPTION"
						},
						"position": 1
					}
				},
				"position": 2
			}
		}
	}
}

TASK_FROM_CONFIG = Task('0', 'TESTTASK', '00:05:00', 'text', {"title": "Title", "description": "Description"}, 1)

GROUP_FROM_CONFIG = TaskGroup('1', 'GROUP', '00:02:00', 2, {
	'0': {'name': 'TESTTASK', 'time': '00:05:00', 'type': 'text',
		  'value': {"title": "Title", "description": "Description"}, 'state': 'todo', 'position': 1}}, 2)
