import sys
from PySide6 import QtCore, QtWidgets, QtGui
from src.modules import Dialogs, InfoWindow
from src.data import project
from src.data import managers


class MainWindow(QtWidgets.QMainWindow):
	def __init__(self, master):
		super().__init__()
		self.master     = master
		self.menu       = self.menuBar()

		file_menu = self.menu.addMenu("Datapack")
		import_action = file_menu.addAction("Open")
		import_action.triggered.connect(self.import_datapacks)
		export_action = file_menu.addAction("Export")
		export_action.triggered.connect(self.export_datapacks)

		about_menu = self.menu.addMenu("About")
		about_action = about_menu.addAction("About Datapack Toolkit")
		about_action.triggered.connect(self.show_about_window)

		self.widget = MainWidget()
		self.setCentralWidget(self.widget)
		#self.biome_manager = self.widget.biome_manager

		self.resize(800, 600)


	@QtCore.Slot()
	def import_datapacks(self):
		file = QtWidgets.QFileDialog.getOpenFileName(self, "Select datapack", "", "Datapack files (*.zip *.jar)")
		location = file[0]

		managers.datapacks.load_pack(location)

		# Legacy BiomeBlender code (to be removed later)
		#self.biome_manager.add_pack(location)
		#self.widget.biome_list_widget.__redraw__()
		self.widget.biome_list_scroll_area.update()

	@QtCore.Slot()
	def export_datapacks(self):
		dlg = Dialogs.ConfirmExportDialog()
		if dlg.exec():

			info = Dialogs.ExportDetailsDialog().exec()

			if info != 0:
				result = managers.datapacks.export_packs(info[0], compress=info[1], level=info[2])

				if result is not None:
					msgBox = QtWidgets.QMessageBox()
					msgBox.setText("Success :3")
					msgBox.exec()


	@QtCore.Slot()
	def show_about_window(self):
		new_window = InfoWindow.AboutWidget()
		new_window.exec()


class MainWidget(QtWidgets.QWidget):
	def __init__(self):
		super().__init__()

		#self.biome_manager = biomeblender.BiomeBlender([])

		self.datapack_list_widget = DatapackListWidget()
		self.biome_list_widget = BiomeListWidget()

		self.workspace = QtWidgets.QTabWidget()

		self.structure_list_widget = StructureSetListWidget()


		# Layout time!!!!!!!!!!
		self.layout = QtWidgets.QHBoxLayout(self)
		self.layout.addWidget(self.datapack_list_widget)
		self.biome_list_scroll_area = QtWidgets.QScrollArea()
		self.biome_list_scroll_area.setWidget(self.biome_list_widget)
		self.biome_list_scroll_area.setWidgetResizable(True)
		#self.layout.addWidget(self.biome_list_scroll_area)

		self.sset_scroll = QtWidgets.QScrollArea()
		self.sset_scroll.setWidget(self.structure_list_widget)
		self.sset_scroll.setWidgetResizable(True)


		self.workspace.addTab(self.biome_list_scroll_area, "Biome providers")
		self.workspace.addTab(self.sset_scroll, "Structure sets")
		self.layout.addWidget(self.workspace)
		


class DatapackListWidget(QtWidgets.QListWidget):

	def __init__(self):
		super().__init__()
		#self.master         = master
		#self.controller     = controller
		self.entries        = list()
		self.layout         = QtWidgets.QVBoxLayout(self)

		self.layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)

		self.setFixedWidth(300)

		managers.datapacks.add_child_widget(self)
		self.__redraw__()


	def __redraw__(self):
		if hasattr(self, 'entries'):
			for entry in self.entries:
				self.layout.removeWidget(entry)
				entry.deleteLater()

		self.entries.clear()

		for pack in managers.datapacks.get_pack_list():
			entry = self.DatapackItemWidget(self, pack)
			self.entries.append(entry)
			self.layout.addWidget(entry)


	class DatapackItemWidget(QtWidgets.QFrame):

		def __init__(self, master, pack_id):
			super().__init__()

			# Init normal
			self.packID = pack_id
			self.layout = QtWidgets.QVBoxLayout(self)
			manager = managers.datapacks

			# Init legacy (to be removed)
			self.master = master

			# Widget styling
			self.setStyleSheet("DatapackItemWidget {border: 2px solid #808080; border-radius: 10px}")
			self.setFrameShape(QtWidgets.QFrame.Shape.Box)
			self.setLineWidth(1)
			self.setMinimumHeight(50)
			self.setMaximumHeight(150)

			# Widget labels
			self.id_label = QtWidgets.QLabel(f"<h3>{self.packID}</h3>", alignment=QtCore.Qt.AlignmentFlag.AlignCenter); self.id_label.setMaximumHeight(75); self.id_label.setWordWrap(True)
			self.removal_button = QtWidgets.QPushButton(); self.removal_button.setText("Remove"); self.removal_button.clicked.connect(self._remove_)
			self.move_up_button = QtWidgets.QPushButton(); self.move_up_button.setText("Move up"); self.move_up_button.clicked.connect(self._move_up_)

			# Pack icon code
			img = QtGui.QPixmap()
			img.loadFromData(managers.datapacks.get_pack_icon(self.packID))
			img = img.scaledToWidth(75)
			self.icon = QtWidgets.QLabel(); self.icon.setPixmap(img)

			# Description code
			desc = manager.get_pack_description(self.packID)
			self.desc = QtWidgets.QLabel(desc)

			# Layout time!!!!!!!!!
			self.layout.addWidget(self.id_label)

			self.layout_for_description = QtWidgets.QHBoxLayout()
			self.layout_for_description.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
			self.layout_for_description.addWidget(self.icon)
			self.layout_for_description.addSpacing(5)
			self.layout_for_description.addWidget(self.desc)

			self.layout_for_buttons = QtWidgets.QHBoxLayout()

			self.layout_for_buttons.addWidget(self.move_up_button)
			self.layout_for_buttons.addWidget(self.removal_button)

			self.layout.addLayout(self.layout_for_description)
			self.layout.addLayout(self.layout_for_buttons)


		def _move_up_(self):
			managers.datapacks.move_up(self.packID)

		def _remove_(self):
			managers.datapacks.remove_pack(self.packID)


class BiomeListWidget(QtWidgets.QWidget):

	def __init__(self):
		super().__init__()
		#self.controller     = controller
		self.entries        = list()
		self.layout         = QtWidgets.QVBoxLayout(self)

		managers.datapacks.add_child_widget(self)
		self.__redraw__()


	def __redraw__(self):
		print("Updating biome list widget...")

		for entry in self.entries:
			self.layout.removeWidget(entry)
			entry.deleteLater()

		self.entries.clear()

		for biome in managers.biomes.biome_list:
			entry = self.ItemWidget(biome)
			self.entries.append(entry)
			self.layout.addWidget(entry)

		self.update()


	class ItemWidget(QtWidgets.QWidget):

		def __init__(self, biome: str):
			super().__init__()
			self.biomeID    = biome

			# Biome label time!!!!!!
			self.text = QtWidgets.QLabel(self.biomeID)
			self.text.setFixedWidth(200)
			self.text.setMaximumHeight(75)
			self.text.setWordWrap(True)

			# Dropdown button for options!!!!!!!
			self.options_button = QtWidgets.QComboBox()
			self.options_button.setFixedWidth(200)
			self.options_button.addItems(managers.biomes.get_packs_with_biome(self.biomeID))
			if "minecraft:" in self.biomeID:
				self.options_button.addItem("Vanilla")

			if managers.biomes.get_biome_changed(self.biomeID):
				if managers.biomes.get_biome_preference(self.biomeID) is None:
					self.options_button.setCurrentText("Vanilla")
				else:
					self.options_button.setCurrentText(managers.biomes.get_biome_preference(self.biomeID))

			self.options_button.currentTextChanged.connect(self._activated_event_)

			# Layout time!!!!
			self.layout = QtWidgets.QHBoxLayout(self)
			self.layout.addWidget(self.text)
			self.layout.addWidget(self.options_button)


		@QtCore.Slot()
		def _activated_event_(self, selection: str):
			if selection.lower() != "vanilla":
				managers.biomes.set_biome_preference(self.biomeID, selection)
			else:
				managers.biomes.set_biome_preference(self.biomeID, None)


class StructureSetListWidget(QtWidgets.QWidget):
	def __init__(self):
		super().__init__()
		self.entries        = list()
		self.layout         = QtWidgets.QVBoxLayout(self)
		self.manager        = managers.structure_sets

		self.layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)

		managers.datapacks.add_child_widget(self)
		self.__redraw__()

	def __redraw__(self):
		for entry in self.entries:
			self.layout.removeWidget(entry)
			entry.deleteLater()

		self.entries.clear()

		for structure_set in self.manager.get_structure_set_list():
			entry = self.ItemWidget(structure_set)
			self.entries.append(entry)
			self.layout.addWidget(entry)

		self.update()

	class ItemWidget(QtWidgets.QWidget):
		def __init__(self, setID: str):
			super().__init__()
			self.setID = setID
			self.layout = QtWidgets.QHBoxLayout(self)
			self.text = QtWidgets.QLabel(setID)
			self.text.setFixedWidth(200)

			# Buttons
			config_layout = QtWidgets.QVBoxLayout()

			self.entries = dict()
			data = managers.structure_sets.get_placement_data(self.setID)
			for key in data:

				label = QtWidgets.QLabel()
				label.setText(f"{key.capitalize()}:".replace("_", " "))
				label.setStyleSheet("QLabel {text-decoration: underline}")

				if isinstance(data[key], int):
					self.entries[key] = QtWidgets.QDoubleSpinBox(
						decimals=0,
						minimum=0,
						maximum=4096,
						value=data[key]
					)
					self.entries[key].type = int
					self.entries[key].valueChanged.connect(self._changed_)

					if key == "spacing":
						label.setToolTip("Average distance (in chunks) between two neighboring generation attempts. Value from 0 to 4096 (inclusive).")
					elif key == "separation":
						label.setToolTip("Minimum distance (in chunks) between two neighboring attempts. Value from 0 to 4096 (inclusive).")
					elif key == "distance":
						label.setToolTip("The thickness of a ring <i>plus</i> that of a gap between two rings. Value from 0 to 1023 (inclusive). <b>Unit is 6 chunks.</b>")
						self.entries[key].setMaximum(1023)
					elif key == "count":
						label.setToolTip("The total number of generation attempts in a dimension. Value from 1 to 4095 (inclusive).")
						self.entries[key].setMinimum(1)
						self.entries[key].setMaximum(4095)
					elif key == "spread":
						label.setToolTip("How many attempts are on the ring closest to spawn. Value from 0 to 1023 (inclusive).")
						self.entries[key].setMaximum(1023)
					else:
						label.setToolTip("Unknown key. Value range unknown.")

				elif isinstance(data[key], float):
					self.entries[key] = QtWidgets.QDoubleSpinBox(
						decimals=4,
						minimum=0,
						maximum=1,
						value=data[key],
						singleStep=0.1
					)
					self.entries[key].type = float
					self.entries[key].valueChanged.connect(self._changed_)

					if key == "frequency":
						label.setToolTip("Probability of generation if conditions are met.")
					else:
						label.setToolTip("Unknown key. Value range unknown.")

				else:
					print(key +"  " + str(type(data[key])))
					self.entries[key] = QtWidgets.QLineEdit(text=str(data[key]))
					self.entries[key].textChanged.connect(self._changed_)

				self.entries[key].setMaximumWidth(200)

				layout = QtWidgets.QHBoxLayout()
				layout.addWidget(label)
				layout.addWidget(self.entries[key])

				config_layout.addLayout(layout)

			# Button for resetting everything
			reset_button = QtWidgets.QPushButton("Reset to original")
			reset_button.setMaximumWidth(200)
			reset_button.pressed.connect(self.reset_options)

			config_layout.addWidget(reset_button)

			# Layout time!!
			self.layout.addWidget(self.text)
			self.layout.addLayout(config_layout)

		def reset_options(self):
			managers.structure_sets.reset_placement(self.setID)
			for key in self.entries:
				try:
					self.entries[key].setValue(managers.structure_sets.get_original_placement_data(self.setID)[key])
				except AttributeError:
					self.entries[key].setText(managers.structure_sets.get_original_placement_data(self.setID)[key])
				self.entries[key].update()

		def _changed_(self):
			for key in self.entries:
				try:
					if self.entries[key].type == int:
						managers.structure_sets.set_placement(self.setID, key, int(self.entries[key].value()))
					else:
						managers.structure_sets.set_placement(self.setID, key, self.entries[key].value())
				except AttributeError:
					managers.structure_sets.set_placement(self.setID, key, self.entries[key].text())


class App(QtWidgets.QApplication):
	def __init__(self):
		self.setStyle(project.META.default_theme)
		self.setDesktopSettingsAware(True)
		super().__init__()
		self.setStyleSheet("QTabBar::tab:selected {font-weight: bold}")
		self.setApplicationName(project.META.app_name)

		icon = QtGui.QPixmap()
		icon.load(f"assets/icon.png")
		self.setWindowIcon(icon)


if __name__ == "__main__":
	app = App()

	window = MainWindow(app)
	window.show()

	sys.exit(app.exec())