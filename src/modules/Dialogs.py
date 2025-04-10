# Confirmation and warning dialogs
from PySide6 import QtWidgets, QtCore

class ConfirmExportDialog(QtWidgets.QDialog):
	def __init__(self):
		super().__init__()

		# Dialog text
		title = QtWidgets.QLabel("<h3>Are you sure you want to export now?</h3>")
		title.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
		message = QtWidgets.QLabel("You will be asked to select a folder to export to. The program <i>might</i> temporarily freeze.")
		warning = QtWidgets.QLabel("Modified datapacks <b>are not</b> supported by their creators.")
		gap = QtWidgets.QLabel("")

		# Buttons
		self.button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.StandardButton.Ok | QtWidgets.QDialogButtonBox.StandardButton.Cancel)
		self.button_box.accepted.connect(self.accept)
		self.button_box.rejected.connect(self.reject)

		# Layout time!!!!!!!!!!!!!!!!!!!!!!!
		self.layout = QtWidgets.QVBoxLayout()
		self.layout.addWidget(title)
		self.layout.addWidget(message)
		self.layout.addWidget(warning)
		self.layout.addWidget(gap)
		self.layout.addWidget(self.button_box)
		self.setLayout(self.layout)
