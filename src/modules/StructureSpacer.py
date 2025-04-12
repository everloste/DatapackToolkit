# The manager that takes care of structure (set) configuration
#from src.modules.DatapackManager import DatapackManager
#from src.data.project import META
import json

from src.modules.DatapackManager import DatapackManager


class StructureSpacer:
	relevant_packs: set
	structure_set_objects: dict
	list_of_structure_sets: list

	def __init__(self, dpmanager):
		self.manager = dpmanager
		self.manager.add_child_manager(self)

		self.relevant_packs = set(); self.structure_set_objects = dict(); self.list_of_structure_sets = list()

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
		type: str = "minecraft:random_spread"
		placement_data: dict
		original_placement_data: dict

		def __init__(self, setID: str, source_json: dict = None):
			self.setID = setID
			self.source_json = source_json

			self.type = self.source_json["placement"]["type"]
			self.placement_data = self.source_json["placement"].copy()
			del self.placement_data["type"]
			del self.placement_data["salt"]
			if "spread_type" in self.placement_data:
				del self.placement_data["spread_type"]
			if "frequency_reduction_method" in self.placement_data:
				del self.placement_data["frequency_reduction_method"]
			if "preferred_biomes" in self.placement_data:
				del self.placement_data["preferred_biomes"]
			if "exclusion_zone" in self.placement_data:
				del self.placement_data["exclusion_zone"]
			if "locate_offset" in self.placement_data:
				del self.placement_data["locate_offset"]

			self.original_placement_data = self.placement_data.copy()

		def set_placement_data(self, key: str, n: int):
			self.placement_data[key] = n
			self.modified = True

		def reset_placement_data(self):
			self.placement_data = self.original_placement_data.copy()
			self.modified = False

	########## Getters ##########

	def get_structure_set_list(self) -> list:
		return self.list_of_structure_sets

	def get_original_placement_data(self, setID: str) -> dict:
		return self.structure_set_objects[setID].original_placement_data

	def get_placement_data(self, setID: str) -> dict:
		return self.structure_set_objects[setID].placement_data

	def get_modified(self, setID: str) -> bool:
		return self.structure_set_objects[setID].modified

	def get_json(self, setID: str) -> dict:
		return self.structure_set_objects[setID].source_json

	def get_placement_type(self, setID: str) -> str:
		return self.structure_set_objects[setID].type

	########## Setters ##########

	def set_placement(self, setID: str, key: str, n: int):
		self.structure_set_objects[setID].set_placement_data(key, n)

	def reset_placement(self, setID: str):
		self.structure_set_objects[setID].reset_placement_data()

	def apply_changes_to_pack(self, datapack_object: DatapackManager.Datapack):
		structure_sets = self.get_structure_set_list()

		for structure_set in structure_sets:
			if self.get_modified(structure_set):

				# Get path to structure set file
				path = structure_set.split(":")
				path = f"/{path[0]}/worldgen/structure_set/{path[1]}.json"

				# Modify the JSON data
				data = self.get_json(structure_set)

				placement_data = self.get_placement_data(structure_set)
				for key in placement_data:
					data["placement"][key] = placement_data[key]

				# Inject into final mixer
				datapack_object.rewrite_file(path, json.dumps(data, indent=4))

			# It will not get overwritten if it doesn't exist in the original,
			# but note we are dumping all structure sets there