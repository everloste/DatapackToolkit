from PySide6 import QtWidgets
from src.modules.Gui import ConfigGui
from src.modules.Data import DataHandler
from src.modules.Gui.Editors import BiomeListWidget, StructureSetListWidget


class TabbedWorkspaceWidget(QtWidgets.QTabWidget):
	def __init__(self):
		super().__init__()
		self.configScreens = dict()
		self.backend = DataHandler()

		# Create editors
		self.biome_editor = BiomeListWidget()
		self.structure_set_editor = StructureSetListWidget()

		# Add them as tabs
		area1 = QtWidgets.QScrollArea(widgetResizable=True)
		area1.setWidget(self.biome_editor)
		self.addTab(area1, "Biome providers")

		area2 = QtWidgets.QScrollArea(widgetResizable=True)
		area2.setWidget(self.structure_set_editor)
		self.addTab(area2, "Structure sets")

		# Link self to receive updates
		self.backend.dataPacks.add_child_widget(self)


	def __redraw__(self, reason):
		configable_packs = self.backend.customConfigs.get_packs()

		# Clear buttons from the tab bar except the first two
		for i in range(self.count()-1, 1, -1):
			self.removeTab(i)

		# Add the tabs back
		for pack in configable_packs:
			# Set up the config screen widget if it doesn't exist
			if pack not in self.configScreens: self.configScreens[pack] = ConfigGui.TkConfigScreen(pack)

			# Add the scroll area as a tab
			self.addTab(self.configScreens[pack], self.configScreens[pack].tabName)

			# Loaded, but unused config screens (for packs that were removed) stay in memory for now
