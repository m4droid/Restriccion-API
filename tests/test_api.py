import json

from mock import patch
import moment

from base_tests import BaseTestCase
from restriccion_scl.wsgi import app


class TestApi(BaseTestCase):

    def setUp(self):        
        self.app = app.test_client()

    def test_empty_entries(self):
        response = self.app.get('0/registro')
        self.assertEquals('application/json; charset=utf-8', response.content_type)
        self.assertEquals(200, response.status_code)
        self.assertEquals('[]', response.data.decode())

    @patch('restriccion_scl.crawlers.uoct.moment.now')
    def test_get_all_entries(self, mock_moment):
        mock_moment.side_effect = lambda: moment.date('2015-06-22', '%Y-%m-%d')
        from restriccion_scl.crawlers.uoct import UOCT_Crawler

        crawler = UOCT_Crawler()
        crawler.url = self.get_fixture_file_path('uoct.cl_restriccion-vehicular_0.html')
        crawler.parse()

        response = self.app.get('0/registro')
        self.assertEquals('application/json; charset=utf-8', response.content_type)
        self.assertEquals(200, response.status_code)

        entries = json.loads(response.data.decode())

        self.assertEquals(26, len(entries))

    @patch('restriccion_scl.crawlers.uoct.moment.now')
    def test_get_date_entry(self, mock_moment):
        mock_moment.side_effect = lambda: moment.date('2015-06-22', '%Y-%m-%d')
        from restriccion_scl.crawlers.uoct import UOCT_Crawler

        crawler = UOCT_Crawler()
        crawler.url = self.get_fixture_file_path('uoct.cl_restriccion-vehicular_0.html')
        crawler.parse()

        response = self.app.get('0/registro?fecha=2015-06-21')
        self.assertEquals('application/json; charset=utf-8', response.content_type)
        self.assertEquals(200, response.status_code)

        entries = json.loads(response.data.decode())

        self.assertEquals(1, len(entries))

        self.assertEquals(
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
