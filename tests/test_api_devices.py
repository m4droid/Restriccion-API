# -*- coding: utf-8 -*-
import json

from mock import patch
import moment

from .base_tests import ApiBaseTestCase
from restriccion import CONFIG
from restriccion.models.device import Device


class TestApiDevices(ApiBaseTestCase):

    def test_devices_get_empty_params(self):
        params_list = ['', '?tipo=gcm', '?id=dummy']

        for params in params_list:
            response = self.app.get('/0/dispositivos' + params)
            self.assertEqual('application/json', response.mimetype)
            self.assertEqual(404, response.status_code)
            self.assertEqual('[]', response.data.decode())

    def test_devices_get_not_found(self):
        response = self.app.get('0/dispositivos?tipo=gcm&id=dummy')
        self.assertEqual('application/json', response.mimetype)
        self.assertEqual(404, response.status_code)
        self.assertEqual('[]', response.data.decode())

    @patch('restriccion.models.device.moment.utcnow')
    def test_devices_get_ok(self, mock_moment):
        mock_datetime = moment.utc('2015-06-22', '%Y-%m-%d').timezone(CONFIG['moment']['timezone'])
        mock_moment.side_effect = lambda: mock_datetime

        expected_device = {'tipo': 'gcm', 'id': 'dummy', 'fecha_registro': mock_datetime.isoformat()}
        Device.insert_one(self.mongo_db, 'gcm', 'dummy')

        response = self.app.get('/0/dispositivos?tipo=gcm&id=dummy')
        self.assertEqual('application/json', response.mimetype)
        self.assertEqual(200, response.status_code)

        data = json.loads(response.data.decode())

        self.assertEqual(list, type(data))
        self.assertEqual(expected_device, data[0])

    def test_devices_get_email_without_delete_param(self):
        response = self.app.get('/0/dispositivos?tipo=email&id=dummy@email.com')

        self.assertEqual('application/json', response.mimetype)
        self.assertEqual(404, response.status_code)
        self.assertEqual('[]', response.data.decode())

    def test_devices_post_empty_params(self):
        expected_response = {'mensaje': 'Faltan parámetros.', 'status': 'error'}
        data_list = [{}, {'tipo': 'gcm'}, {'id': 'dummy'}]

        for data in data_list:
            response = self.app.post('/0/dispositivos', data=data)
            self.assertEqual('application/json', response.mimetype)
            self.assertEqual(400, response.status_code)
            self.assertEqual(expected_response, json.loads(response.data.decode()))

    def test_devices_post_wrong_type(self):
        expected_response = {'status': 'error', 'mensaje': 'Tipo de dispositivo no permitido.'}
        response = self.app.post('/0/dispositivos', data={'tipo': 'fake', 'id': 'dummy'})
        self.assertEqual('application/json', response.mimetype)
        self.assertEqual(400, response.status_code)
        self.assertEqual(expected_response, json.loads(response.data.decode()))

    @patch('restriccion.wsgi.moment.utcnow')
    def test_devices_post_ok(self, mock_moment):
        mock_datetime = moment.date('2015-06-22', '%Y-%m-%d')
        mock_moment.side_effect = lambda: mock_datetime

        expected_device = {'tipo': 'gcm', 'id': 'dummy'}

        response = self.app.post('/0/dispositivos', data=expected_device)

        self.assertEqual('application/json', response.mimetype)
        self.assertEqual(200, response.status_code)

        data = json.loads(response.data.decode())

        self.assertEqual(dict, type(data))

        expected_device['fecha_registro'] = mock_datetime.isoformat()
        self.assertEqual(expected_device, data)

    @patch('restriccion.wsgi.moment.utcnow')
    def test_devices_post_existing(self, mock_moment):
        mock_datetime = moment.utc('2015-06-22', '%Y-%m-%d').timezone(CONFIG['moment']['timezone'])
        mock_moment.side_effect = lambda: mock_datetime

        expected_device = {
            'tipo': 'gcm',
            'id': 'dummy',
            'fecha_registro': moment.date('2015-06-21', '%Y-%m-%d').isoformat()
        }

        Device.insert_one(self.mongo_db, 'gcm', 'dummy')

        response = self.app.post('/0/dispositivos', data={'tipo': 'gcm', 'id': 'dummy'})

        self.assertEqual('application/json', response.mimetype)
        self.assertEqual(200, response.status_code)

        data = json.loads(response.data.decode())

        self.assertEqual(dict, type(data))

        self.assertNotEqual(expected_device['fecha_registro'], data['fecha_registro'])
        del expected_device['fecha_registro']
        del data['fecha_registro']

        self.assertEqual(expected_device, data)

    @patch('restriccion.wsgi.moment.utcnow')
    def test_devices_post_email_ok(self, mock_moment):
        mock_datetime = moment.utc('2015-06-22', '%Y-%m-%d').timezone(CONFIG['moment']['timezone'])
        mock_moment.side_effect = lambda: mock_datetime

        expected_device = {
            'tipo': 'email',
            'id': 'dummy@email.com',
            'fecha_registro': mock_datetime.isoformat()
        }
        self.mongo_db.devices.insert_one(expected_device)
        del expected_device['_id']
        del expected_device['fecha_registro']

        response = self.app.post('/0/dispositivos', data=expected_device)

        self.assertEqual('application/json', response.mimetype)
        self.assertEqual(200, response.status_code)

        data = json.loads(response.data.decode())

        self.assertEqual(dict, type(data))

        expected_device['fecha_registro'] = mock_datetime.isoformat()
        self.assertEqual(expected_device, data)

    def test_devices_post_email_invalid(self):
        expected_response = {'mensaje': 'Email inválido', 'status': 'error'}

        response = self.app.post('/0/dispositivos', data={'tipo': 'email', 'id': 'invalid$email'})
        self.assertEqual('application/json', response.mimetype)
        self.assertEqual(400, response.status_code)
        self.assertEqual(expected_response, json.loads(response.data.decode()))

    def test_devices_delete_email_with_get(self):
        expected_devices = [
            {
                'tipo': 'gcm',
                'id': 'dummy',
                'fecha_registro': moment.utcnow().isoformat()
            },
            {
                'tipo': 'email',
                'id': 'dummy@email.com',
                'fecha_registro': moment.utcnow().isoformat()
            }
        ]
        self.mongo_db.devices.insert_many(expected_devices)

        response = self.app.get('/0/dispositivos?tipo=email&id=dummy@email.com&borrar=1')

        self.assertEqual('application/json', response.mimetype)
        self.assertEqual(200, response.status_code)

        del expected_devices[1]['_id']
        expected_devices[1]['mensaje'] = 'El dispositivo ha sido borrado con éxito'

        data = json.loads(response.data.decode())
        self.assertEqual(expected_devices[1], data[0])

        self.assertEqual(1, self.mongo_db.devices.count())

    def test_devices_delete_gcm_with_get(self):
        expected_devices = [
            {
                'tipo': 'gcm',
                'id': 'dummy',
                'fecha_registro': moment.utcnow().isoformat()
            },
            {
                'tipo': 'email',
                'id': 'dummy@email.com',
                'fecha_registro': moment.utcnow().isoformat()
            }
        ]
        self.mongo_db.devices.insert_many(expected_devices)

        response = self.app.get('/0/dispositivos?tipo=gcm&id=dummy&borrar=1')

        self.assertEqual('application/json', response.mimetype)
        self.assertEqual(400, response.status_code)
        self.assertEqual('[]', response.data.decode())
        self.assertEqual(2, self.mongo_db.devices.count())
