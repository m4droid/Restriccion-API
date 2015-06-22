from mock import patch
import moment

from base_tests import BaseTestCase
from restriccion_scl.crawlers.uoct import UOCT_Crawler


class TestApi(BaseTestCase):

    def test_parse_file(self):
        crawler = UOCT_Crawler()
        crawler.url = self.get_fixture_file_path('uoct.cl_restriccion-vehicular_0.html')

        self.assertEquals(0, self.mongo_db.restrictions.count())
        new_restrictions = crawler.parse()
        self.assertEquals(list, type(new_restrictions))
        self.assertEquals(26, len(new_restrictions))
        self.assertEquals(26, self.mongo_db.restrictions.count())

    @patch('restriccion_scl.crawlers.uoct.moment.now')
    def test_database_entry_data(self, mock_moment):
        mock_moment.side_effect = lambda: moment.date('2015-06-22', '%Y-%m-%d')
        from restriccion_scl.crawlers.uoct import UOCT_Crawler

        crawler = UOCT_Crawler()
        crawler.url = self.get_fixture_file_path('uoct.cl_restriccion-vehicular_0.html')
        crawler.parse()

        first_entry = self.mongo_db.restrictions.find_one({'$query': {}, '$orderby': {'fecha' : -1}}, {'_id': 0})

        self.assertEquals(
            {
                'fecha': '2015-06-21',
                'hash': '5e15b0168c9978cb5a50ad4c27c8065942d7fd30',
                'estado': 'Preemergencia Ambiental',
                'sin_sello_verde': '3-4-5-6-7-8',
                'con_sello_verde': '0-9',
                'actualizacion': '2015-06-22T00:00:00',
            },
            first_entry
        )

    @patch('restriccion_scl.crawlers.uoct.moment.now')
    def test_parse_new_entry(self, mock_moment):
        mock_moment.side_effect = lambda: moment.date('2015-06-22', '%Y-%m-%d')
        from restriccion_scl.crawlers.uoct import UOCT_Crawler

        crawler = UOCT_Crawler()
        crawler.url = self.get_fixture_file_path('uoct.cl_restriccion-vehicular_0.html')
        crawler.parse()

        first_entries = []
        second_entries = []
        rows = self.mongo_db.restrictions.find({'$query': {}, '$orderby': {'fecha' : -1}})

        for row in rows:
            first_entries.append(row)

        crawler.url = self.get_fixture_file_path('uoct.cl_restriccion-vehicular_1.html')
        new_restrictions = crawler.parse()

        self.assertEquals(1, len(new_restrictions))

        rows = self.mongo_db.restrictions.find({'$query': {}, '$orderby': {'fecha' : -1}})
        for row in rows:
            second_entries.append(row)

        # Keep old data
        self.assertEquals(first_entries, second_entries[1:])

        new_document = second_entries[0]
        del new_document['_id']

        self.assertEquals(
            {
                'fecha': '2015-06-22',
                'hash': '1abfb85af96da8080510d2c051a70edf5093da48',
                'estado': 'Emergencia Ambiental',
                'sin_sello_verde': '0-1-2-5-6-7-8-9',
                'con_sello_verde': '1-2-3-4',
                'actualizacion': '2015-06-22T00:00:00',
            },
            new_document
        )

    @patch('restriccion_scl.crawlers.uoct.moment.now')
    def test_parse_update_entry(self, mock_moment):
        mock_moment.side_effect = lambda: moment.date('2015-06-22T00:00:00', '%Y-%m-%dT%H:%M:%S')
        from restriccion_scl.crawlers.uoct import UOCT_Crawler

        first_entries = []
        second_entries = []

        crawler = UOCT_Crawler()
        crawler.url = self.get_fixture_file_path('uoct.cl_restriccion-vehicular_1.html')
        crawler.parse()

        rows = self.mongo_db.restrictions.find({'$query': {}, '$orderby': {'fecha' : -1}})
        for row in rows:
            first_entries.append(row)

        mock_moment.side_effect = lambda: moment.date('2015-06-22T01:00:00', '%Y-%m-%dT%H:%M:%S')
        from restriccion_scl.crawlers.uoct import UOCT_Crawler

        crawler = UOCT_Crawler()
        crawler.url = self.get_fixture_file_path('uoct.cl_restriccion-vehicular_2.html')
        new_restrictions = crawler.parse()

        self.assertEquals(0, len(new_restrictions))

        rows = self.mongo_db.restrictions.find({'$query': {}, '$orderby': {'fecha' : -1}})
        for row in rows:
            second_entries.append(row)

        # Keep old data
        self.assertEquals(first_entries[0], second_entries[0])
        self.assertEquals(first_entries[2:], second_entries[2:])

        self.assertEquals(first_entries[1]['_id'], second_entries[1]['_id'])
        self.assertEquals(first_entries[1]['fecha'], second_entries[1]['fecha'])
        self.assertEquals(first_entries[1]['estado'], second_entries[1]['estado'])
        self.assertEquals(first_entries[1]['sin_sello_verde'], second_entries[1]['sin_sello_verde'])

        self.assertNotEquals(first_entries[1]['hash'], second_entries[1]['hash'])
        self.assertNotEquals(first_entries[1]['con_sello_verde'], second_entries[1]['con_sello_verde'])
        self.assertNotEquals(first_entries[1]['actualizacion'], second_entries[1]['actualizacion'])
