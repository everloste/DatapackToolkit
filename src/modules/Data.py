from src.modules.Managers.DatapackManager import DatapackManager
from src.modules.Managers.StructureSpacer import StructureSpacer
from src.modules.Managers.BiomeBlenderNew import BiomeBlender
from src.modules.Managers.DPConfigHandler import CustomConfigManager


class DataHandler:
	_instance = None

	def __new__(cls, *args, **kwargs):
		print("Data handler accessed... (This call should be seen as infrequently as possible!)")
		if not cls._instance:
			cls._instance = super().__new__(cls)
		return cls._instance

	def __init__(self):
		if not hasattr(self, '_initialized'):
			print("Initializing data handling...")
			self._initialized = True

			print("\tInitializing the datapack manager...")
			self.dataPacks = DatapackManager()
			print("\tInitializing other modules...")
			self.structureSets = StructureSpacer(self.dataPacks)
			self.biomeProviders = BiomeBlender(self.dataPacks)
			self.customConfigs = CustomConfigManager(self.dataPacks)
