import unittest
from unittest.mock import patch, Mock

from services import execute_command

PARTICIPANT_INFO = {
	'participant_id': 'VARIABLE_ID',
	'suite': 'VARIABLE_SUITE',
	'start_time': 'VARIABLE_STARTTIME',
	'timestamp': 'VARIABLE_TIMESTAMP',
	'script_count': 0
}

CUSTOM_VARIABLE = {
	'custom': 'VARIABLE_CUSTOM'
}


def poll():
	return True


class ExecuteCommandTests(unittest.TestCase):

	@patch('shlex.split')
	@patch('subprocess.Popen')
	@patch('pygame.event.get', return_value=[])
	def test_execute_command(self, mock_event_get: Mock, mock_subprocesses_popen: Mock, mock_shlex_split: Mock):
		command = 'command {id}, {suite}, {startTime}, {timestamp}, {scriptCount}, {custom}'
		formatted_command = 'command VARIABLE_ID, VARIABLE_SUITE, VARIABLE_STARTTIME, VARIABLE_TIMESTAMP, 0, VARIABLE_CUSTOM'
		mock_shlex_split.return_value = formatted_command

		mock_process = Mock()
		mock_process.poll.side_effect = [None, True]
		mock_process.wait.return_value = 200
		mock_process.stderr = None

		mock_subprocesses_popen.return_value = mock_process

		error, code = execute_command(command, PARTICIPANT_INFO, CUSTOM_VARIABLE)

		mock_shlex_split.assert_called_once_with(formatted_command, posix=False)
		mock_subprocesses_popen.assert_called_once_with(formatted_command, shell=False)
		self.assertEqual(code, 200)
		self.assertEqual(error, False)
