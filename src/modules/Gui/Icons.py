from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

class IconProviderClass:

	def __init__(self):
		self.app = None

	def get(self, icon: str) -> QPixmap:
		theme = self.app.styleHints().colorScheme()

		if theme == Qt.ColorScheme.Light:
			return QPixmap(f"assets/icons/light/{icon}.png")
		else:
			return QPixmap(f"assets/icons/dark/{icon}.png")

	def set_app(self, app):
		self.app = app


Provider = IconProviderClass()