# Confirmation and warning dialogs
from PySide6 import QtWidgets

class ConfirmExportDialog(QtWidgets.QDialog):
	def __init__(self):
		super().__init__()

		# Dialog text
		title = QtWidgets.QLabel("Are you sure you want to export now?")
		message = QtWidgets.QLabel("Exporting will extract files into the directory where imported datapacks are located.\nExtracted files will be deleted. The program might temporarily freeze.")

		# Buttons
		self.button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.StandardButton.Ok | QtWidgets.QDialogButtonBox.StandardButton.Cancel)
		self.button_box.accepted.connect(self.accept)
		self.button_box.rejected.connect(self.reject)

		# Layout time!!!!!!!!!!!!!!!!!!!!!!!
		self.layout = QtWidgets.QVBoxLayout()
		self.layout.addWidget(title)
		self.layout.addWidget(message)
		self.layout.addWidget(self.button_box)
		self.setLayout(self.layout)
