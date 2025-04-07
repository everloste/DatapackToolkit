# The datapack manager for loading, unloading, analysing, and merging packs
# indev!!!!!!
import sys, os, zipfile, json
from PySide6 import QtWidgets, QtGui

# currently unused - will be improved and used later on
class DatapackManager:
	datapacks: dict = dict()
	pack_order: list = list()

	def __init__(self):
		pass

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

			return data["id"]

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

	def get_pack_data(self, dpack: str) -> dict:
		return self.datapacks[dpack]

	def get_pack_description(self, dpack: str) -> str:
		return self.datapacks[dpack]["description"]

	def get_pack_icon(self, dpack: str) -> bytes:
		return self.datapacks[dpack]["icon"]

	def get_pack_list(self) -> list:
		return self.pack_order


test = DatapackManager()
packid1 = test.load_pack(f"C:/Users/{os.getlogin()}/Downloads/Geophilic v3.4 f15-71.dp.zip")
packid2 = test.load_pack(f"C:/Users/{os.getlogin()}/Downloads/Terralith_1.21_v2.5.8.zip")
print(test.get_pack_list())


pack = packid2


app = QtWidgets.QApplication([])
app.setApplicationName(test.get_pack_data(pack)["name"])
app.setDesktopSettingsAware(True)
app.setStyle("fusion")

msg = QtWidgets.QMessageBox()
msg.setMaximumWidth(1000)
msg.setText(test.get_pack_description(pack))

img = QtGui.QPixmap()
img.loadFromData(test.get_pack_icon(pack))
img = img.scaledToWidth(50)

msg.setIconPixmap(img)

msg.show()

sys.exit(app.exec())