from dataclasses import dataclass

def biome_id_from_path(path: str) -> str:
	split_path = path.split("/")
	i = len(split_path) - (split_path[::-1]).index("data")
	biome = "/".join(split_path[i:]).replace("/worldgen/biome/", ":").removesuffix(".json")
	return biome


class BiomeBlender:
	relevant_packs = list()
	biome_list = list()
	biomes_in_pack = dict()
	biome_objects = dict()

	def __init__(self, dpmanager):
		self.manager = dpmanager
		self.manager.add_child_manager(self)

		self.__update__()

	# This runs when packs are added/moved/removed
	def __update__(self):

		# Reset things
		self.relevant_packs.clear()
		self.biomes_in_pack.clear()

		# Find relevant packs (ones with biome files)
		for pack in self.manager.get_pack_list():
			if "biome" in self.manager.get_pack_modules(pack):
				self.relevant_packs.append(pack)

		# In those packs, find biome files
		biomes = set()
		for pack in self.relevant_packs:
			archive = self.manager.open_pack_archive(pack) # Open pack archive using the Datapack Manager object
			self.biomes_in_pack[pack] = set() # Might as well reset this
			paths = archive.namelist();  archive.close()
			for path in paths:
				if (path[-5:] == ".json") and ("/worldgen/biome/" in path) and ("/tags/" not in path):
					biome = biome_id_from_path(path)
					biomes.add(biome)
					self.biomes_in_pack[pack].add(biome)

		self.biome_list = list(biomes)
		self.biome_list.sort()

		# Lastly create editable biome objects/items
		# CURRENTLY THIS RESETS EVERY TIME SO FINISH THAT CODE THANK U
		for biome in self.biome_list:

			packs_with_biome = list()
			for pack in self.relevant_packs:
				if biome in self.biomes_in_pack[pack]:
					packs_with_biome.append(pack)

			if biome in self.biome_objects:
				if self.get_biome_changed(biome):
					self.biome_objects[biome].packs = packs_with_biome
				else:
					self.biome_objects[biome] = self.BiomeItem(biomeID=biome, packs=packs_with_biome, preference=packs_with_biome[0])
			else:
				self.biome_objects[biome] = self.BiomeItem(biomeID=biome, packs=packs_with_biome, preference=packs_with_biome[0])

	#################### Biome handler dataclass ####################

	@dataclass(slots=True)
	class BiomeItem:
		biomeID: str
		packs: list
		preference: str | None = None
		changed: bool = False

	#################### Getter functions ####################

	def get_biome_preference(self, biomeID):
		return self.biome_objects[biomeID].preference

	def get_biome_changed(self, biomeID):
		return self.biome_objects[biomeID].changed

	def get_packs_with_biome(self, biomeID: str) -> list:
		return self.biome_objects[biomeID].packs

	#################### Setting functions ####################

	def apply_changes_to_pack(self, path: str):
		pass

	def set_biome_preference(self, biomeID: str, preference: str):
		self.biome_objects[biomeID].preference = preference
		self.biome_objects[biomeID].changed = True