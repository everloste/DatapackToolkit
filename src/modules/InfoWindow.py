# The "About Datapack Tools" window
from PySide6 import QtWidgets, QtCore

class AboutWidget(QtWidgets.QDialog):
	def __init__(self):
		super().__init__()
		self.setWindowTitle("About Datapack Toolkit")
		self.setFixedWidth(400)

		# The program title
		self.text = QtWidgets.QLabel('''<h1 style='color:#beabee;'>Datapack Toolkit</h1> v0.25.4.6<br>''')

		# App description
		self.desc = QtWidgets.QLabel("Easily configure Minecraft worldgen datapacks.")

		# Minecraft/Mojang disclaimer
		self.disclaimer = QtWidgets.QLabel('''<i>Minecraft</i> is a trademark of Mojang AB. This app is not affiliated with, endorsed, sponsored, or approved by Mojang. For more information about Minecraft, visit the official <a href=\'https://www.minecraft.net/\'>Minecraft website.</a>''')
		self.disclaimer.setWordWrap(True)

		# Information about Qt
		self.disclaimer2 = QtWidgets.QLabel('''This app uses <i>Qt for Python</i>, which is licensed under GNU LGPL. See <a href=\'https://www.qt.io/qt-licensing/\'>the official webpage</a> for an overview of Qt licensing.<br>''')
		self.disclaimer2.setWordWrap(True)

		# Close button
		self.button = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.StandardButton.Close)
		self.button.clicked.connect(self.close)

		# Layout time!!!!!!!!
		self.layout = QtWidgets.QVBoxLayout(self)
		self.layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)

		self.layout.addWidget(self.text)
		self.layout.addWidget(self.desc)
		self.layout.addWidget(self.disclaimer)
		self.layout.addWidget(self.disclaimer2)
		self.layout.addWidget(self.button)
