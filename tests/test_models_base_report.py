from .base_tests import BaseTestCase

from restriccion.models.base_report import BaseReport


class TestModelsRestriction(BaseTestCase):

    @classmethod
    def setUpClass(cls):
        super(TestModelsRestriction, cls).setUpClass()
        cls.base_report = BaseReport()

    def test_get_mongo_collection_not_implemented(self):
        self.assertRaises(NotImplementedError, self.base_report.get_mongo_collection)

    def test_get_fields_not_implemented(self):
        self.assertRaises(NotImplementedError, self.base_report.get_fields)

    def test_get_unique_fields_not_implemented(self):
        self.assertRaises(NotImplementedError, self.base_report.get_unique_fields)
