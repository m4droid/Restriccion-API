import os
import unittest

import pymongo

from restriccion import CONFIG
from restriccion.wsgi import app


class BaseTestCase(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(BaseTestCase, self).__init__(*args, **kwargs)

        self.script_path = os.path.dirname(os.path.realpath(__file__))

        self.mongo_client = pymongo.MongoClient(**CONFIG['pymongo']['client'])
        self.mongo_db = self.mongo_client[CONFIG['pymongo']['database']]

    def tearDown(self):
        collections = [
            'reports_restriction',
            'reports_air_quality',
            'devices'
        ]
        for collection in collections:
            self.mongo_db[collection].drop()

        self.mongo_client.close()

    def get_fixture_file_path(self, fixture):
        return 'file://' + os.path.join(self.script_path, 'fixtures', fixture)


class ApiBaseTestCase(BaseTestCase):

    def setUp(self):
        super(ApiBaseTestCase, self).setUp()

        app.config['TESTING'] = True
        app.config['DEBUG'] = True
        self.app = app.test_client()
