import json

from mock import patch
import moment

from .base_tests import ApiBaseTestCase
from restriccion_scl.crawlers.uoct import UOCT_Crawler


class TestApiRestrictions(ApiBaseTestCase):

    def test_restrictions_get_empty_entries(self):
        response = self.app.get('/0/restricciones')

        self.assertEqual('application/json', response.mimetype)
        self.assertEqual(200, response.status_code)
        self.assertEqual('[]', response.data.decode())

    @patch('restriccion_scl.crawlers.uoct.moment.now')
    def test_restrictions_get_all_entries(self, mock_moment):
        mock_moment.side_effect = lambda: moment.date('2015-06-22', '%Y-%m-%d')


        crawler = UOCT_Crawler()
        crawler.url = self.get_fixture_file_path('uoct.cl_restriccion-vehicular_0.html')
        crawler.parse()

        response = self.app.get('/0/restricciones')
        self.assertEqual('application/json', response.mimetype)
        self.assertEqual(200, response.status_code)

        entries = json.loads(response.data.decode())

        self.assertEqual(26, len(entries))

    @patch('restriccion_scl.crawlers.uoct.moment.now')
    def test_restrictions_get_date_entry(self, mock_moment):
        mock_moment.side_effect = lambda: moment.date('2015-06-22', '%Y-%m-%d')

        crawler = UOCT_Crawler()
        crawler.url = self.get_fixture_file_path('uoct.cl_restriccion-vehicular_0.html')
        crawler.parse()

        response = self.app.get('/0/restricciones?fecha=2015-06-21')
        self.assertEqual('application/json', response.mimetype)
        self.assertEqual(200, response.status_code)

        entries = json.loads(response.data.decode())

        self.assertEqual(1, len(entries))

        self.assertEqual(
            {
                'fecha': '2015-06-21',
                'hash': '5e15b0168c9978cb5a50ad4c27c8065942d7fd30',
                'estado': 'Preemergencia Ambiental',
                'sin_sello_verde': '3-4-5-6-7-8',
                'con_sello_verde': '0-9',
                'actualizacion': '2015-06-22T00:00:00',
            },
            entries[0]
        )

    def test_restrictions_get_wrong_date_parameter(self):
        for date in ['', 'asdf', '21-06-2015']:
            response = self.app.get('/0/restricciones?fecha=' + date)
            self.assertEqual('application/json', response.mimetype)
            self.assertEqual(400, response.status_code)
            self.assertEqual('[]', response.data.decode())
