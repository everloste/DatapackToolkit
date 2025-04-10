from src.modules.DatapackManager import DatapackManager
from src.modules.StructureSpacer import StructureSpacer
from src.modules.BiomeBlenderNew import BiomeBlender

datapacks = DatapackManager()
structure_sets = StructureSpacer(datapacks)
biomes = BiomeBlender(datapacks)