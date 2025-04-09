# The datapack manager for loading, unloading, analysing, and merging packs
import zipfile, json
from typing import Type
from zipfile import ZipFile

class DatapackManager:
	datapacks: dict = dict()
	pack_order: list = list()
	children_managers: list = list()
	children_widgets: list = list()

	def __init__(self):
		pass

	def __update_everything__(self):
		for child in self.children_managers:
			child.__update__()
		for child in self.children_widgets:
			child.__redraw__()

	def load_pack(self, path: str) -> str:
		archive = zipfile.ZipFile(path, 'r')

		try:
			json.loads(archive.read("pack.mcmeta"))

		except KeyError or FileNotFoundError:
			raise FileNotFoundError("Could not load pack.mcmeta. Archive is not a datapack!!! >:(")

		else:
			data = {
				"id":           path.split("/")[-1],
				"path":         path,
				"directory":    "/".join(path.split("/")[:-1]),
				"mcmeta":       json.loads(archive.read("pack.mcmeta")),
				"name":         "Unknown pack",
				"description":  "A Minecraft datapack",
				"modules":      set(),
				"icon":         bytes(),
			}

			try:
				data["icon"] = archive.read("pack.png")
			except KeyError:
				data["icon"] = None

			# Modules are things that the datapack modifies - biomes, structures, etc. - list only things that are relevant for this program
			files = archive.namelist(); modules = list()
			for file in files:
				if "/structure_set/" in file:
					modules.append("structure_set")
				elif "/biome/" in file:
					modules.append("biome")
				elif "/template_pool/" in file:
					modules.append("template_pool")
				elif "/loot_table/" in file:
					modules.append("loot_table")
				elif "minecraft/dimension/overworld.json" in file:
					modules.append("dimension/overworld")

			data["modules"] = set(modules)

			archive.close()

			self.datapacks[data["id"]] = data.copy()
			self.update_pack_data(data["id"])
			self.pack_order.append(data["id"])

			self.__update_everything__()

			return data["id"]

	def add_child_manager(self, manager: object):
		self.children_managers.append(manager)

	def add_child_widget(self, widget: object):
		self.children_widgets.append(widget)

	def update_pack_data(self, dpack: str):
		data = self.datapacks[dpack]

		# Update the pack name, if possible
		if "id" in data["mcmeta"]["pack"]:
			data["name"] = data["mcmeta"]["pack"]["id"].capitalize()
		elif "name" in data["mcmeta"]["pack"]:
			data["name"] = data["mcmeta"]["pack"]["name"].capitalize()
		else:
			data["name"] = data["id"]

		# Update the pack description
		description = data["mcmeta"]["pack"]["description"]
		if isinstance(description, list):
			string = str()
			for entry in description:
				line = str()
				if "color" in entry:
					color = entry["color"]
					line += f'''<font style='color:{color};'>'''
					line += entry["text"]
					line += "</font>"
				else:
					line = entry["text"]
				line = line.replace("\n", "<br>")
				string += line

			description = string
		data["description"] = description

	def remove_pack(self, dpack: str) -> Type[ValueError] | str:
		try:
			self.pack_order.remove(dpack)
			del self.datapacks[dpack]

			self.__update_everything__()
			return dpack

		except ValueError:
			print(f"DPManager: Tried to remove '{dpack}', but it is not present in list")
			return ValueError

	def move_up(self, dpack: str) -> list:
		i = self.pack_order.index(dpack)
		if i >= 1:
			self.pack_order.remove(dpack)
			self.pack_order.insert(i-1, dpack)
		self.__update_everything__()
		return self.pack_order

	########## Getters ##########

	def get_pack_data(self, dpack: str) -> dict:
		return self.datapacks[dpack]

	def get_pack_description(self, dpack: str) -> str:
		return self.datapacks[dpack]["description"]

	def get_pack_icon(self, dpack: str) -> bytes:
		return self.datapacks[dpack]["icon"]

	def get_pack_modules(self, dpack: str) -> set:
		return self.datapacks[dpack]["modules"]

	def get_pack_list(self) -> list:
		return self.pack_order

	def open_pack_archive(self, dpack: str) -> ZipFile:
		archive = zipfile.ZipFile(self.get_pack_data(dpack)["path"], 'r')
		return archive


#from PySide6 import QtWidgets, QtGui
# from src.modules.StructureSpacer import StructureSpacer
#
# test = DatapackManager()
# structures_test = StructureSpacer(test)
#
# packid1 = test.load_pack(f"C:/Users/{os.getlogin()}/Downloads/minecraft-1.21.5-client-dp.jar")
# packid2 = test.load_pack(f"C:/Users/{os.getlogin()}/Downloads/Terralith_1.21_v2.5.8.zip")
# pack = packid2
#
# print(test.get_pack_list())
#
# print(structures_test.get_structure_set_list())
#
# structures_test.set_spacing("minecraft:villages", 99)
#
#
# app = QtWidgets.QApplication([])
# app.setApplicationName(test.get_pack_data(pack)["name"])
# app.setDesktopSettingsAware(True)
# app.setStyle("fusion")
#
# msg = QtWidgets.QMessageBox()
# msg.setMaximumWidth(1000)
# msg.setText(test.get_pack_description(pack))
#
# img = QtGui.QPixmap()
# img.loadFromData(test.get_pack_icon(pack))
# img = img.scaledToWidth(50)
#
# msg.setIconPixmap(img)
#
# msg.show()
#
# sys.exit(app.exec())