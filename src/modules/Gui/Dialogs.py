# Confirmation and warning dialogs
from PySide6.QtCore import Qt
from PySide6 import QtWidgets as qtw
from pathlib import Path

class ExportConfirmationDialog(qtw.QDialog):
	def __init__(self):
		super().__init__()

		# Dialog text
		title = qtw.QLabel("<h3>Are you sure you want to export now?</h3>")
		title.setAlignment(Qt.AlignmentFlag.AlignCenter)
		warning = qtw.QLabel("Original creators of modified datapacks are <b>not</b> liable for their functionality.<br>You are configuring them at your own risk. <i>Here be chickens!</i>")

		# Buttons
		self.button_box = qtw.QDialogButtonBox(qtw.QDialogButtonBox.StandardButton.Ok | qtw.QDialogButtonBox.StandardButton.Cancel)
		self.button_box.accepted.connect(self.accept)
		self.button_box.rejected.connect(self.reject)

		# Layout time!!!!!!!!!!!!!!!!!!!!!!!
		self.layout = qtw.QVBoxLayout()
		self.layout.addWidget(title)
		self.layout.addWidget(warning)
		self.layout.addWidget(self.button_box)
		self.setLayout(self.layout)


class ExportDetailsDialog(qtw.QDialog):
	def __init__(self):
		super().__init__()
		self.layout = qtw.QVBoxLayout()

		# Dialog title
		title = qtw.QLabel("<h3>Export details 🖊</h3>")
		title.setAlignment(Qt.AlignmentFlag.AlignCenter)
		self.layout.addWidget(title)

		line = qtw.QFrame(self)
		line.setFrameShape(qtw.QFrame.Shape.HLine)
		line.setStyleSheet("QFrame {color: #808080}")
		self.layout.addWidget(line)

		# Export location
		export_path_layout = qtw.QHBoxLayout()

		label = qtw.QLabel("Location:")
		export_path_layout.addWidget(label)

		self.location_entry = qtw.QLineEdit()
		self.location_entry.setMinimumWidth(160)
		self.location_entry.setText(str(Path.home()).replace("\\", "/")+"/Downloads")
		self.location_entry.deselect()
		export_path_layout.addWidget(self.location_entry)

		open_location_button = qtw.QPushButton(); export_path_layout.addWidget(open_location_button)
		open_location_button.setText("Browse")
		open_location_button.clicked.connect(self.open_explorer)

		self.layout.addLayout(export_path_layout)

		# Compression?
		self.cmprscheck = qtw.QCheckBox("Compress archives?")
		self.cmprscheck.setChecked(True)

		self.layout.addWidget(self.cmprscheck)

		# Compression level
		compress_level_layout = qtw.QHBoxLayout()

		compress_level_layout.addWidget(qtw.QLabel("Compression level:  "))

		self.compress_slider = qtw.QSlider()
		self.compress_slider.setMaximum(9)
		self.compress_slider.setValue(5)
		self.compress_slider.setOrientation(Qt.Orientation.Horizontal)
		self.compress_slider.valueChanged.connect(self.change_compression_level)
		compress_level_layout.addWidget(self.compress_slider)

		self.compress_level_label = qtw.QLabel("5")
		compress_level_layout.addWidget(self.compress_level_label)

		self.layout.addLayout(compress_level_layout)

		# Buttons
		self.button_box = qtw.QDialogButtonBox(qtw.QDialogButtonBox.StandardButton.Ok | qtw.QDialogButtonBox.StandardButton.Cancel)
		self.button_box.accepted.connect(self.accept)
		self.button_box.rejected.connect(self.reject)

		# Layout time!!!!!!!!!!!!!!!!!!!!!!!

		self.layout.addWidget(self.button_box)
		self.setLayout(self.layout)

		self.setFixedHeight(self.sizeHint().height())
		self.setMinimumWidth(self.sizeHint().width())
		self.setMaximumWidth(self.sizeHint().width()*2)

	def exec(self, /) -> tuple[str, bool, int] | int:
		super().exec()
		if self.result() != 0:
			a = (self.location_entry.text(), self.cmprscheck.isChecked(), int(self.compress_slider.value()))
			return a
		else:
			return 0

	def reject(self):
		super().reject()

	def open_explorer(self):
		export_directory = qtw.QFileDialog.getExistingDirectory()
		print(export_directory)
		if export_directory != "": self.location_entry.setText(export_directory)

	def change_compression_level(self):
		self.compress_level_label.setText(str(self.compress_slider.value()))