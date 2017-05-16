import json
import os
import sys


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _get_config_path(filename):
    if filename is None:
        return None

    config_paths = [
        os.path.join(BASE_DIR, 'configs'),
        os.path.join(os.path.expanduser('~'), 'configs'),
    ]
    for config_path in config_paths:
        p = os.path.join(config_path, filename)
        if os.path.exists(p):
            return p
    return None


def load_env_params():
    env = os.environ.get('ENV')

    config_path = _get_config_path('env_{0:s}.json'.format(env))

    if config_path is None:
        raise Exception('ERROR: {0:s} environment config file not found'.format(env), file=sys.stderr)

    with open(config_path) as f:
        data = json.load(f)

    return data
