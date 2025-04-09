from PySide6 import QtCore, QtWidgets, QtGui
import src.data.managers as managers


class StructureSetListItem(QtWidgets.QWidget):
	def __init__(self, setID: str):
		super().__init__()
		self.structure_setID = setID
		self.text = QtWidgets.QLabel(setID)

		# Buttons
		self.spacing_entry = QtWidgets.QDoubleSpinBox(decimals=0, suffix=" chunks", minimum=0, maximum=4096,
		                                              value=managers.structure_sets.get_original_spacing(
			                                              self.structure_setID))
		self.separation_entry = QtWidgets.QDoubleSpinBox(decimals=0, suffix=" chunks", minimum=0, maximum=4096,
		                                                 value=managers.structure_sets.get_original_separation(
			                                                 self.structure_setID))
		self.spacing_entry.valueChanged.connect(self.__spacing_changed__)
		self.separation_entry.valueChanged.connect(self.__separation_changed__)
		self.spacing_label = QtWidgets.QLabel("Spacing:")
		self.spacing_label.setToolTip("Average distance between two structures.")
		self.separation_label = QtWidgets.QLabel("Separation:")
		self.separation_label.setToolTip("Minimum distance between two structures.")
		self.spacing_layout = QtWidgets.QHBoxLayout()
		self.spacing_layout.addWidget(self.spacing_label)
		self.spacing_layout.addWidget(self.spacing_entry)
		self.separation_layout = QtWidgets.QHBoxLayout()
		self.separation_layout.addWidget(self.separation_label)
		self.separation_layout.addWidget(self.separation_entry)
		self.config_layout = QtWidgets.QVBoxLayout()
		self.config_layout.addLayout(self.spacing_layout)
		self.config_layout.addLayout(self.separation_layout)
		self.reset_button = QtWidgets.QPushButton("Reset to original")
		self.reset_button.pressed.connect(self.reset_options)
		self.config_layout.addWidget(self.reset_button)

		# Layout time!!
		self.layout = QtWidgets.QHBoxLayout(self)
		self.layout.addWidget(self.text)
		self.layout.addLayout(self.config_layout)

	def reset_options(self):
		managers.structure_sets.reset_spacing(self.structure_setID)
		managers.structure_sets.reset_separation(self.structure_setID)

	def __spacing_changed__(self, n: float):
		print(n)
		if n == managers.structure_sets.get_original_spacing(self.structure_setID):
			managers.structure_sets.reset_spacing(self.structure_setID)
		else:
			managers.structure_sets.set_spacing(self.structure_setID, n)

	def __separation_changed__(self, n: float):
		if n == managers.structure_sets.get_original_separation(self.structure_setID):
			managers.structure_sets.reset_separation(self.structure_setID)
		else:
			managers.structure_sets.set_separation(self.structure_setID, n)