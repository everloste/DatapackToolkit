from src.modules.Managers.DatapackManager import DatapackManager
import src.modules.Log as Log
import json, math


class ValueType:
	class Int:
		pass
	class Float:
		pass
	class Percent:
		pass

class OptionType:
	class Title:
		pass
	class ValueEdit:
		pass


class CustomConfigManager:

	def __init__(self, dpmanager):
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
					self.log.printInfo(f"Loaded dpconfig from archive for '{pack}'")

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
			self.log.print(f"Writing changes made using dpconfig to '{datapack.name}'...")

			# Load working objects
			config = self.handlers[datapack.name]
			pack_files: list[str] = datapack.archive.namelist()

			# Iterate through methods in config
			for method_name in config.methods:

				# Load method object
				method: ConfigMethod = config.methods[method_name]

				# Skip if no input
				if method.input is None:
					self.log.print(f"Ignoring method '{method_name}' (input is null)")
					continue

				# Load input
				value = method.input

				# Apply transformer to value IF it has one
				if hasattr(method, "transformer"):
					try:
						value = method.readTransformerArgument(method.transformer)
					except:
						self.log.print(f"Failed to use transformer of method '{method_name}', aborted writing")
						continue
				else:
					self.log.printInfo(f"Method '{method_name}' has no transformer, ignoring")

				# Iterate through accessors to write transformed value to JSONs
				for ai, accessor in enumerate(method.accessors):
					# Create a list of all files we need to modify
					modifiable_files: list = accessor["file_path"] if isinstance(accessor["file_path"], list) else [accessor["file_path"]]
					exact_file_paths = [x[2:] for x in modifiable_files if x[:2] == "./"]

					# Now let's go throught every file in the archive
					matched_files = list()
					for file in pack_files:

						# If it matches
						if file.endswith(tuple(modifiable_files)) or (file.startswith(tuple(exact_file_paths)) and file.endswith(tuple(exact_file_paths))):
							matched_files.append(file)

							keys = accessor["value_path"].split("/")
							struct = json.loads(datapack.archive.read(file))
							inval = value

							deep_struct = struct
							for key in keys[:-1]:
								if key.isdigit():
									key = int(key)
								deep_struct = deep_struct[key]
							last_key = keys[-1]
							if last_key.isdigit():
								last_key = int(last_key)

							outval = None
							if "method" not in accessor:
								self.log.print(f"No write method in accessor {ai} for method '{method_name}'")
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
											self.log.print(f"Warn: Tried to use the REMOVE write method on a non-list object:\n\tValue: {inval}\n\tTo key: {last_key}\n\tUsing write method: {write_method}\n\tIn file: {file}")

									elif write_method == "pop":
										if isinstance(deep_struct[last_key], list):
											outval = deep_struct[last_key].copy()
											outval.pop(int(inval))
										else:
											self.log.print(f"Warn: Tried to use the POP write method on a non-list object:\n\tValue: {inval}\n\tTo key: {last_key}\n\tUsing write method: {write_method}\n\tIn file: {file}")

									else:
										outval = inval

								except:
									self.log.print(f"Accessor {ai} for method '{method_name}' failed to use its write method:\n\tValue: {inval}\n\tTo key: {last_key}\n\tUsing write method: {write_method}\n\tIn file: {file}")
									continue

							if outval is not None:
								deep_struct[last_key] = outval
								self.log.printInfo(f"Accessor {ai} for method '{method_name}' successful")
							else:
								self.log.print(f"Accessor {ai} for method '{method_name}' failed to write value (final value is None)\n\tValue: {inval}\n\tTo key: {last_key}\n\tIn file: {file}")
								continue

							datapack.rewrite_file(file, json.dumps(struct))

					if len(matched_files) == 0:
						self.log.print(f"Accessor {ai} for method '{method_name}' failed to write - no files matching file path {modifiable_files} or {exact_file_paths}")
					matched_files.clear()


class Config:
	def __init__(self, datapackID: str, file: str | dict):
		self.datapackID = datapackID

		self.JSON = dict()
		if isinstance(file, dict):
			self.JSON = file.copy()
		elif isinstance(file, str):
			self.JSON = json.loads(file)

		self.tabName = self.JSON["config"]["meta"]["tab"]

		self.widgets = list()
		for entry in self.JSON["config"]["widgets"]:
			self.widgets.append(entry)

		self.methods = dict()
		for entry in self.JSON["config"]["methods"]:
			self.methods[entry] = ConfigMethod(self.JSON["config"]["methods"][entry])

	def getWidgets(self) -> list[dict]:
		return self.widgets

	def inputToMethod(self, method: str, value):
		self.methods[method].input = value


class ConfigMethod:
	input: None
	def __init__(self, data: dict):
		self.STRUCT = data
		self.input = None

		if "accessors" in self.STRUCT:
			self.accessors = self.STRUCT["accessors"]

		if "transformer" in self.STRUCT:
			self.transformer = self.STRUCT["transformer"]

	def readTransformerArgument(self, argument: str | dict | int | float):
		if isinstance(argument, str):
			if argument == "input":
				return self.input
			else:
				return argument

		elif isinstance(argument, int) or isinstance(argument, float):
			return argument

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

				elif argument["function"] == "square":
					return pow(self.readTransformerArgument(argument["argument"]), 2)

				elif argument["function"] == "square_root":
					return math.sqrt(self.readTransformerArgument(argument["argument"]))

				if argument["function"] == "add":
					return self.readTransformerArgument(argument["argument"]) + self.readTransformerArgument(argument["argument1"])

		else:
			return None