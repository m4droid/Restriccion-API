from mock import patch
import moment

from .base_tests import BaseTestCase
from restriccion_scl.crawlers.uoct import UOCT_Crawler
from restriccion_scl.models.restriction import Restriction


class TestModelsRestriction(BaseTestCase):

    @patch('restriccion_scl.models.restriction.moment.utcnow')
    def test_models_device_get(self, mock_moment):
        mock_datetime = moment.date('2015-06-22', '%Y-%m-%d')
        mock_moment.side_effect = lambda: mock_datetime

        crawler = UOCT_Crawler()
        crawler.url = self.get_fixture_file_path('uoct.cl_restriccion-vehicular_0.html')
        Restriction.insert_many(self.mongo_db, crawler.parse())

        restrictions = Restriction.get(self.mongo_db)
        self.assertEqual(10, len(restrictions))
        self.assertEqual(
            {
                'fecha': '2015-06-21',
                'hash': '5e15b0168c9978cb5a50ad4c27c8065942d7fd30',
                'estado': 'Preemergencia Ambiental',
                'sin_sello_verde': '3-4-5-6-7-8',
                'con_sello_verde': '0-9',
                'actualizacion': mock_datetime.isoformat(),
                'fuente': 'http://www.uoct.cl/restriccion-vehicular/',
            },
            restrictions[0]
        )

    def test_models_device_get_limit(self):
        crawler = UOCT_Crawler()
        crawler.url = self.get_fixture_file_path('uoct.cl_restriccion-vehicular_0.html')
        Restriction.insert_many(self.mongo_db, crawler.parse())

        self.assertEqual(26, len(Restriction.get(self.mongo_db, limit=30)))

    @patch('restriccion_scl.models.restriction.moment.utcnow')
    def test_models_device_insert_many(self, mock_moment):
        mock_datetime = moment.date('2015-06-22', '%Y-%m-%d')
        mock_moment.side_effect = lambda: mock_datetime

        crawler = UOCT_Crawler()
        crawler.url = self.get_fixture_file_path('uoct.cl_restriccion-vehicular_0.html')

        new_restrictions = crawler.parse()

        Restriction.insert_many(self.mongo_db, new_restrictions)
            
        self.assertEqual(len(new_restrictions), self.mongo_db.restrictions.count())

        rows = self.mongo_db.restrictions.find({}, {'_id': 0})
        for i in range(len(new_restrictions)):
            new_restrictions[i]['actualizacion'] = mock_datetime.isoformat()
            self.assertEqual(new_restrictions[i], rows[i])

    @patch('restriccion_scl.models.restriction.moment.utcnow')
    def test_models_device_insert_many_keep_old_data(self, mock_moment):
        mock_datetime = moment.date('2015-06-22', '%Y-%m-%d')
        mock_moment.side_effect = lambda: mock_datetime

        crawler = UOCT_Crawler()
        crawler.url = self.get_fixture_file_path('uoct.cl_restriccion-vehicular_0.html')
        Restriction.insert_many(self.mongo_db, crawler.parse())
        self.assertEqual(26, self.mongo_db.restrictions.count())

        first_entries = []
        rows = self.mongo_db.restrictions.find({'$query': {}, '$orderby': {'fecha' : -1}}, {'_id': 0})
        for row in rows:
            first_entries.append(row)

        crawler.url = self.get_fixture_file_path('uoct.cl_restriccion-vehicular_1.html')
        new_restrictions = crawler.parse()
        Restriction.insert_many(self.mongo_db, new_restrictions)
        self.assertEqual(len(new_restrictions), self.mongo_db.restrictions.count())

        second_entries = []
        rows = self.mongo_db.restrictions.find({'$query': {}, '$orderby': {'fecha' : -1}}, {'_id': 0})
        for row in rows:
            second_entries.append(row)

        # Keep old data
        self.assertEqual(first_entries, second_entries[1:])
        self.assertEqual(
            {
                'fecha': '2015-06-22',
                'hash': '1abfb85af96da8080510d2c051a70edf5093da48',
                'estado': 'Emergencia Ambiental',
                'sin_sello_verde': '0-1-2-5-6-7-8-9',
                'con_sello_verde': '1-2-3-4',
                'actualizacion': mock_datetime.isoformat(),
                'fuente': 'http://www.uoct.cl/restriccion-vehicular/',
            },
            second_entries[0]
        )

    @patch('restriccion_scl.models.restriction.moment.utcnow')
    def test_models_device_insert_many_updated_data(self, mock_moment):
        # First data
        mock_moment.side_effect = lambda: moment.date('2015-06-22T00:00:00', '%Y-%m-%dT%H:%M:%S')
        crawler = UOCT_Crawler()
        crawler.url = self.get_fixture_file_path('uoct.cl_restriccion-vehicular_1.html')
        Restriction.insert_many(self.mongo_db, crawler.parse())

        first_entries = []
        rows = self.mongo_db.restrictions.find({'$query': {}, '$orderby': {'fecha' : -1}})
        for row in rows:
            first_entries.append(row)

        # Modified data
        mock_moment.side_effect = lambda: moment.date('2015-06-22T01:00:00', '%Y-%m-%dT%H:%M:%S')
        crawler = UOCT_Crawler()
        crawler.url = self.get_fixture_file_path('uoct.cl_restriccion-vehicular_2.html')
        Restriction.insert_many(self.mongo_db, crawler.parse())

        second_entries = []
        rows = self.mongo_db.restrictions.find({'$query': {}, '$orderby': {'fecha' : -1}})
        for row in rows:
            second_entries.append(row)

        # Keep old data
        self.assertEqual(first_entries[0], second_entries[0])
        self.assertEqual(first_entries[2:], second_entries[2:])

        # Check updated
        for key in ['_id', 'fecha', 'estado', 'sin_sello_verde', 'fuente']:
            self.assertEqual(first_entries[1][key], second_entries[1][key])

        for key in ['hash', 'con_sello_verde', 'actualizacion']:
            self.assertNotEqual(first_entries[1][key], second_entries[1][key])
