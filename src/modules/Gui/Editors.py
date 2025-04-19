from PySide6 import QtCore, QtWidgets, QtGui
from src.modules.Data import DataHandler
from src.modules.Gui import Icons as ICONS


class DatapackListWidget(QtWidgets.QScrollArea):

	def __init__(self):
		super().__init__()
		self.entries = dict()
		self.order = list()

		self.cool_widget = QtWidgets.QWidget()
		self.cool_layout = QtWidgets.QVBoxLayout(self)
		self.cool_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
		self.cool_widget.setLayout(self.cool_layout)

		self.setWidget(self.cool_widget)
		self.setWidgetResizable(True)
		self.setFixedWidth(300)

		self.dh = DataHandler()

		self.dh.dataPacks.add_child_widget(self)
		self.__redraw__(None)

	def __redraw__(self, reason):
		self.order = self.dh.dataPacks.get_pack_list()

		remove = set()
		for pack in self.entries:
			self.cool_layout.removeWidget(self.entries[pack])
			if pack not in self.order:
				self.entries[pack].deleteLater()
				remove.add(pack)
		for pack in remove:
			del self.entries[pack]

		for pack in self.order:
			if pack in self.entries:
				self.cool_layout.addWidget(self.entries[pack])
			else:
				self.entries[pack] = self.DatapackItemWidget(pack)
				self.cool_layout.addWidget(self.entries[pack])


	class DatapackItemWidget(QtWidgets.QFrame):

		def __init__(self, pack_id):
			super().__init__()

			# Init normal
			self.packID = pack_id
			self.layout = QtWidgets.QVBoxLayout(self)
			self.dh = DataHandler()

			# Widget styling
			self.setStyleSheet("DatapackItemWidget {border: 1px solid #808080; border-radius: 5px}")
			self.setFrameShape(QtWidgets.QFrame.Shape.Box)
			self.setLineWidth(1)
			self.setMinimumHeight(50)
			self.setMaximumHeight(150)

			# Widget labels
			self.id_label = QtWidgets.QLabel(f"<h3>{self.packID}</h3>", alignment=QtCore.Qt.AlignmentFlag.AlignCenter); self.id_label.setMaximumHeight(75); self.id_label.setWordWrap(True)
			self.removal_button = QtWidgets.QPushButton(); self.removal_button.setText("Remove"); self.removal_button.clicked.connect(self._remove_)
			self.move_up_button = QtWidgets.QPushButton(); self.move_up_button.setText("Move up"); self.move_up_button.clicked.connect(self._move_up_)
			self.removal_button.setIcon(ICONS.Provider.get("delete"))
			self.move_up_button.setIcon(ICONS.Provider.get("up"))

			# Pack icon code
			img = QtGui.QPixmap()
			img.loadFromData(self.dh.dataPacks.get_pack_icon(self.packID))
			img = img.scaledToWidth(75)
			self.icon = QtWidgets.QLabel(); self.icon.setPixmap(img)

			# Description code
			desc = self.dh.dataPacks.get_pack_description(self.packID)
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
			self.dh.dataPacks.move_up(self.packID)

		def _remove_(self):
			self.dh.dataPacks.remove_pack(self.packID)


class BiomeListWidget(QtWidgets.QWidget):

	def __init__(self):
		super().__init__()
		#self.controller     = controller
		self.entries        = list()
		self.layout         = QtWidgets.QVBoxLayout(self)
		self.backend = DataHandler()

		self.backend.dataPacks.add_child_widget(self)
		self.__redraw__(None)

	def __redraw__(self, reason):
		#print("Updating biome list widget...")

		for entry in self.entries:
			self.layout.removeWidget(entry)
			entry.deleteLater()

		self.entries.clear()

		for biome in self.backend.biomeProviders.biome_list:
			entry = self.ItemWidget(biome, self.backend)
			self.entries.append(entry)
			self.layout.addWidget(entry)

		self.update()

	class ItemWidget(QtWidgets.QWidget):

		def __init__(self, biome: str, backend):
			super().__init__()
			self.biomeID    = biome
			self.dh = backend

			# Biome label time!!!!!!
			human_text = self.biomeID.split(":")[1].replace("_", " ").title()
			self.text = QtWidgets.QLabel(f"<b>{human_text}</b><br><i>{self.biomeID}</i>")
			self.text.setFixedWidth(200)
			self.text.setMaximumHeight(75)
			self.text.setWordWrap(True)

			# Dropdown button for options!!!!!!!
			self.options_button = QtWidgets.QComboBox()
			self.options_button.setFixedWidth(200)
			self.options_button.addItems(self.dh.biomeProviders.get_packs_with_biome(self.biomeID))
			if "minecraft:" in self.biomeID:
				self.options_button.addItem("Vanilla")

			if self.dh.biomeProviders.get_biome_changed(self.biomeID):
				if self.dh.biomeProviders.get_biome_preference(self.biomeID) is None:
					self.options_button.setCurrentText("Vanilla")
				else:
					self.options_button.setCurrentText(self.dh.biomeProviders.get_biome_preference(self.biomeID))

			self.options_button.currentTextChanged.connect(self._activated_event_)

			# Layout time!!!!
			self.layout = QtWidgets.QHBoxLayout(self)
			self.layout.addWidget(self.text)
			self.layout.addWidget(self.options_button)


		@QtCore.Slot()
		def _activated_event_(self, selection: str):
			if selection.lower() != "vanilla":
				self.dh.biomeProviders.set_biome_preference(self.biomeID, selection)
			else:
				self.dh.biomeProviders.set_biome_preference(self.biomeID, None)


class StructureSetListWidget(QtWidgets.QWidget):
	def __init__(self):
		super().__init__()
		self.entries        = list()
		self.layout         = QtWidgets.QVBoxLayout(self)
		#self.manager        = managers.structure_sets
		self.dh = DataHandler()

		self.layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)

		self.dh.dataPacks.add_child_widget(self)
		self.__redraw__(None)

	def __redraw__(self, reason):
		for entry in self.entries:
			self.layout.removeWidget(entry)
			entry.deleteLater()

		self.entries.clear()

		for structure_set in self.dh.structureSets.get_structure_set_list():
			entry = self.ItemWidget(structure_set, self.dh)
			self.entries.append(entry)
			self.layout.addWidget(entry)

		self.update()

	class ItemWidget(QtWidgets.QWidget):
		def __init__(self, setID: str, backend: DataHandler):
			super().__init__()
			self.setID = setID
			self.layout = QtWidgets.QHBoxLayout(self)
			self.text = QtWidgets.QLabel(setID)
			self.text.setFixedWidth(200)
			self.dh = backend

			# Buttons
			config_layout = QtWidgets.QVBoxLayout()

			self.entries = dict()
			data = self.dh.structureSets.get_placement_data(self.setID)
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
					#print(key +"  " + str(type(data[key])))
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
			self.dh.structureSets.reset_placement(self.setID)
			for key in self.entries:
				try:
					self.entries[key].setValue(self.dh.structureSets.get_original_placement_data(self.setID)[key])
				except AttributeError:
					self.entries[key].setText(self.dh.structureSets.get_original_placement_data(self.setID)[key])
				self.entries[key].update()

		def _changed_(self):
			for key in self.entries:
				try:
					if self.entries[key].type == int:
						self.dh.structureSets.set_placement(self.setID, key, int(self.entries[key].value()))
					else:
						self.dh.structureSets.set_placement(self.setID, key, self.entries[key].value())
				except AttributeError:
					self.dh.structureSets.set_placement(self.setID, key, self.entries[key].text())