# The manager that takes care of structure (set) configuration
#from src.modules.DatapackManager import DatapackManager
#from src.data.project import META
import json


class StructureSpacer:
	relevant_packs = set()
	structure_set_objects = dict()
	list_of_structure_sets = list()

	def __init__(self, dpmanager):
		self.manager = dpmanager
		self.manager.add_child_manager(self)

		self.__update__()

	# This runs when packs are added/moved/removed
	def __update__(self):

		# Add packs that have structures into our list
		self.relevant_packs.clear()
		for pack in self.manager.get_pack_list():
			if "structure_set" in self.manager.get_pack_modules(pack):
				self.relevant_packs.add(pack)

		# Find all structure sets in datapacks
		structure_sets = set(); jsons = dict()
		for pack in self.relevant_packs:
			archive = self.manager.open_pack_archive(pack)
			sets = [x.split("/worldgen/structure_set/")[0].split("/")[-1] + ":" + x.split("/worldgen/structure_set/")[-1].removesuffix(".json") for x in archive.namelist() if "/worldgen/structure_set/" in x and ".json" in x]
			[structure_sets.add(x) for x in sets]

			for entry in sets:
				files = [x for x in archive.namelist() if str(entry.split(":")[0] + "/worldgen/structure_set/" + entry.split(":")[1] + ".json") in x]
				jsons[entry] = json.loads(archive.read(files[-1]))

			archive.close()

		self.list_of_structure_sets = list(structure_sets)
		self.list_of_structure_sets.sort()

		# Now create editable entries for these structure sets, -if- they don't exist
		for structure_set in self.list_of_structure_sets:

			if (structure_set not in self.structure_set_objects) or (not self.structure_set_objects[structure_set].modified):
				self.structure_set_objects[structure_set] = self.StructureSetItem(structure_set, source_json=jsons[structure_set])


	class StructureSetItem:
		setID = str()
		modified: bool = False
		source_json: dict
		spacing_original: int = 0
		separation_original: int = 0
		spacing_new: int = 0
		separation_new: int = 0

		def __init__(self, setID: str, source_json: dict = None):
			self.setID = setID
			self.source_json = source_json

		def set_spacing(self, n: int):
			self.spacing_new = n
			self.modified = True

		def set_separation(self, n: int):
			self.separation_new = n
			self.modified = True

	########## Getters ##########

	def get_structure_set_list(self) -> list:
		return self.list_of_structure_sets

	########## Setters ##########

	def set_spacing(self, setID: str, n: int):
		self.structure_set_objects[setID].set_spacing(n)

	def set_separation(self, setID: str, n: int):
		self.structure_set_objects[setID].set_separation(n)