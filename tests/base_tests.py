import os
import unittest

import pymongo
from restriccion_scl import CONFIG
from restriccion_scl.wsgi import app


class BaseTestCase(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(BaseTestCase, self).__init__(*args, **kwargs)
        
        self.script_path = os.path.dirname(os.path.realpath(__file__))

        self.mongo_client = pymongo.MongoClient(**CONFIG['pymongo']['client'])
        self.mongo_db = self.mongo_client[CONFIG['pymongo']['database']]

    def tearDown(self):
        self.mongo_db.restrictions.drop()
        self.mongo_db.devices.drop()

        self.mongo_client.close()

    def get_fixture_file_path(self, fixture):
        return 'file://'+ os.path.join(self.script_path, 'fixtures', fixture)


class ApiBaseTestCase(BaseTestCase):

    def setUp(self):
        super(ApiBaseTestCase, self).setUp()

        app.config['TESTING'] = True
        app.config['DEBUG'] = True
        self.app = app.test_client()
