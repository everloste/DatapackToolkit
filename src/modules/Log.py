import os, datetime
from src.data.project import META

# A log-writing singleton.
# Serves only to create the backend log for the app.
class Writer:
	_instance = None

	def __new__(cls, *args, **kwargs):
		if not cls._instance:
			cls._instance = super().__new__(cls)
		return cls._instance

	def __init__(self):
		if not hasattr(self, '_initialized'):
			print("Initializing log")
			self._initialized = True

			self.log_folder = f"{META.root}/logs"

			if not os.path.exists(self.log_folder):
				os.makedirs(self.log_folder)

			self.log_file_path = f"{self.log_folder}/latest.log"
			self.log_file = open(self.log_file_path, "w+", encoding="UTF-8")
			self.log_file.close()

			self.print("Log created")

	def print(self, text):
		now = datetime.datetime.now()
		line = f"[{now}] {text}\n"

		self.log_file = open(self.log_file_path, "a+", encoding="UTF-8")
		self.log_file.write(line)
		self.log_file.close()

	def end(self):
		self.print("App closed")

	def __del__(self):
		self.print("Log writing terminated")
