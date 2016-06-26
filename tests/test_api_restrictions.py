import json

from mock import patch
import moment

from .base_tests import ApiBaseTestCase
from restriccion import CONFIG
from restriccion.crawlers.uoct import UOCT_Crawler
from restriccion.models.restriction import Restriction


class TestApiRestrictions(ApiBaseTestCase):

    def test_restrictions_get_empty_entries(self):
        response = self.app.get('/0/restricciones')

        self.assertEqual('application/json', response.mimetype)
        self.assertEqual(200, response.status_code)
        self.assertEqual('[]', response.data.decode())

    @patch('restriccion.models.base_report.moment.utcnow')
    def test_restrictions_get_all(self, mock_moment):
        mock_moment.side_effect = lambda: moment.utc('2015-06-22', '%Y-%m-%d').timezone(CONFIG['moment']['timezone'])

        crawler = UOCT_Crawler()
        crawler.url = self.get_fixture_file_path('uoct.cl_restriccion-vehicular_0.html')
        Restriction.insert_many(self.mongo_db, crawler.parse())

        response = self.app.get('/0/restricciones')
        self.assertEqual('application/json', response.mimetype)
        self.assertEqual(200, response.status_code)

        entries = json.loads(response.data.decode())

        self.assertEqual(10, len(entries))

    @patch('restriccion.models.base_report.moment.utcnow')
    def test_restrictions_get_with_date_param(self, mock_moment):
        mock_datetime = moment.utc('2015-06-22', '%Y-%m-%d').timezone(CONFIG['moment']['timezone'])
        mock_moment.side_effect = lambda: mock_datetime

        crawler = UOCT_Crawler()
        crawler.url = self.get_fixture_file_path('uoct.cl_restriccion-vehicular_0.html')
        Restriction.insert_many(self.mongo_db, crawler.parse())

        response = self.app.get('/0/restricciones?fecha=2015-06-21')
        self.assertEqual('application/json', response.mimetype)
        self.assertEqual(200, response.status_code)

        entries = json.loads(response.data.decode())

        self.assertEqual(1, len(entries))

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
            entries[0]
        )

    def test_restrictions_get_wrong_date_parameter(self):
        for date in ['', 'asdf', '21-06-2015']:
            response = self.app.get('/0/restricciones?fecha=' + date)
            self.assertEqual('application/json', response.mimetype)
            self.assertEqual(400, response.status_code)
            self.assertEqual('[]', response.data.decode())
