import zipfile

from PySide6 import QtWidgets, QtGui
from PySide6.QtCore import Qt
from src.modules.Managers.Configs import Config
from src.modules.Data import DataHandler


# TYPE UNKNOWN
class TkConfigScreenItemTemplate(QtWidgets.QWidget):
	data: dict = None
	config: Config = None

	def __init__(self, data, config):
		super().__init__()
		self.data = data
		self.config = config
		self.entryWidth = 200
		self.textWidth = 300
		self.slots = None
		self.method = None

		if "method" in self.data:
			self.method = self.data["method"]

		if "slots" in self.data:
			self.slots = list()
			if isinstance(self.data["slots"], str):
				self.slots.append(str(self.data["slots"]))
			elif isinstance(self.data["slots"], list):
				for slot in self.data["slots"]:
					self.slots.append(str(slot))

		self.setMinimumWidth(550)
		self.__build__()

	def __build__(self):
		self.layout = QtWidgets.QHBoxLayout()

		label = QtWidgets.QLabel(f"Failed to load widget :(")
		self.layout.addWidget(label)

		self.setLayout(self.layout)

	def insertValues(self, v):
		if self.method is not None:
			self.config.inputToMethod(self.data["method"], v)
		if self.slots is not None:
			self.config.inputToSlot(self.slots, v)


# TYPE image
class TkConfigScreenImage(TkConfigScreenItemTemplate):
	def __build__(self):
		self.layout = QtWidgets.QHBoxLayout()
		self.setLayout(self.layout)

		datapackID = self.config.datapackID

		h = DataHandler()
		dd = h.dataPacks.get_pack_data(datapackID)

		archive = zipfile.ZipFile(dd["path"])
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
			label.setText(f"Failed to load image {self.data['file']}")

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
		label.setFixedWidth(self.textWidth)
		label.setWordWrap(True)
		self.layout.addWidget(label)
		self.layout.addItem(
			QtWidgets.QSpacerItem(2, 0, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum))

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
		spinnybox.valueChanged.connect(self.valueChanged)
		spinnybox.setFixedWidth(self.entryWidth)
		self.layout.addWidget(spinnybox)

		self.setLayout(self.layout)

	def valueChanged(self, i):
		if self.data["value"]["type"] == "percent":
			i = i/100
		self.insertValues(i)


# TYPE slider
class TkConfigScreenSlider(TkConfigScreenItemTemplate):
	def __build__(self):
		self.layout = QtWidgets.QHBoxLayout()
		self.setLayout(self.layout)

		# The description
		descText = self.data["text"]
		self.desc = QtWidgets.QLabel(descText)
		self.desc.setFixedWidth(self.textWidth)
		self.desc.setWordWrap(True)

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

		self.mrSlidey.setFixedWidth(self.entryWidth-40)
		self.mrSlidey.valueChanged.connect(self.valueChanged)

		# The label for the slider value
		self.valueLabelSuffix = "%" if self.data["value"]["type"] == "percent" else ""
		self.valueLabel = QtWidgets.QLabel(f"{self.mrSlidey.value()}{self.valueLabelSuffix}")
		self.valueLabel.setFixedWidth(35)

		# We're adding the value label first
		self.layout.addItem(QtWidgets.QSpacerItem(2, 0, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum))
		self.layout.addWidget(self.valueLabel)
		self.layout.addWidget(self.mrSlidey)

	def valueChanged(self, i):
		self.valueLabel.setText(f"{i}{self.valueLabelSuffix}")

		if self.data["value"]["type"] == "percent":
			i = i/100
		self.insertValues(i)


# TYPE switch
class TkConfigScreenSwitch(TkConfigScreenItemTemplate):
	def __build__(self):
		self.layout = QtWidgets.QHBoxLayout()
		self.setLayout(self.layout)

		# Build the description
		descText = self.data["text"]
		self.desc = QtWidgets.QLabel(descText)
		self.desc.setFixedWidth(self.textWidth)
		self.desc.setWordWrap(True)

		self.layout.addWidget(self.desc)
		self.layout.addItem(
			QtWidgets.QSpacerItem(2, 0, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum))

		# Build the switch
		if "default" in self.data:
			self.defaultButtonState = True if self.data["default"] == "enabled" else False
		else:
			self.defaultButtonState = True

		if "enabled_text" in self.data:
			self.enabledText = self.data["enabled_text"]
		else:
			self.enabledText = "Enabled (On)"

		if "disabled_text" in self.data:
			self.disabledText = self.data["disabled_text"]
		else:
			self.disabledText = "Disabled (Off)"

		self.buttonState = self.defaultButtonState
		self.button = QtWidgets.QPushButton()
		self.button.clicked.connect(self.stateChanged)
		self.button.setFixedWidth(self.entryWidth)

		if self.buttonState:
			self.button.setText(self.enabledText)
		else:
			self.button.setText(self.disabledText)

		self.layout.addWidget(self.button)

	def stateChanged(self):
		self.buttonState = (True - self.buttonState)

		if self.buttonState: self.button.setText(self.enabledText)
		else: self.button.setText(self.disabledText)

		r = 1 if (self.buttonState != self.defaultButtonState) else None
		self.insertValues(r)


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
