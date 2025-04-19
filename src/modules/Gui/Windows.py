# The "About Datapack Tools" window
from PySide6 import QtWidgets, QtCore, QtGui
from src.data import project

class InfoWindow(QtWidgets.QDialog):
	def __init__(self):
		super().__init__()
		self.setWindowTitle("About Datapack Toolkit")
		self.setFixedWidth(400)

		# The program title
		version = QtWidgets.QLabel(f'''<b><i>v{project.META.app_version}.</i></b> Check the latest version <a href=\'https://github.com/everloste/DatapackToolkit/releases\'>here.</a>''')
		version.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)
		version.setWordWrap(True)

		img = QtGui.QPixmap("assets/title-export.png")
		img = img.scaledToWidth(300)

		title = QtWidgets.QLabel()
		title.setPixmap(img)
		title.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)

		# App description
		desc = QtWidgets.QLabel("Easily configure Minecraft worldgen datapacks.")
		desc.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)
		desc.setWordWrap(True)

		line = QtWidgets.QFrame(self)
		line.setFrameShape(QtWidgets.QFrame.Shape.HLine)
		line.setStyleSheet("QFrame {color: #808080}")

		# Minecraft/Mojang disclaimer
		disclaimer = QtWidgets.QLabel('''<i>Minecraft</i> is a trademark of Mojang AB. This app is not affiliated with, endorsed, sponsored, or approved by Mojang. For more information about Minecraft, visit the official <a href=\'https://www.minecraft.net/\'>Minecraft website.</a>''')
		disclaimer.setWordWrap(True)

		# Information about Qt
		disclaimer2 = QtWidgets.QLabel('''This app uses <i>Qt for Python</i>, which is licensed under GNU LGPL. See the <a href=\'https://www.qt.io/qt-licensing/\'>official webpage</a> for an overview of Qt licensing.''')
		disclaimer2.setWordWrap(True)

		disclaimer3 = QtWidgets.QLabel("Original creators of modified datapacks are <b>not</b> liable for their functionality. You are configuring them at your own risk.")
		disclaimer3.setWordWrap(True)

		# Close button
		self.button = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.StandardButton.Close)
		self.button.clicked.connect(self.close)

		# Layout time!!!!!!!!
		self.layout = QtWidgets.QVBoxLayout(self)
		#self.layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)

		self.layout.addWidget(title)
		self.layout.addWidget(version)
		self.layout.addWidget(desc)
		self.layout.addWidget(line)
		self.layout.addWidget(disclaimer)
		self.layout.addWidget(disclaimer2)
		self.layout.addWidget(disclaimer3)
		self.layout.addWidget(self.button)

		self.setLayout(self.layout)

		#self.setFixedHeight(250)