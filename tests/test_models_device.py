# -*- coding: utf-8 -*-
from unittest.mock import Mock, patch

import moment

from .base_tests import BaseTestCase

from restriccion import CONFIG
from restriccion.models.device import Device


class TestModelsDevice(BaseTestCase):

    def test_models_device_get_empty_params(self):
        Device.insert_one(self.mongo_db, 'email', 'dummy@email.com')
        self.assertEqual(0, len(Device.get(self.mongo_db)))
        self.assertEqual(0, len(Device.get(self.mongo_db, type_='email')))
        self.assertEqual(0, len(Device.get(self.mongo_db, id_='dummy@email.com')))

    @patch('restriccion.models.device.moment.utcnow')
    def test_models_device_insert_ok(self, mock_moment):
        mock_datetime = moment.utc('2015-06-22', '%Y-%m-%d').timezone(CONFIG['moment']['timezone'])
        mock_moment.side_effect = lambda: mock_datetime

        expected_data = {
            'tipo': 'email',
            'id': 'dummy@email.com',
            'fecha_registro': mock_datetime.isoformat()
        }

        response = Device.insert_one(self.mongo_db, 'email', 'dummy@email.com')

        self.assertEqual(1, self.mongo_db.devices.count())
        device_in_db = self.mongo_db.devices.find_one({'tipo': 'email', 'id': 'dummy@email.com'}, {'_id': 0})
        self.assertEqual(expected_data, device_in_db)

        self.assertEqual('ok', response['status'])
        self.assertEqual(expected_data, response['data'])

    @patch('restriccion.models.device.moment.utcnow')
    def test_models_device_insert_existing(self, mock_moment):
        mock_datetime = moment.utc('2015-06-22', '%Y-%m-%d').timezone(CONFIG['moment']['timezone'])
        mock_moment.side_effect = lambda: mock_datetime

        expected_data = {
            'tipo': 'email',
            'id': 'dummy@email.com',
            'fecha_registro': mock_datetime.isoformat()
        }

        Device.insert_one(self.mongo_db, 'email', 'dummy@email.com')

        # Mock new date
        mock_datetime = moment.date('2015-06-23', '%Y-%m-%d')
        mock_moment.side_effect = lambda: mock_datetime

        response = Device.insert_one(self.mongo_db, 'email', 'dummy@email.com')

        self.assertEqual(1, self.mongo_db.devices.count())
        device_in_db = self.mongo_db.devices.find_one({'tipo': 'email', 'id': 'dummy@email.com'}, {'_id': 0})
        self.assertEqual(expected_data, device_in_db)

        # Keep previous data
        self.assertEqual('ok', response['status'])
        self.assertEqual(expected_data, response['data'])

    def test_models_device_insert_invalid_type(self):
        response = Device.insert_one(self.mongo_db, 'fake_device', 'asdf')

        self.assertEqual(0, self.mongo_db.devices.count())

        self.assertEqual('error', response['status'])
        self.assertEqual('Tipo de dispositivo no permitido.', response['mensaje'])

    def test_models_device_insert_invalid_email(self):
        response = Device.insert_one(self.mongo_db, 'email', 'supra$invalid_address')

        self.assertEqual(0, self.mongo_db.devices.count())

        self.assertEqual('error', response['status'])
        self.assertEqual('Email inválido', response['mensaje'])

    @patch('restriccion.libs.notifications.smtplib.SMTP')
    @patch('restriccion.models.device.moment.utcnow')
    @patch('restriccion.libs.notifications.GCM')
    def test_models_device_notify_gcm_unregistered_or_invalid_ids(self, mock_gcm, mock_moment, mock_smtp):
        mock_datetime = moment.utc('2015-06-22', '%Y-%m-%d').timezone(CONFIG['moment']['timezone'])
        mock_moment.side_effect = lambda: mock_datetime

        mock_method = Mock()
        mock_method.json_request = Mock(return_value={
            'errors': {
                'NotRegistered': ['gcm_not_registered'],
                'InvalidRegistration': ['gcm_invalid_registration']
            }
        })
        mock_gcm.side_effect = lambda *a, **ka: mock_method

        Device.insert_one(self.mongo_db, 'email', 'email@to_remain.com')
        Device.insert_one(self.mongo_db, 'gcm', 'gcm_not_registered')
        Device.insert_one(self.mongo_db, 'gcm', 'gcm_invalid_registration')

        Device.notify(self.mongo_db, {'fake': 'data'})

        self.assertEqual(1, self.mongo_db.devices.find({'tipo': 'email'}).count())
        self.assertEqual(0, self.mongo_db.devices.find({'tipo': 'gcm'}).count())

    @patch('restriccion.libs.notifications.smtplib.SMTP')
    @patch('restriccion.models.device.moment.utcnow')
    @patch('restriccion.libs.notifications.GCM')
    def test_models_device_notify_gcm_canonical_ids_response(self, mock_gcm, mock_moment, mock_smtp):
        mock_datetime = moment.utc('2015-06-22', '%Y-%m-%d').timezone(CONFIG['moment']['timezone'])
        mock_moment.side_effect = lambda: mock_datetime

        mock_method = Mock()
        mock_method.json_request = Mock(return_value={
            'canonical': {
                'gcm_id_to_remove_1': 'gcm_to_remain_2',
                'gcm_id_to_remove_2': 'gcm_to_remain_3',
            }
        })
        mock_gcm.side_effect = lambda *a, **ka: mock_method

        Device.insert_one(self.mongo_db, 'email', 'email@to_remain.com')
        Device.insert_one(self.mongo_db, 'gcm', 'gcm_to_remain_1')
        Device.insert_one(self.mongo_db, 'gcm', 'gcm_to_remain_2')
        Device.insert_one(self.mongo_db, 'gcm', 'gcm_id_to_remove_1')
        Device.insert_one(self.mongo_db, 'gcm', 'gcm_id_to_remove_2')

        Device.notify(self.mongo_db, {'fake': 'data'}, collapse_key='fake_type')

        self.assertEqual(1, self.mongo_db.devices.find({'tipo': 'email'}).count())

        query = {'tipo': 'gcm', 'id': {'$not': {'$in': ['gcm_id_to_remove_1', 'gcm_id_to_remove_1']}}}
        self.assertEqual(3, self.mongo_db.devices.find(query).count())
