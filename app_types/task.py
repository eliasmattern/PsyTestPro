from enum import Enum
from typing import Union


class TaskTypeEnum(Enum):
	TEXT = 'text'
	COMMAND = 'command'
	URL = 'url'


class Task:
	def __init__(self, id: str, name: str, duration: str, task_type: TaskTypeEnum, value: Union[dict[str, str], str],
				 position: int,
				 state: str = 'todo'):
		self.__id = id
		self.__name = name
		self.__duration = duration
		self.__state = state
		self.__position = position
		self.__task_type = task_type
		self.__value = value

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
	def duration(self) -> str:
		return self.__duration

	@duration.setter
	def duration(self, duration: str) -> None:
		self.__duration = duration

	@property
	def task_type(self) -> TaskTypeEnum:
		return self.__task_type

	@task_type.setter
	def task_type(self, task_type: TaskTypeEnum) -> None:
		self.__task_type = task_type

	@property
	def position(self) -> int:
		return self.__position

	@position.setter
	def position(self, position: int) -> None:
		self.__position = position

	@property
	def state(self) -> str:
		return self.__state

	@state.setter
	def state(self, state: str) -> None:
		self.__state = state

	def change_state(self):
		if self.__state == 'todo':
			self.__state = 'skip'
		elif self.__state == 'skip':
			self.__state = 'done'
		else:
			self.__state = 'todo'

	@property
	def value(self) -> dict[str, str] | str:
		return self.__value

	@value.setter
	def value(self, value: dict[str, str] | str) -> None:
		if isinstance(value, dict) and self.__task_type != 'text':
			return
		elif self.__task_type == 'text' and not isinstance(value, dict):
			return
		self.__value = value
