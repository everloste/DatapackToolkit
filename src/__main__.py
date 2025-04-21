# Import Qt
from PySide6 import QtCore, QtWidgets, QtGui
import sys

# Import GUI (and ONLY Gui)
import src.modules.Gui.Dialogs as Dialogs
import src.modules.Gui.Icons as Icons
import src.modules.Gui.Workspaces as Workspace
import src.modules.Gui.Windows as Windows
from src.modules.Gui.Editors import DatapackListWidget

# Import Data
from src.data import project
from src.modules.Data import DataHandler
import src.modules.Log as Log


class App(QtWidgets.QApplication):
	def __init__(self):
		super().__init__()
		self.setApplicationName(project.META.app_name)
		self.setDesktopSettingsAware(True)
		self.setStyle(project.META.default_theme)
		self.setWindowIcon(QtGui.QPixmap("./assets/icon.png"))

		self.logProcess = Log.Writer()
		Icons.Provider.set_app(self)

		self.aboutToQuit.connect(self.onQuit)

	def onQuit(self):
		self.logProcess.end()


class MainWindow(QtWidgets.QMainWindow):
	def __init__(self):
		super().__init__()
		self.setCentralWidget(MainWindowWidget())
		self.menubar = None
		self.createMenuBar()
		self.resize(950, 600)

	def createMenuBar(self):
		self.menubar = self.menuBar()

		file_menu = self.menubar.addMenu("Datapack")
		a1 = file_menu.addAction("Open")
		a1.triggered.connect(self.loadDatapacks)
		a2 = file_menu.addAction("Export")
		a2.triggered.connect(self.exportDatapacks)

		about_menu = self.menubar.addMenu("About")
		b2 = about_menu.addAction("Open current log")
		b2.triggered.connect(self.showLog)
		b1 = about_menu.addAction("About Datapack Toolkit")
		b1.triggered.connect(self.showInfoWindow)

	@QtCore.Slot()
	def loadDatapacks(self):
		files = QtWidgets.QFileDialog.getOpenFileNames(self, "Select datapacks", "", "Datapacks (*.zip *.jar)")

		for location in files[0]:
			data.dataPacks.load_pack(location)

	@QtCore.Slot()
	def exportDatapacks(self):
		ask = Dialogs.ExportConfirmationDialog()
		if ask.exec():
			info = Dialogs.ExportDetailsDialog().exec()
			if info != 0:
				result = data.dataPacks.export_packs(info[0], compress=info[1], level=info[2])
				if result is not None:
					msg = QtWidgets.QMessageBox(text="Success! :3")
					msg.exec()

	@QtCore.Slot()
	def showInfoWindow(self):
		new_window = Windows.InfoWindow()
		new_window.exec()

	@QtCore.Slot()
	def showLog(self):
		self.logBrowser = Log.BrowserWidget()
		self.logBrowser.show()


class MainWindowWidget(QtWidgets.QWidget):
	def __init__(self):
		super().__init__()
		self.layout = QtWidgets.QHBoxLayout(self)

		self.dp_list = DatapackListWidget()
		self.layout.addWidget(self.dp_list)

		self.workspace = Workspace.TabbedWorkspaceWidget()
		self.layout.addWidget(self.workspace)


# class MainWidget(QtWidgets.QWidget):
# 	def __init__(self):
# 		super().__init__()
#
# 		managers.datapacks.add_child_widget(self)
# 		self.workspace = QtWidgets.QTabWidget()
#
# 		self.datapack_list_widget = DatapackListWidget()
# 		self.biome_list_widget = BiomeListWidget()
# 		self.structure_list_widget = StructureSetListWidget()
#
# 		self.config_screens = dict()
#
# 		# Layout time!!!!!!!!!!
# 		self.layout = QtWidgets.QHBoxLayout(self)
#
# 		self.layout.addWidget(self.datapack_list_widget)
#
# 		self.biome_list_scroll_area = QtWidgets.QScrollArea()
# 		self.biome_list_scroll_area.setWidget(self.biome_list_widget)
# 		self.biome_list_scroll_area.setWidgetResizable(True)
# 		#self.layout.addWidget(self.biome_list_scroll_area)
#
# 		self.sset_scroll = QtWidgets.QScrollArea()
# 		self.sset_scroll.setWidget(self.structure_list_widget)
# 		self.sset_scroll.setWidgetResizable(True)
#
#
# 		self.workspace.addTab(self.biome_list_scroll_area, "Biome providers")
# 		self.workspace.addTab(self.sset_scroll, "Structure sets")
# 		self.layout.addWidget(self.workspace)
#
# 		self.config_screen_tab_bar_indexes = dict()
#
# 	def __redraw__(self):
# 		for pack in managers.custom_cfgs.get_packs():
# 			if pack not in self.config_screens:
# 				self.config_screens[pack] = DPTConfigGui.DatapackConfigScreen(pack)
#
# 				area = QtWidgets.QScrollArea()
# 				area.setWidgetResizable(True)
# 				area.setWidget(self.config_screens[pack])
#
# 				i = self.workspace.addTab(area, self.config_screens[pack].tab_name)
# 				self.config_screen_tab_bar_indexes[pack] = i
#
#
# 		removals = set()
# 		for pack in self.config_screens:
# 			if pack not in managers.custom_cfgs.get_packs():
# 				removals.add(pack)
# 				self.workspace.removeTab(self.config_screen_tab_bar_indexes[pack])
#
# 		for pack in removals:
# 			del self.config_screens[pack]


if __name__ == "__main__":
	sys.setrecursionlimit(sys.getrecursionlimit()*2)
	print(f"Doubled recursion limit to {sys.getrecursionlimit()}.")

	data = DataHandler()
	print(f"Initialized the data handler.")
	app = App()

	main_window = MainWindow()
	main_window.show()

	sys.exit(app.exec())