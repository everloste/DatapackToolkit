import os

class META:
	app_name = "Datapack Toolkit"
	app_version = "0.25.4.19"
	default_theme = "fusion"
	debug_mode = True
	root = "/".join(os.path.dirname(os.path.realpath(__file__)).split("\\")[:-1])
	export_log = 1