from src.modules.Managers.DatapackManager import DatapackManager
import src.modules.Log as Log
import json, math

class ConfigManager:

	def __init__(self, dpmanager: DatapackManager):
		self.manager = dpmanager
		self.manager.add_child_manager(self)

		self.packs = set()
		self.handlers = dict()

		self.log = Log.Writer()

	def __update__(self):
		pack_list = self.manager.get_pack_list()

		for pack in pack_list:
			if "dpconfig" in self.manager.get_pack_modules(pack):
				if pack not in self.packs:
					self.packs.add(pack)
					self.handlers[pack] = Config(pack, self.manager.get_pack_config(pack))
					self.log.printInfo(f"[CONFIG] Detected and loaded config for '{pack}'")

		removals = set()
		for pack in self.packs:
			if pack not in pack_list:
				removals.add(pack)
				del self.handlers[pack]

		for pack in removals:
			self.packs.remove(pack)

	def get_packs(self):
		return self.packs

	def get_pack_config(self, pack: str):
		return self.handlers[pack]

	def apply_changes_to_pack(self, datapack: DatapackManager.Datapack):

		# Don't do anything if datapack doesn't have a config
		if datapack.name not in self.packs:
			return None

		else:
			self.log.printInfo(f"[CONFIG] Writing changes made using config to '{datapack.name}'...")

			# Load working objects
			config = self.handlers[datapack.name]
			pack_files: list[str] = datapack.archive.namelist()

			already_edited_files = dict()

			# Iterate through methods in config
			for method_name in config.methods:

				# Load method object
				method: ConfigMethod = config.methods[method_name]

				# Skip this method if no input
				if method.input is None:
					self.log.printInfo(f"[CONFIG] Ignoring method '{method_name}' (input is null)")
					continue

				# Load input
				value = method.input

				# Apply transformer to input IF it has one
				if hasattr(method, "transformer"):
					try:
						value = method.readTransformerArgument(method.transformer)
					except:
						self.log.printError(f"[CONFIG] Failed to use transformer of method '{method_name}', aborted writing")
						continue
				else:
					self.log.printInfo(f"[CONFIG] Method '{method_name}' has no method-wide transformer")

				# Iterate through accessors to write transformed value to JSONs
				for ai, accessor in enumerate(method.accessors):

					# Create a list of all files we need to modify
					modifiable_files: list = accessor["file_path"] if isinstance(accessor["file_path"], list) else [accessor["file_path"]]
					exact_file_paths = [x[2:] for x in modifiable_files if x[:2] == "./"]

					# Transform value if accessor has transformer
					inval = value
					if "transformer" in accessor:
						inval = method.readTransformerArgument(accessor["transformer"])
						self.log.printInfo(f"[CONFIG] Accessor {ai} for method '{method_name}' has own transformer value")

					# Now let's go through every file in the archive
					matched_files = list()
					for file in pack_files:

						# If it matches
						if file.endswith(tuple(modifiable_files)) or (file.startswith(tuple(exact_file_paths)) and file.endswith(tuple(exact_file_paths))):
							matched_files.append(file)

							# Create key path
							keys = accessor["value_path"].split("/")

							# Load JSON file
							if file not in already_edited_files:
								already_edited_files[file] = json.loads(datapack.archive.read(file)).copy()
							struct = already_edited_files[file]

							# Navigate JSON using the key path
							deep_struct = struct
							for key in keys[:-1]:
								if key.isdigit():
									key = int(key)
								deep_struct = deep_struct[key]
							last_key = keys[-1]
							if last_key.isdigit():
								last_key = int(last_key)

							# Now write it using the write method
							outval = None
							if "method" not in accessor:
								self.log.printError(f"[CONFIG] No write method in accessor {ai} for method '{method_name}'")
								continue
							else:
								write_method = accessor["method"]

								try:
									if write_method == "multiply":
										outval = deep_struct[last_key] * inval

									elif write_method == "multiply_int":
										outval = int(deep_struct[last_key] * inval)

									elif write_method == "divide":
										outval = deep_struct[last_key] / inval

									elif write_method == "divide_int":
										outval = int(deep_struct[last_key] // inval)

									elif write_method == "add":
										outval = deep_struct[last_key] + inval

									elif write_method == "add_int":
										outval = int(deep_struct[last_key] + inval)

									elif write_method == "subtract":
										outval = deep_struct[last_key] - inval

									elif write_method == "subtract_int":
										outval = int(deep_struct[last_key] - inval)

									elif write_method == "remove":
										if isinstance(deep_struct[last_key], list):
											outval = deep_struct[last_key].copy()
											outval.remove(inval)
										else:
											self.log.printError(f"[CONFIG] Tried to use the REMOVE write method on a non-list object:\n\tValue: {inval}\n\tTo key: {last_key}\n\tUsing write method: {write_method}\n\tIn file: {file}")

									elif write_method == "pop":
										if isinstance(deep_struct[last_key], list):
											outval = deep_struct[last_key].copy()
											outval.pop(int(inval))
										else:
											self.log.printError(f"[CONFIG] Tried to use the POP write method on a non-list object:\n\tValue: {inval}\n\tTo key: {last_key}\n\tUsing write method: {write_method}\n\tIn file: {file}")

									else:
										outval = inval

								except:
									self.log.printError(f"[CONFIG] Accessor {ai} for method '{method_name}' failed to use its write method:\n\tValue: {inval}\n\tTo key: {last_key}\n\tUsing write method: {write_method}\n\tIn file: {file}")
									continue

							if outval is not None:
								deep_struct[last_key] = outval
								self.log.printInfo(f"[CONFIG] Accessor {ai} for method '{method_name}' successful")
							else:
								self.log.printError(f"[CONFIG] Accessor {ai} for method '{method_name}' failed to write value (final value is None)\n\tValue: {inval}\n\tTo key: {last_key}\n\tIn file: {file}")
								continue

					if len(matched_files) == 0:
						self.log.printError(f"[CONFIG] Accessor {ai} for method '{method_name}' failed to write - no files matching file path {modifiable_files} or {exact_file_paths}")
					matched_files.clear()

			for file in already_edited_files:
				self.log.printInfo(f"[CONFIG] Overwriting file {file}")
				datapack.rewrite_file(f"./{file}", json.dumps(already_edited_files[file]))


class Config:
	datapackID: str

	def __init__(self, datapackID: str, file: str | dict):
		self.datapackID = datapackID
		self.jsonObject = dict()

		if isinstance(file, dict):
			self.jsonObject = file.copy()
		elif isinstance(file, str):
			self.jsonObject = json.loads(file)

		self.tabName = self.jsonObject["config"]["meta"]["tab"]

		self.widgets = list()
		for entry in self.jsonObject["config"]["widgets"]:
			self.widgets.append(entry)

		self.methods = dict()
		for entry in self.jsonObject["config"]["methods"]:
			self.methods[entry] = ConfigMethod(self.jsonObject["config"]["methods"][entry], self)

		self.slots = dict()
		if "slots" in self.jsonObject["config"]:
			for entry in self.jsonObject["config"]["slots"]:
				self.slots[entry] = self.jsonObject["config"]["slots"][entry]

	def getWidgets(self) -> list[dict]:
		return self.widgets

	def inputToMethod(self, method: str, value):
		self.methods[method].input = value

	def inputToSlot(self, slots: str | list, value):
		if isinstance(slots, str):
			self.slots[slots] = value
		elif isinstance(slots, list):
			for slot in slots:
				self.slots[slot] = value


class ConfigMethod:
	input = None

	def __init__(self, data: dict, master: Config):
		self.jsonObject = data
		self.masterConfig = master
		self.input = None

		if "accessors" in self.jsonObject:
			self.accessors = self.jsonObject["accessors"]

		if "transformer" in self.jsonObject:
			self.transformer = self.jsonObject["transformer"]

	def readTransformerArgument(self, argument: str | dict | int | float | None):

		# Argument is a string...
		if isinstance(argument, str):
			if argument[0] == "$":
				if argument == "$input" or argument == "$in":
					return self.input
				else:
					try:
						return self.readTransformerArgument(self.masterConfig.slots[argument[1:]])
					except KeyError:
						return None

			elif argument == "input":
				return self.input
			else:
				return argument

		# Argument is a number...
		elif isinstance(argument, int) or isinstance(argument, float):
			return argument

		# Argument is an object (function)
		elif isinstance(argument, dict):
			if not "function" in argument:
				return None

			else:
				if argument["function"] == "if_else":
					arg1 = self.readTransformerArgument(argument["argument"])
					arg2 = self.readTransformerArgument(argument["argument1"])

					if argument["operator"] == ">":
						if arg1 > arg2:
							return self.readTransformerArgument(argument["true"])
						else:
							return self.readTransformerArgument(argument["false"])

					elif argument["operator"] == "==":
						if arg1 == arg2:
							return self.readTransformerArgument(argument["true"])
						else:
							return self.readTransformerArgument(argument["false"])

					elif argument["operator"] == ">=":
						if arg1 >= arg2:
							return self.readTransformerArgument(argument["true"])
						else:
							return self.readTransformerArgument(argument["false"])

					else:
						return self.readTransformerArgument(argument["false"])

				elif argument["function"] == "int":
					return int(round(self.readTransformerArgument(argument["argument"])))

				elif argument["function"] == "multiply":
					return self.readTransformerArgument(argument["argument"]) * self.readTransformerArgument(argument["argument1"])

				elif argument["function"] == "divide":
					return self.readTransformerArgument(argument["argument"]) / self.readTransformerArgument(argument["argument1"])

				elif argument["function"] == "modulo":
					return self.readTransformerArgument(argument["argument"]) % self.readTransformerArgument(argument["argument1"])

				elif argument["function"] == "square":
					return pow(self.readTransformerArgument(argument["argument"]), 2)

				elif argument["function"] == "square_root":
					return math.sqrt(self.readTransformerArgument(argument["argument"]))

				elif argument["function"] == "add":
					return self.readTransformerArgument(argument["argument"]) + self.readTransformerArgument(argument["argument1"])

				else:
					return None

		else:
			return None