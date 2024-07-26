from datetime import datetime, timedelta

from .task import Task


class TaskGroup:
	def __init__(self, id: str, name: str, pause_inbetween: str, loops: int, tasks: dict, position: int):
		self.__id = id
		self.__name = name
		self.__pause_inbetween = timedelta(hours=int(pause_inbetween.split(':')[0]),
										   minutes=int(pause_inbetween.split(':')[1]),
										   seconds=int(pause_inbetween.split(':')[2]))
		self.__loops = loops
		self.__position = position
		self.__tasks: list[Task] = []

		for task_id, task_detail in tasks.items():
			self.__tasks.append(
				Task(task_id, task_detail['name'], task_detail['time'], task_detail['type'], task_detail['value'],
					 task_detail['position'], task_detail['state']))

	@property
	def id(self) -> str:
		return self.__id

	@property
	def name(self) -> str:
		return self.__name

	@name.setter
	def name(self, name: str) -> None:
		self.__name = name

	@property
	def pause_inbetween(self) -> timedelta:
		return self.__pause_inbetween

	@pause_inbetween.setter
	def pause_inbetween(self, pause_inbetween: str) -> None:
		self.__pause_inbetween = timedelta(hours=int(pause_inbetween.split(':')[0]),
										   minutes=int(pause_inbetween.split(':')[1]),
										   seconds=int(pause_inbetween.split(':')[2]))

	@property
	def loops(self) -> int:
		return self.__loops

	@loops.setter
	def loops(self, loops: int) -> None:
		self.__loops = loops

	@property
	def position(self) -> int:
		return self.__position

	@position.setter
	def position(self, position: int) -> None:
		self.__position = position

	@property
	def tasks(self) -> list[Task]:
		return self.__tasks

	@tasks.setter
	def tasks(self, tasks: str) -> None:
		self.__tasks = tasks
