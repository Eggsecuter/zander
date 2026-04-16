class Logger:
	__logs_enabled: bool = False

	@staticmethod
	def enable_logs():
		Logger.__logs_enabled = True

	@staticmethod
	def log(message: str):
		if Logger.__logs_enabled:
			print(message)
