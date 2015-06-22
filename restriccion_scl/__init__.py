import json
import os


script_path = os.path.dirname(os.path.realpath(__file__))
config_file_path = os.environ.get(
    'RESTRICCION_SCL_CONFIG',
    os.path.join(script_path, '..', 'configs/localhost.json')
)

config_file = open(config_file_path, 'r')
CONFIG = json.load(config_file)
config_file.close()
