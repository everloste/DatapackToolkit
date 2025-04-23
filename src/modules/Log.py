import os, datetime
from src.data.project import META, LOG_VERBOSITY_LEVEL
from PySide6 import QtWidgets

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

			self.browserWidget = None

			self.print("New log created")

	def print(self, text):
		now = datetime.datetime.now()
		line = f"[{now}] {text}\n"

		self.log_file = open(self.log_file_path, "a+", encoding="UTF-8")
		self.log_file.write(line)
		self.log_file.close()

		if self.browserWidget is not None:
			self.browserWidget.updateLog()

	def printInfo(self, text):
		if META.log_verbosity_level >= LOG_VERBOSITY_LEVEL.ALL:
			self.print(text)

	def printWarn(self, text):
		if META.log_verbosity_level >= LOG_VERBOSITY_LEVEL.WARN:
			self.print(f"[WARN] {text}")

	def printError(self, text):
		if META.log_verbosity_level >= LOG_VERBOSITY_LEVEL.ERROR:
			self.print(f"[ERROR] {text}")

	def end(self):
		self.print("App closed")

	def __del__(self):
		self.print("Log writing somehow terminated")

	def addBrowserWidget(self, w):
		self.browserWidget = w


class BrowserWidget(QtWidgets.QWidget):
	def __init__(self):
		super().__init__()
		self.layout = QtWidgets.QVBoxLayout(self)
		self.setLayout(self.layout)

		self.writerObject = Writer()
		self.writerObject.addBrowserWidget(self)

		self.changeLogStateButton = QtWidgets.QPushButton("Log verbosity: Everything")
		self.changeLogStateButton.clicked.connect(self.buttonStateChanged)
		self.layout.addWidget(self.changeLogStateButton)

		self.textBox = QtWidgets.QTextBrowser()
		self.textBox.setText("this is a text browser")
		self.layout.addWidget(self.textBox)

		self.buttonLayout = QtWidgets.QHBoxLayout()

		self.openFileButton = QtWidgets.QPushButton("Open log file")
		self.openFileButton.clicked.connect(self.openFile)
		self.buttonLayout.addWidget(self.openFileButton)

		self.layout.addLayout(self.buttonLayout)

		self.updateLog()
		self.resize(500, 600)

	def updateLog(self):
		log_file = open(self.writerObject.log_file_path, "r", encoding="UTF-8")
		self.textBox.setText(log_file.read())
		log_file.close()

	def openFile(self):
		os.startfile(self.writerObject.log_file_path)

	def buttonStateChanged(self):
		META.log_verbosity_level += 1
		if META.log_verbosity_level > LOG_VERBOSITY_LEVEL.ALL:
			META.log_verbosity_level = 0
		strings = [
			"Nothing",
			"Only errors",
			"Warns and errors",
			"Everything"
		]
		ns = strings[META.log_verbosity_level]
		self.changeLogStateButton.setText(f"Log verbosity: {ns}")