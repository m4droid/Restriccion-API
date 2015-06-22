import unittest
import json

from mock import patch
import moment

from .base_tests import BaseTestCase
from restriccion_scl.wsgi import app


class TestApiDevices(BaseTestCase):

    def setUp(self):        
        self.app = app.test_client()

    def test_get_empty_params(self):
        params_list = ['', '?tipo=android', '?id=dummy']

        for params in params_list:
            response = self.app.get('0/dispositivos' + params)
            self.assertEqual('application/json; charset=utf-8', response.content_type)
            self.assertEqual(400, response.status_code)
            self.assertEqual('[]', response.data.decode())

    def test_get_not_found(self):
        response = self.app.get('0/dispositivos?tipo=android&id=dummy')
        self.assertEqual('application/json; charset=utf-8', response.content_type)
        self.assertEqual(404, response.status_code)
        self.assertEqual('[]', response.data.decode())

    def test_get_ok(self):
        expected_device = {'tipo': 'android', 'id': 'dummy', 'fecha_registro': moment.now().isoformat()}
        self.mongo_db.devices.insert_one(expected_device)

        response = self.app.get('0/dispositivos?tipo=android&id=dummy')
        self.assertEqual('application/json; charset=utf-8', response.content_type)
        self.assertEqual(200, response.status_code)

        data = json.loads(response.data.decode())

        self.assertEqual(list, type(data))

        del expected_device['_id']
        self.assertEqual(expected_device, data[0])

    def test_post_empty_params(self):
        data_list = [{}, {'tipo': 'android'}, {'id': 'dummy'}]

        for data in data_list:
            response = app.test_client().post('0/dispositivos', data=data)
            self.assertEqual('application/json; charset=utf-8', response.content_type)
            self.assertEqual(400, response.status_code)
            self.assertEqual('[]', response.data.decode())

    def test_post_wrong_type(self):
        response = app.test_client().post('0/dispositivos', data={'tipo': 'fake', 'id': 'dummy'})
        self.assertEqual('application/json; charset=utf-8', response.content_type)
        self.assertEqual(400, response.status_code)
        self.assertEqual('[]', response.data.decode())


    # @unittest.skip("Travis CI Failing")
    @patch('restriccion_scl.wsgi.moment.now')
    def test_post_ok(self, mock_moment):
        mock_datetime = moment.date('2015-06-22', '%Y-%m-%d')
        mock_moment.side_effect = lambda: mock_datetime

        expected_device = {'tipo': 'android', 'id': 'dummy'}

        response = self.app.post('/0/dispositivos', data=expected_device)

        self.assertEqual('application/json; charset=utf-8', response.content_type)
        self.assertEqual(200, response.status_code)

        data = json.loads(response.data.decode())

        self.assertEqual(list, type(data))

        expected_device['fecha_registro'] = mock_datetime.isoformat()
        self.assertEqual(expected_device, data[0])
