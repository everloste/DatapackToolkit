# Confirmation and warning dialogs
from PySide6 import QtWidgets, QtCore

class ConfirmExportDialog(QtWidgets.QDialog):
	def __init__(self):
		super().__init__()

		# Dialog text
		title = QtWidgets.QLabel("<h3>Are you sure you want to export now?</h3>")
		title.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
		warning = QtWidgets.QLabel("Original creators of modified datapacks are <b>not</b> liable for their functionality.<br>You are configuring them at your own risk. <i>Here be chickens!</i>")

		# Buttons
		self.button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.StandardButton.Ok | QtWidgets.QDialogButtonBox.StandardButton.Cancel)
		self.button_box.accepted.connect(self.accept)
		self.button_box.rejected.connect(self.reject)

		# Layout time!!!!!!!!!!!!!!!!!!!!!!!
		self.layout = QtWidgets.QVBoxLayout()
		self.layout.addWidget(title)
		self.layout.addWidget(warning)
		self.layout.addWidget(self.button_box)
		self.setLayout(self.layout)


class ExportDetailsDialog(QtWidgets.QDialog):
	def __init__(self):
		super().__init__()

		# Dialog text
		title = QtWidgets.QLabel("<h3>Export details</h3>")
		title.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

		# Detail info tthings idk
		self.compress_check = QtWidgets.QCheckBox("Compress archives?")
		self.compress_check.setChecked(True)
		self.compress_level = QtWidgets.QDoubleSpinBox(decimals=0, minimum=0, maximum=9, value=5, suffix="/9")
		layout1 = QtWidgets.QHBoxLayout(); layout1.addWidget(QtWidgets.QLabel("Compression level:")); layout1.addWidget(self.compress_level)

		# Buttons
		self.button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.StandardButton.Ok | QtWidgets.QDialogButtonBox.StandardButton.Cancel)
		self.button_box.accepted.connect(self.accept)
		self.button_box.rejected.connect(self.reject)

		# Layout time!!!!!!!!!!!!!!!!!!!!!!!
		self.layout = QtWidgets.QVBoxLayout()
		self.layout.addWidget(title)
		self.layout.addWidget(self.compress_check)
		self.layout.addLayout(layout1)
		self.layout.addWidget(self.button_box)
		self.setLayout(self.layout)

	def exec(self, /) -> tuple[bool, int] | int:
		super().exec()
		if self.result() != 0:
			a = (self.compress_check.isChecked(), int(self.compress_level.value()))
			return a
		else:
			return 0

	def reject(self):
		super().reject()
