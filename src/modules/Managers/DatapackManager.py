# The datapack manager for loading, unloading, analysing, and merging packs
import zipfile, json, os, shutil
from typing import Type
from zipfile import ZipFile, ZIP_DEFLATED, ZIP_STORED
from src.data.project import META
from dataclasses import dataclass, field
from src.enums import WidgetUpdateReason
import src.modules.Log as Log

# This is for optimising things
import time


class DatapackManager:
	datapacks: dict = dict()
	pack_order: list = list()
	children_managers: list = list()
	children_widgets: list = list()

	def __init__(self):
		self.log = Log.Writer()

	def __update_children__(self, reason):
		for child in self.children_managers:
			child.__update__()
		for child in self.children_widgets:
			#print(f"Updating {child}")
			child.__redraw__(reason)

	def load_pack(self, path: str) -> str:
		archive = zipfile.ZipFile(path, 'r')

		try:
			json.loads(archive.read("pack.mcmeta"))

		except KeyError or FileNotFoundError:
			self.log.printWarn(f"Didn't load {path} - no pack.mcmeta file present")
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
				"config":       None
			}

			# Make sure we can't load the same pack twice
			if data["id"] in self.get_pack_list():
				raise FileExistsError

			# Check if a pack icon exists
			try:
				data["icon"] = archive.read("pack.png")
			except KeyError:
				data["icon"] = None

			# Detect modules:
			# Modules are things that the datapack modifies - biomes, structures, etc. - list only things that are relevant for this program
			files = archive.namelist(); modules = set()

			for file in files:
				if "/structure_set/" in file:
					modules.add("structure_set")
				elif "/worldgen/biome/" in file:
					modules.add("biome")
				elif "minecraft/dimension/overworld.json" in file:
					modules.add("dimension/overworld")
				elif "dpconfig.json" in file:
					modules.add("dpconfig")

			data["modules"] = set(modules)

			if "dpconfig" in data["modules"]:
				data["config"] = json.loads(archive.read("dpconfig.json"))

			# Close archive and finalise
			archive.close()

			self.datapacks[data["id"]] = data.copy()
			self.update_pack_data(data["id"])
			self.pack_order.append(data["id"])

			self.__update_children__(WidgetUpdateReason.DatapackAddition)

			self.log.printInfo(f'''Loaded {path} as '{data["id"]}' ''')

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

				if "bold" in entry and entry["bold"]:
					line = f"<b>{line}</b>"
				if "italic" in entry and entry["italic"]:
					line = f"<i>{line}</i>"
				if "underlined" in entry and entry["underlined"]:
					line = f"<u>{line}</u>"

				line = line.replace("\n", "<br>")

				string += line

			description = string
		data["description"] = description

	def remove_pack(self, dpack: str) -> Type[ValueError] | str:
		try:
			self.pack_order.remove(dpack)
			del self.datapacks[dpack]

			self.__update_children__(WidgetUpdateReason.DatapackRemoval)
			return dpack

		except ValueError:
			print(f"DPManager: Tried to remove '{dpack}', but it is not present in list")
			return ValueError

	def move_up(self, dpack: str) -> list:
		i = self.pack_order.index(dpack)
		if i >= 1:
			self.pack_order.remove(dpack)
			self.pack_order.insert(i-1, dpack)
		self.__update_children__(WidgetUpdateReason.DatapackOrderChange)
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

	def get_pack_config(self, dpack: str) -> dict:
		return self.datapacks[dpack]["config"]

	def get_pack_list(self) -> list:
		return self.pack_order

	def get_pack_path(self, dpack: str) -> str:
		return self.datapacks[dpack]["path"]

	def get_pack_directory(self, dpack: str) -> str:
		return self.datapacks[dpack]["directory"]

	def open_pack_archive(self, dpack: str) -> ZipFile:
		archive = zipfile.ZipFile(self.get_pack_data(dpack)["path"], 'r')
		return archive

	########## Export ##########

	def export_packs(self, export_dir: str, compress: bool = True, level: int = 5) -> bool:

		timer: float = time.perf_counter()

		# Create temporary directory to work in
		temp_dir = f"{META.root}/temp"
		if not os.path.exists(temp_dir):
			os.makedirs(temp_dir)

		# Copy datapacks to temporary directory
		for pack in self.get_pack_list():
			path = self.get_pack_path(pack)

			if not os.path.exists(path):
				raise FileNotFoundError

			temp_path = f"{temp_dir}/{pack}"

			shutil.copy(path, temp_path)

			# Open archive to make changes
			archive = zipfile.ZipFile(temp_path, "r")
			datapack = self.Datapack(archive=archive, path=temp_path)

			# Now we may edit it
			timer1: float = time.perf_counter()
			for child_manager in self.children_managers:
				child_manager.apply_changes_to_pack(datapack)

			timer1 = time.perf_counter() - timer1
			print(f"[EXPORT] Called managers to apply changes to {datapack.name}. This took {round(timer1 * 1000)} ms. See log for detailed info")

			datapack.apply(compress=compress, level=level)

			# Close it
			datapack.archive.close()
			del datapack

			# And export it
			copy_path = f"{temp_path}.temp"
			pack_rename = f"Modified copy of {pack}"
			new_path = f"{export_dir}/{pack_rename}"
			shutil.move(copy_path, new_path)

		# Delete temporary directory
		shutil.rmtree(temp_dir)

		timer = time.perf_counter() - timer
		print(f"[EXPORT] Exported datapacks to filesystem. The whole process took a total of {round(timer * 1000)} ms")

		return True

	@dataclass(slots=True)
	class Datapack:
		path: str
		archive: zipfile.ZipFile
		name: str = ""
		files_to_disable: list = field(default_factory=list)
		files_to_enable: list = field(default_factory=list)
		files_to_rewrite: dict = field(default_factory=dict)

		def __post_init__(self):
			self.name = self.path.split("/")[-1]

		def disable_files(self, files: list | tuple):
			[self.files_to_disable.append(file) for file in files]

		def enable_files(self, files: list | tuple):
			[self.files_to_enable.append(file) for file in files]

		def rewrite_file(self, path: str, new_content: str):
			self.files_to_rewrite[path] = new_content

		def apply(self, compress: bool = True, level: int = 5):
			temp_path = f"{self.path}.temp"

			log = Log.Writer()
			log.printInfo(f"Final write for '{self.name}':\n\tDisabling files: {self.files_to_disable}\n\tEnabling files: {self.files_to_enable}\n\tRewriting files: {self.files_to_rewrite.keys()}")

			timer: float = time.perf_counter()

			compression = ZIP_DEFLATED if compress == True else ZIP_STORED
			with (zipfile.ZipFile(temp_path, "w", compression=compression, compresslevel=level) as final):

				for item in self.archive.infolist():
					data = self.archive.read(item.filename)
					new_name = item.filename

					for rule in self.files_to_disable:
						if rule[:2] != "./" and item.filename.endswith(rule) \
						or (rule[:2] == "./" and rule[2:] == item.filename):
							new_name = f"{item.filename}.disabled"

					for rule in self.files_to_enable:
						if rule[:2] != "./" and item.filename.endswith(f"{rule}.disabled") \
						or (rule[:2] == "./" and f"{rule[2:]}.disabled" == f"{item.filename}.disabled"):
							new_name = item.filename.removesuffix(".disabled")

					for rule in self.files_to_rewrite:
						if (rule[:2] != "./" and item.filename.endswith(rule)) \
						or (rule[:2] == "./" and rule[2:] == item.filename):
							data = self.files_to_rewrite[rule]

					final.writestr(new_name, data)

			timer = time.perf_counter() - timer
			print(f"[EXPORT] Written files to archive for {self.name}. This took {round(timer * 1000)} ms. See log for detailed info")
