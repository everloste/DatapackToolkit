import zipfile, json, os, shutil

# this will later be superseded by a better thing
class BiomeBlender:

	def __init__(self, packs: list = None):
		self.pack_locations = [] if packs is None else packs
		self.packs = list()
		self.biome_list = dict()

		for pack_location in self.pack_locations:
			self.add_pack(pack_location)


	def add_pack(self, pack_location: str) -> str:
		archive = zipfile.ZipFile(pack_location, 'r')

		packinfo = {
			"id": pack_location.split("/")[-1],
			"location": pack_location,
			"mcmeta": json.loads(archive.read("pack.mcmeta")),
			"name": "Unknown pack"
		}

		if "id" in packinfo["mcmeta"]["pack"]:
			packinfo["name"] = packinfo["mcmeta"]["pack"]["id"].capitalize()
		elif "name" in packinfo["mcmeta"]["pack"]:
			packinfo["name"] = packinfo["mcmeta"]["pack"]["name"].capitalize()
		else:
			packinfo["name"] = packinfo["id"]

		print(f"Importing {packinfo["name"]}")

		# evil version:
		#biomes = (["/".join(path.split("/")[len(path.split("/"))-(path.split("/")[::-1]).index("data"):]).replace("/worldgen/biome/", ":").removesuffix(".json") for path in archive.namelist() if ".json" in path and "/biome/" in path and not "/tags/" in path])

		contents = archive.namelist(); biomes = list()
		for path in contents:
			if ".json" in path and "/biome/" in path and not "/tags/" in path:
				split_path = path.split("/")
				i = len(split_path) - (split_path[::-1]).index("data")
				biomes.append("/".join(split_path[i:]).replace("/worldgen/biome/", ":").removesuffix(".json"))

		biomes = list(set(biomes)); biomes.sort(); packinfo["biomes"] = biomes
		self.packs.append(packinfo)

		self.update_biome_list()

		archive.close()

		return packinfo["id"]


	def get_pack_info(self, packID: str) -> dict:
		i = -1
		for fpack in self.packs:
			if packID == fpack["id"] or packID == fpack["name"]:
				i = self.packs.index(fpack)
		return self.packs[i]


	def list_all_biomes(self) -> list:
		biomes = list()
		for pack in self.packs:
			for biome in pack["biomes"]:
				biomes.append(biome)
		biomes = list(set(biomes)); biomes.sort()
		return biomes


	def get_biome_info(self, biomeID: str) -> dict:
		return self.biome_list[biomeID]


	def get_packs_with_biome(self, biomeID: str) -> list:
		return self.biome_list[biomeID]["packs"]


	def get_biome_preference(self, biomeID: str) -> str:
		return self.biome_list[biomeID]["preference"]


	def update_biome_list(self):
		biomeIDs = self.list_all_biomes()

		for biome in biomeIDs:
			# First, find out what packs have this biome!!
			packs_with_biome = list()
			for pack in self.packs:
				if biome in pack["biomes"]:
					packs_with_biome.append(pack["id"])

			# Set the preference - pack higher in the list (lower index) will take priority
			preference = packs_with_biome[0]

			# Either override or recreate the settings for this biome
			if not biome in self.biome_list:
				self.biome_list[biome] = {
						"id": biome,
						"packs": packs_with_biome,
						"preference": preference,
						"changed": False
					}
			else:
				if not self.biome_list[biome]["changed"]:
					self.biome_list[biome]["packs"] = packs_with_biome
					self.biome_list[biome]["preference"] = preference
				else:
					self.biome_list[biome]["packs"] = packs_with_biome

			#print(f"{biome}\n{packs_with_biome}\n{preference}")
		print(f"Updated biome list. Current amount of biomes: {len(self.biome_list)}")


	def set_biome_preference(self, biomeID: str, packID: str) -> bool:
		if packID != self.biome_list[biomeID]["preference"]:

			if packID in self.biome_list[biomeID]["packs"]:
				self.biome_list[biomeID]["preference"] = packID
				self.biome_list[biomeID]["changed"] = True
				return True

			elif packID is None:
				self.biome_list[biomeID]["preference"] = None
				self.biome_list[biomeID]["changed"] = True
				return True

		return False


	def move_pack_up(self, packID: str):
		i = -1
		for fpack in self.packs:
			if packID == fpack["id"] or packID == fpack["name"]:
				i = self.packs.index(fpack)

		if i != -1 and i != 0:
			item = self.packs.pop(i)
			self.packs.insert(i-1, item)
			print("Moved.")
			self.update_biome_list()


	def remove_pack(self, packID: str):
		i = -1
		for fpack in self.packs:
			if packID == fpack["id"] or packID == fpack["name"]:
				i = self.packs.index(fpack)

		if i != -1:
			self.packs.pop(i)
			self.update_biome_list()
			print(f"Removed {packID}")


	def export_datapacks(self) -> list | None:
		changes = str()

		# First, check what biomes were modified
		biomes = self.list_all_biomes(); modified_biomes = list()
		for biome in biomes:
			info = self.get_biome_info(biome)
			if info["changed"]:
				modified_biomes.append(biome)

		# Second, do magic
		if len(modified_biomes) == 0:
			return None

		else:
			for pack in self.packs:
				packID = pack["id"]
				archive = zipfile.ZipFile(pack["location"], 'r')
				extract_path = pack["location"].removesuffix(".zip").removesuffix(".jar").removesuffix(".ZIP").removesuffix(".JAR") + ".modified"
				archive.extractall(extract_path)
				archive.close()
				file_list = [x for x in archive.namelist() if ".json" in x.lower()]
				for biome in modified_biomes:
					if packID in self.get_packs_with_biome(biome):
						if packID != self.get_biome_preference(biome):
							changes += f"\t{biome} will be disabled from {packID}\n"
							biome_file_list = [x for x in file_list if (("biome/"+biome.split(":")[1]) in x) and ((biome.split(":")[0]) in x)]
							for biome_file in biome_file_list:
								os.rename(f"{extract_path}/{biome_file}", f"{extract_path}/{biome_file}.disabled")

				shutil.make_archive(extract_path, 'zip', extract_path)
				if ".jar" in pack["location"]:
					os.rename(f"{extract_path}.zip", f"{extract_path}.jar")
				shutil.rmtree(extract_path)

		print(f"List of changes to datapack(s):\n{changes}")
		return []
