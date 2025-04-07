import sys
from modules import Dialogs, biomeblender, InfoWindow
from PySide6 import QtCore, QtWidgets, QtGui


class MainWindow(QtWidgets.QMainWindow):
	def __init__(self, master):
		super().__init__()
		self.master     = master
		self.menu       = self.menuBar()

		file_menu = self.menu.addMenu("Datapack")
		import_action = file_menu.addAction("Import datapack")
		import_action.triggered.connect(self.import_datapacks)
		export_action = file_menu.addAction("Export datapack(s)")
		export_action.triggered.connect(self.export_datapacks)

		about_menu = self.menu.addMenu("About")
		about_action = about_menu.addAction("About Datapack Toolkit")
		about_action.triggered.connect(self.show_about_window)

		self.widget = MainWidget()
		self.setCentralWidget(self.widget)
		self.biome_manager = self.widget.biome_manager


	@QtCore.Slot()
	def import_datapacks(self):
		file = QtWidgets.QFileDialog.getOpenFileName(self, "Select datapack", "", "Datapack files (*.zip *.jar)")
		location = file[0]
		self.biome_manager.add_pack(location)

		self.widget.biome_list_widget.update_list()
		self.widget.biome_list_scroll_area.update()
		self.widget.datapack_list_widget.update_list()


	@QtCore.Slot()
	def export_datapacks(self):
		dlg = Dialogs.ConfirmExportDialog()
		if dlg.exec():
			if self.biome_manager.export_datapacks() is not None:
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

		self.biome_manager = biomeblender.BiomeBlender([])

		self.datapack_list_widget = DatapackListWidget(self, self.biome_manager)
		self.biome_list_widget = BiomeListWidget(self.biome_manager)

		# Layout time!!!!!!!!!!
		self.layout = QtWidgets.QHBoxLayout(self)
		self.layout.addWidget(self.datapack_list_widget)
		self.biome_list_scroll_area = QtWidgets.QScrollArea()
		self.biome_list_scroll_area.setWidget(self.biome_list_widget)
		self.biome_list_scroll_area.setWidgetResizable(True)
		self.layout.addWidget(self.biome_list_scroll_area)


class DatapackListWidget(QtWidgets.QListWidget):

	def __init__(self, master, controller: biomeblender.BiomeBlender):
		super().__init__()
		self.master         = master
		self.controller     = controller
		self.entries        = list()
		self.layout         = QtWidgets.QVBoxLayout(self)

		self.setFixedWidth(250)

		self.update_list()


	def update_list(self):
		if hasattr(self, 'entries'):
			for entry in self.entries:
				self.layout.removeWidget(entry)
				entry.deleteLater()

		self.entries.clear()

		for pack in self.controller.packs:
			entry = self.ItemWidget(self, pack["id"])
			self.entries.append(entry)
			self.layout.addWidget(entry)


	class ItemWidget(QtWidgets.QFrame):

		def __init__(self, master, pack_id):
			super().__init__()
			self.packID     = pack_id
			self.master     = master
			self.layout     = QtWidgets.QVBoxLayout(self)

			self.setLineWidth(1); self.setFrameShape(QtWidgets.QFrame.Shape.Box)
			self.setFixedHeight(150)

			self.text = QtWidgets.QLabel(self.packID, alignment=QtCore.Qt.AlignmentFlag.AlignCenter); self.text.setMaximumHeight(75); self.text.setWordWrap(True)
			self.removal_button = QtWidgets.QPushButton(); self.removal_button.setText("Remove"); self.removal_button.clicked.connect(self._remove_)
			self.move_up_button = QtWidgets.QPushButton(); self.move_up_button.setText("Move up"); self.move_up_button.clicked.connect(self._move_up_)

			desc = self.master.controller.get_pack_info(self.packID)["mcmeta"]["pack"]["description"]
			if isinstance(desc, list):
				string = str()
				for entry in desc:
					string += entry["text"]
				desc = string

			self.desc = QtWidgets.QLabel(desc, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)

			self.layout.addWidget(self.text)
			self.layout.addWidget(self.desc)
			self.layout.addWidget(self.move_up_button)
			self.layout.addWidget(self.removal_button)


		def _move_up_(self):
			self.master.controller.move_pack_up(self.packID)
			self.master.update_list()
			self.master.master.biome_list_widget.update_list()


		def _remove_(self):
			self.master.controller.remove_pack(self.packID)
			self.master.update_list()
			self.master.master.biome_list_widget.update_list() # :)


class BiomeListWidget(QtWidgets.QWidget):

	def __init__(self, controller: biomeblender.BiomeBlender):
		super().__init__()
		self.controller     = controller
		self.entries        = list()
		self.layout         = QtWidgets.QVBoxLayout(self)

		self.update_list()


	def update_list(self):
		print("Updating biome list widget...")

		for entry in self.entries:
			self.layout.removeWidget(entry)
			entry.deleteLater()

		self.entries.clear()

		for biome in self.controller.list_all_biomes():
			entry = self.ItemWidget(self, biome)
			self.entries.append(entry)
			self.layout.addWidget(entry)

		self.update()


	class ItemWidget(QtWidgets.QWidget):

		def __init__(self, master, biome):
			super().__init__()
			self.master     = master
			self.biomeID    = biome

			# Biome label time!!!!!!
			self.text = QtWidgets.QLabel(self.biomeID)
			self.text.setFixedWidth(200)
			self.text.setMaximumHeight(75)
			self.text.setWordWrap(True)

			# Dropdown button for options!!!!!!!
			self.options_button = QtWidgets.QComboBox()
			self.options_button.setFixedWidth(200)
			self.options_button.addItems(self.master.controller.get_packs_with_biome(self.biomeID))
			if "minecraft:" in self.biomeID:
				self.options_button.addItem("Vanilla")

			if self.master.controller.get_biome_info(self.biomeID)["changed"]:
				if self.master.controller.get_biome_preference(self.biomeID) is None:
					self.options_button.setCurrentText("Vanilla")
				else:
					self.options_button.setCurrentText(self.master.controller.get_biome_preference(self.biomeID))

			self.options_button.currentTextChanged.connect(self._activated_event_)

			# Layout time!!!!
			self.layout = QtWidgets.QHBoxLayout(self)
			self.layout.addWidget(self.text)
			self.layout.addWidget(self.options_button)


		@QtCore.Slot()
		def _activated_event_(self, selection: str):
			if selection.lower() != "vanilla":
				self.master.controller.set_biome_preference(self.biomeID, selection)
			else:
				self.master.controller.set_biome_preference(self.biomeID, None)


if __name__ == "__main__":
	app = QtWidgets.QApplication([])
	app.setApplicationName("Datapack Toolkit")
	app.setDesktopSettingsAware(True)
	app.setStyle("fusion")

	icon = QtGui.QPixmap()
	icon.load(f"assets/app.ico")
	app.setWindowIcon(icon)

	window = MainWindow(app)
	window.resize(800, 600)
	window.show()

	sys.exit(app.exec())