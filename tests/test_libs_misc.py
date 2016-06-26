from .base_tests import BaseTestCase
from restriccion.libs.misc import list_chunks_generator


class TestLibsMisc(BaseTestCase):

    def test_libs_misc_list_chunks_empty_params(self):
        self.assertEqual([], list(list_chunks_generator([], 0)))
        self.assertEqual([], list(list_chunks_generator([], 1)))
        self.assertEqual([], list(list_chunks_generator([], 2)))

    def test_libs_misc_list_chunks_ok(self):
        list_ = [0, 1, 2]

        self.assertEqual([list_], list(list_chunks_generator(list_, 0)))
        self.assertEqual([[0], [1], [2]], list(list_chunks_generator(list_, 1)))
        self.assertEqual([[0, 1], [2]], list(list_chunks_generator(list_, 2)))
