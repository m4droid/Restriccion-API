from .base_tests import BaseTestCase

from restriccion.libs.env import _get_config_path, load_env_params


class TestLibsEnv(BaseTestCase):

    def test_libs_env__get_config_path_none_value(self):
        self.assertIsNone(_get_config_path(None))

    def test_libs_env__get_config_path_wrong_value(self):
        self.assertIsNone(_get_config_path('fake_file'))

    def test_libs_env_load_env_params_wrong_value(self):
        self.assertRaises(Exception, load_env_params, ('fake_file',))
