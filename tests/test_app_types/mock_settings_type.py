class MockSettings:
	def __init__(self, background_color='#000000', primary_color='#C0C0C0', button_color='#C0C0C0',
				 button_text_color='#000000', active_button_color='#DECADE', inactive_button_color='#FF0000',
				 group_button_color='#F0E68C', success_color='#DADDDC', danger_color='#646464', warning_color='#087F8C',
				 grid_color='#C0C0C0', show_next_task=True, show_play_task_button=True, audio_path='path/to/audio'):
		self.background_color = background_color
		self.primary_color = primary_color
		self.button_color = button_color
		self.button_text_color = button_text_color
		self.active_button_color = active_button_color
		self.inactive_button_color = inactive_button_color
		self.group_button_color = group_button_color
		self.success_color = success_color
		self.danger_color = danger_color
		self.warning_color = warning_color
		self.grid_color = grid_color
		self.show_next_task = show_next_task
		self.show_play_task_button = show_play_task_button
		self.audio_path = audio_path
