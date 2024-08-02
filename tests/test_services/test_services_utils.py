from app_types import Task, TaskGroup
from tests.test_app_types import MockSettings

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
						"name": "TESTTASK",
						"time": "00:05:00",
						"state": "todo",
						"type": "text",
						"value": {
							"title": "Title",
							"description": "Description"
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
						"name": "TESTTASK",
						"time": "00:05:00",
						"state": "todo",
						"type": "text",
						"value": {
							"title": "Title",
							"description": "Description"
						},
						"position": 1
					}
				},
				"position": 2
			}
		}
	}
}

TASK_CONFIG_JSON_WITH_DELETED_TASK = {
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
						"name": "TESTTASK",
						"time": "00:05:00",
						"state": "todo",
						"type": "text",
						"value": {
							"title": "Title",
							"description": "Description"
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
			"1": {
				"is_group": True,
				"name": "GROUP",
				"pause": "00:02:00",
				"loops": 2,
				"tasks": {
					"0": {
						"is_group": False,
						"name": "TESTTASK",
						"time": "00:05:00",
						"state": "todo",
						"type": "text",
						"value": {
							"title": "Title",
							"description": "Description"
						},
						"position": 1
					}
				},
				"position": 1
			}
		}
	}
}

TASK_FROM_CONFIG = Task('0', 'TESTTASK', '00:05:00', 'text', {"title": "Title", "description": "Description"}, 1)

GROUP_FROM_CONFIG = TaskGroup('1', 'GROUP', '00:02:00', 2, {
	'0': {'name': 'TESTTASK', 'time': '00:05:00', 'type': 'text',
		  'value': {"title": "Title", "description": "Description"}, 'state': 'todo', 'position': 1}}, 2)

CUSTOM_VARIABLES = ['var1', 'var2']

SETTINGS_JSON = {
	"language": "en",
	"backgroundColor": "#000000",
	"primaryColor": "#C0C0C0",
	"buttonColor": "#C0C0C0",
	"buttonTextColor": "#000000",
	"successColor": "#DECADE",
	"dangerColor": "#FF0000",
	"warningColor": "#F0E68C",
	"activeButtonColor": "#DADDDC",
	"inactiveButtonColor": "#646464",
	"groupButtonColor": "#087F8C",
	"gridColor": "#C0C0C0",
	"showNextTask": True,
	"showPlayTaskButton": True,
	"audioPath": "path/to/audio"
}

NEW_SETTINGS = MockSettings('new', 'new', 'new', 'new', 'new', 'new', 'new', 'new', 'new', 'new', 'new', False, False,
							'new')
