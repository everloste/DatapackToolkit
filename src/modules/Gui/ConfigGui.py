import zipfile

from PySide6 import QtWidgets, QtGui
from PySide6.QtCore import Qt
from src.modules.Managers.DPConfigHandler import Config
from src.modules.Data import DataHandler


# class ConfigScreenItemWidget(QtWidgets.QWidget):
# 	info: Config.Widget = None
#
# 	def __init__(self, info):
# 		super().__init__()
# 		self.info = info
# 		self.__build__()
#
# 	def __build__(self):
# 		self.layout = QtWidgets.QHBoxLayout()
# 		self.setLayout(self.layout)
#
#
# class ConfigScreen(QtWidgets.QWidget):
#
# 	def __init__(self, pack_name: str):
# 		super().__init__()
#
# 		data = DataHandler()
#
# 		self.config_object = data.customConfigs.get_pack_config(pack_name)
#
# 		self.tab_name = self.config_object.tab_name
#
# 		self.widgets = list()
#
# 		for item in self.config_object.get_widgets():
# 			if item.type == "value":
# 				self.widgets.append(self.ValueWidget(item))
# 			elif item.type == "title":
# 				self.widgets.append(self.TitleWidget(item))
# 			elif item.type == "large_title":
# 				self.widgets.append(self.TitleWidget(item))
#
#
# 		# Layout
#
# 		self.layout = QtWidgets.QVBoxLayout()
# 		self.layout.setSpacing(0)
# 		self.setLayout(self.layout)
#
# 		print(self.widgets)
# 		for w in self.widgets:
# 			self.layout.addWidget(w)
#
# 		self.layout.addItem(QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding))
#
#
#
#
# 	class ValueWidget(ConfigScreenItemWidget):
# 		def __build__(self):
# 			self.layout = QtWidgets.QHBoxLayout()
#
# 			# First we make a little label :3
# 			text = self.info.getText()
# 			if self.info.tooltip: text += "*"
# 			label = QtWidgets.QLabel(text)
# 			self.layout.addWidget(label)
#
# 			if self.info.tooltip: self.setToolTip(self.info.tooltip)
#
# 			# Second the entry widget
# 			self.entry = None
# 			if self.info.value_type == ValueType.Int:
# 				self.entry = QtWidgets.QSpinBox()
# 			elif self.info.value_type == ValueType.Float:
# 				self.entry = QtWidgets.QDoubleSpinBox()
# 			elif self.info.value_type == ValueType.Percent:
# 				self.entry = QtWidgets.QSpinBox()
# 				self.entry.setSuffix("%")
#
#
# 			self.entry.setMinimum(self.info.min_value)
# 			self.entry.setMaximum(self.info.max_value)
# 			if not self.info.input: self.entry.setValue(self.info.default_value)
# 			else: self.entry.setValue(self.info.input)
# 			if self.info.step: self.entry.setSingleStep(self.info.step)
#
# 			self.entry.valueChanged.connect(self.__changed__)
#
# 			self.layout.addWidget(self.entry)
#
# 			self.setLayout(self.layout)
#
# 		def __changed__(self, i):
# 			if self.info.value_type == ValueType.Percent:
# 				i = i/100
# 			self.info.setInput(i)
#
#
# 	class TitleWidget(ConfigScreenItemWidget):
# 		def __build__(self):
# 			self.layout = QtWidgets.QHBoxLayout()
#
# 			text = self.info.getText()
# 			label = QtWidgets.QLabel(f"<h3>{text}</h3>")
# 			self.layout.addWidget(label)
#
# 			self.setLayout(self.layout)
#
#
# 	class LargeTitleWidget(ConfigScreenItemWidget):
# 		def __build__(self):
# 			self.layout = QtWidgets.QHBoxLayout()
#
# 			text = self.info.getText()
# 			label = QtWidgets.QLabel(f"<h2>{text}</h2>")
# 			self.layout.addWidget(label)
#
# 			self.setLayout(self.layout)
#
#


# TYPE UNKNOWN
class TkConfigScreenItemTemplate(QtWidgets.QWidget):
	data: dict = None
	config: Config = None

	def __init__(self, data, config):
		super().__init__()
		self.data = data
		self.config = config
		self.entryWidth = 200
		self.__build__()

	def __build__(self):
		self.layout = QtWidgets.QHBoxLayout()

		label = QtWidgets.QLabel(f"Failed to load widget :(")
		self.layout.addWidget(label)

		self.setLayout(self.layout)


# TYPE image
class TkConfigScreenImage(TkConfigScreenItemTemplate):
	def __build__(self):
		self.layout = QtWidgets.QHBoxLayout()
		self.setLayout(self.layout)

		datapackID = self.config.datapackID

		h = DataHandler()
		dd = h.dataPacks.get_pack_data(datapackID)

		archive = zipfile.ZipFile(dd["path"])
		imgdata = None
		try:
			imgdata = archive.read(self.data["file"])
		except KeyError:
			imgdata = None

		archive.close()

		label = QtWidgets.QLabel()
		if imgdata:
			img = QtGui.QPixmap()
			img.loadFromData(imgdata)
			if "width" in self.data:
				img = img.scaledToWidth(self.data["width"])
			if "height" in self.data:
				img = img.scaledToHeight(self.data["height"])
			label.setPixmap(img)
		else:
			label.setText(f"Failed to load image {self.data['file']}.")

		self.layout.addWidget(label)


# TYPE text
class TkConfigScreenText(TkConfigScreenItemTemplate):
	def __build__(self):
		self.layout = QtWidgets.QHBoxLayout()
		self.setLayout(self.layout)

		text = self.data["text"]
		label = QtWidgets.QLabel(text)

		label.setOpenExternalLinks(True)
		label.setWordWrap(True)

		self.layout.addWidget(label)


# TYPE title/heading
class TkConfigScreenTitle(TkConfigScreenItemTemplate):
	def __build__(self):
		self.layout = QtWidgets.QHBoxLayout()

		text = self.data["text"]
		size = "h1" if self.data["type"] == "title" else "h3"
		label = QtWidgets.QLabel(f"<{size}>{text}</{size}>")
		self.layout.addWidget(label)

		self.setLayout(self.layout)


# TYPE number
class TkConfigScreenSpinbox(TkConfigScreenItemTemplate):
	def __build__(self):
		self.layout = QtWidgets.QHBoxLayout()

		text = self.data["text"]
		label = QtWidgets.QLabel(text)
		self.layout.addWidget(label)

		# Value edit box
		spinnybox = QtWidgets.QSpinBox() if self.data["value"]["type"] != "float" else QtWidgets.QDoubleSpinBox()

		# value/range
		if "range" in self.data["value"]:
			spinnybox.setMinimum(self.data["value"]["range"][0])
			spinnybox.setMaximum(self.data["value"]["range"][1])
		elif self.data["value"]["type"] == "percent":
			spinnybox.setMinimum(50)
			spinnybox.setMaximum(200)
		else:
			spinnybox.setMinimum(1)
			spinnybox.setMaximum(2)

		# value/default
		if "default" in self.data["value"]:
			spinnybox.setValue(self.data["value"]["default"])
		else:
			spinnybox.setValue(spinnybox.minimum())

		# other
		if self.data["value"]["type"] == "percent":
			spinnybox.setSuffix("%")

		if self.data["value"]["type"] == "float":
			if "decimals" in self.data["value"]:
				spinnybox.setDecimals(self.data["value"]["decimals"])
			else:
				spinnybox.setDecimals(2)
			if "step" in self.data["value"]:
				spinnybox.setSingleStep(self.data["value"]["step"])
			else:
				spinnybox.setSingleStep(0.1)

		if "suffix" in self.data["value"]:
			spinnybox.setSuffix(str(self.data["value"]["suffix"]))

		# Finalise
		spinnybox.valueChanged.connect(self._changed)
		spinnybox.setMaximumWidth(self.entryWidth)
		self.layout.addWidget(spinnybox)

		self.setLayout(self.layout)

	def _changed(self, i):
		self.config.inputToMethod(self.data["method"], i)


# TYPE slider
class TkConfigScreenSlider(TkConfigScreenItemTemplate):
	def __build__(self):
		self.layout = QtWidgets.QHBoxLayout()
		self.setLayout(self.layout)

		# The description
		descText = self.data["text"]
		self.desc = QtWidgets.QLabel(descText)
		self.layout.addWidget(self.desc)

		# The slider
		self.mrSlidey = QtWidgets.QSlider()
		self.mrSlidey.setOrientation(Qt.Orientation.Horizontal)

		# value/range
		if "range" in self.data["value"]:
			self.mrSlidey.setMinimum(self.data["value"]["range"][0])
			self.mrSlidey.setMaximum(self.data["value"]["range"][1])
		elif self.data["value"]["type"] == "percent":
			self.mrSlidey.setMinimum(50)
			self.mrSlidey.setMaximum(200)
		else:
			self.mrSlidey.setMinimum(1)
			self.mrSlidey.setMaximum(2)

		# value/step
		if "step" in self.data["value"]:
			self.mrSlidey.setSingleStep(self.data["value"]["step"])
			self.mrSlidey.setTickInterval(self.data["value"]["step"])
		else:
			self.mrSlidey.setSingleStep(1)
			self.mrSlidey.setTickInterval(1)

		# value/default
		if "default" in self.data["value"]:
			self.mrSlidey.setValue(self.data["value"]["default"])
		else:
			self.mrSlidey.setValue(self.mrSlidey.minimum())

		self.mrSlidey.setMaximumWidth(self.entryWidth)
		self.mrSlidey.valueChanged.connect(self._changed)

		# The label for the slider value
		self.valueLabelSuffix = "%" if self.data["value"]["type"] == "percent" else ""
		self.valueLabel = QtWidgets.QLabel(f"{self.mrSlidey.value()}{self.valueLabelSuffix}")

		# We're adding the value label first
		self.layout.addItem(QtWidgets.QSpacerItem(2, 0, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum))
		self.layout.addWidget(self.valueLabel)
		self.layout.addWidget(self.mrSlidey)

	def _changed(self, i):
		self.config.inputToMethod(self.data["method"], i)
		self.valueLabel.setText(f"{i}{self.valueLabelSuffix}")


# TYPE switch
class TkConfigScreenSwitch(TkConfigScreenItemTemplate):
	def __build__(self):
		self.layout = QtWidgets.QHBoxLayout()
		self.setLayout(self.layout)

		# Build the description
		descText = self.data["text"]
		self.desc = QtWidgets.QLabel(descText)

		self.layout.addWidget(self.desc)

		# Build the switch
		if "default" in self.data: self.defaultButtonState = self.data["default"]
		else: self.defaultButtonState = True
		self.buttonState = self.defaultButtonState
		self.button = QtWidgets.QPushButton()
		self.button.clicked.connect(self._changed)
		self.button.setMaximumWidth(self.entryWidth)
		if self.buttonState:
			self.button.setText("Enabled (ON)")
		else:
			self.button.setText("Disabled (OFF)")

		self.layout.addWidget(self.button)

	def _changed(self):
		self.buttonState = (True - self.buttonState)

		if self.buttonState:
			self.button.setText("Enabled (ON)")
		else:
			self.button.setText("Disabled (OFF)")

		if self.buttonState != self.defaultButtonState:
			self.config.inputToMethod(self.data["method"], 1)
		else:
			self.config.inputToMethod(self.data["method"], None)


TkConfigWidgetStringIdentifiers = {
	"text": TkConfigScreenText,
	"title": TkConfigScreenTitle,
	"heading": TkConfigScreenTitle,
	"number": TkConfigScreenSpinbox,
	"value": TkConfigScreenSpinbox,
	"slider": TkConfigScreenSlider,
	"switch": TkConfigScreenSwitch,
	"image": TkConfigScreenImage
}


class TkConfigScreen(QtWidgets.QScrollArea):
	def __init__(self, pack_name: str):
		super().__init__()

		# Set up Qt objects for the GUI
		self.canvas = QtWidgets.QWidget()
		self.layout = QtWidgets.QVBoxLayout()

		self.layout.setSpacing(0)
		self.canvas.setLayout(self.layout)
		self.setWidget(self.canvas)
		self.setWidgetResizable(True)

		# Set up tools to work with the backend
		self.backEnd = DataHandler()
		self.config: Config = self.backEnd.customConfigs.get_pack_config(pack_name)

		# Set up other variables
		self.tabName = self.config.tabName

		# Load all widgets for the screen
		self.widgets = list()

		for data in self.config.getWidgets():
			# Detect what type it is and create appropriate GUI widget
			if data["type"] in TkConfigWidgetStringIdentifiers:
				w = TkConfigWidgetStringIdentifiers[data["type"]](data, self.config)
			else:
				w = TkConfigScreenItemTemplate(data, self.config)

			self.widgets.append(w)
			self.layout.addWidget(w)

		self.layout.addItem(
			QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding))
