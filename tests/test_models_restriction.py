from mock import patch
import moment

from .base_tests import BaseTestCase
from restriccion.crawlers.uoct import UOCT_Crawler
from restriccion.models.restriction import Restriction


class TestModelsRestriction(BaseTestCase):

    @patch('restriccion.models.base_report.moment.utcnow')
    def test_models_restriction_get(self, mock_moment):
        mock_datetime = moment.utc('2015-06-21', '%Y-%m-%d')
        mock_moment.side_effect = lambda: mock_datetime

        crawler = UOCT_Crawler()
        crawler.url = self.get_fixture_file_path('uoct.cl_restriccion-vehicular_0.html')
        Restriction.insert_many(self.mongo_db, crawler.parse()['restrictions'])

        restrictions = Restriction.get(self.mongo_db)
        self.assertEqual(10, len(restrictions))
        self.assertEqual(
            {
                'ciudad': 'Santiago',
                'fecha': '2015-06-21',
                'hash': 'ed55bf3ea8e18f328eb03471874be28e5779424b',
                'sin_sello_verde': ['3', '4', '5', '6', '7', '8'],
                'con_sello_verde': ['0', '9'],
                'actualizacion': mock_datetime.isoformat(),
                'fuente': 'http://www.uoct.cl/restriccion-vehicular/',
            },
            restrictions[0]
        )

    @patch('restriccion.models.base_report.moment.utcnow')
    def test_models_restriction_get_limit(self, mock_moment):
        mock_moment.side_effect = lambda: moment.utc('2015-06-21', '%Y-%m-%d')

        crawler = UOCT_Crawler()
        crawler.url = self.get_fixture_file_path('uoct.cl_restriccion-vehicular_0.html')
        Restriction.insert_many(self.mongo_db, crawler.parse()['restrictions'])

        self.assertEqual(26, len(Restriction.get(self.mongo_db, limit=30)))

    @patch('restriccion.models.base_report.moment.utcnow')
    def test_models_restriction_insert_many(self, mock_moment):
        mock_datetime = moment.utc('2015-06-22', '%Y-%m-%d')
        mock_moment.side_effect = lambda: mock_datetime

        crawler = UOCT_Crawler()
        crawler.url = self.get_fixture_file_path('uoct.cl_restriccion-vehicular_0.html')

        new_restrictions = crawler.parse()['restrictions']

        Restriction.insert_many(self.mongo_db, new_restrictions)

        self.assertEqual(len(new_restrictions), self.mongo_db[Restriction.get_mongo_collection()].count())

        rows = self.mongo_db[Restriction.get_mongo_collection()].find({}, {'_id': 0})
        for i in range(len(new_restrictions)):
            new_restrictions[i]['actualizacion'] = mock_datetime.isoformat()
            self.assertEqual(new_restrictions[i], rows[i])

    @patch('restriccion.models.base_report.moment.utcnow')
    def test_models_restriction_insert_many_keep_old_data(self, mock_moment):
        mock_moment.side_effect = lambda: moment.utc('2015-06-21', '%Y-%m-%d')

        crawler = UOCT_Crawler()
        crawler.url = self.get_fixture_file_path('uoct.cl_restriccion-vehicular_0.html')
        Restriction.insert_many(self.mongo_db, crawler.parse()['restrictions'])
        self.assertEqual(26, self.mongo_db[Restriction.get_mongo_collection()].count())

        first_entries = []
        rows = self.mongo_db[Restriction.get_mongo_collection()].find(
            {'$query': {}, '$orderby': {'fecha': -1}}, {'_id': 0}
        )
        for row in rows:
            first_entries.append(row)

        mock_datetime = moment.utc('2015-06-22', '%Y-%m-%d')
        mock_moment.side_effect = lambda: mock_datetime

        crawler.url = self.get_fixture_file_path('uoct.cl_restriccion-vehicular_1.html')
        new_restrictions = crawler.parse()['restrictions']
        Restriction.insert_many(self.mongo_db, new_restrictions)
        self.assertEqual(len(new_restrictions), self.mongo_db[Restriction.get_mongo_collection()].count())

        second_entries = []
        rows = self.mongo_db[Restriction.get_mongo_collection()].find(
            {'$query': {}, '$orderby': {'fecha': -1}}, {'_id': 0}
        )
        for row in rows:
            second_entries.append(row)

        # Keep old data
        self.assertEqual(first_entries, second_entries[1:])
        self.assertEqual(
            {
                'ciudad': 'Santiago',
                'fecha': '2015-06-22',
                'hash': '4550713861c4b74e957963c03195202980f4b831',
                'sin_sello_verde': ['0', '1', '2', '5', '6', '7', '8', '9'],
                'con_sello_verde': ['1', '2', '3', '4'],
                'actualizacion': mock_datetime.isoformat(),
                'fuente': 'http://www.uoct.cl/restriccion-vehicular/',
            },
            second_entries[0]
        )

    @patch('restriccion.models.base_report.moment.utcnow')
    def test_models_restriction_insert_many_updated_data(self, mock_moment):
        # First data
        mock_moment.side_effect = lambda: moment.utc('2015-06-22T00:00:00', '%Y-%m-%dT%H:%M:%S')

        crawler = UOCT_Crawler()
        crawler.url = self.get_fixture_file_path('uoct.cl_restriccion-vehicular_1.html')
        Restriction.insert_many(self.mongo_db, crawler.parse()['restrictions'])

        first_entries = []
        rows = self.mongo_db[Restriction.get_mongo_collection()].find({'$query': {}, '$orderby': {'fecha': -1}})
        for row in rows:
            first_entries.append(row)

        # Modified data
        mock_moment.side_effect = lambda: moment.utc('2015-06-22T01:00:00', '%Y-%m-%dT%H:%M:%S')
        crawler = UOCT_Crawler()
        crawler.url = self.get_fixture_file_path('uoct.cl_restriccion-vehicular_2.html')
        Restriction.insert_many(self.mongo_db, crawler.parse()['restrictions'])

        second_entries = []
        rows = self.mongo_db[Restriction.get_mongo_collection()].find({'$query': {}, '$orderby': {'fecha': -1}})
        for row in rows:
            second_entries.append(row)

        # Keep old data
        self.assertEqual(first_entries[0], second_entries[0])
        self.assertEqual(first_entries[2:], second_entries[2:])

        # Check updated
        for key in ['_id', 'fecha', 'sin_sello_verde', 'fuente', 'ciudad']:
            self.assertEqual(first_entries[1][key], second_entries[1][key])

        for key in ['hash', 'con_sello_verde', 'actualizacion']:
            self.assertNotEqual(first_entries[1][key], second_entries[1][key])
