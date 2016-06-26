import json
import os


script_path = os.path.dirname(os.path.realpath(__file__))
config_file_path = os.environ.get(
    'RESTRICCION_CONFIG',
    os.path.join(script_path, '..', 'configs/localhost.json')
)


with open(config_file_path, 'r') as config_file:
    CONFIG = json.load(config_file)
