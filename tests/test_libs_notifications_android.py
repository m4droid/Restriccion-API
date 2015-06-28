from mock import Mock, patch
import moment

from .base_tests import BaseTestCase
from restriccion_scl.libs.notifications import send_to_gcm


class TestLibsNotificationsGcm(BaseTestCase):

    def test_libs_notifications_send_to_gcm_empty_params(self):
        self.assertEqual(([], []), send_to_gcm(None, None))
        self.assertEqual(([], []), send_to_gcm([], None))
        self.assertEqual(([], []), send_to_gcm(None, {}))
        self.assertEqual(([], []), send_to_gcm([], {}))

    @patch('restriccion_scl.libs.notifications.GCM')
    def test_libs_notifications_send_to_gcm_empty_response(self, mock_gcm):
        mock_method = Mock()
        mock_method.json_request = Mock(return_value={})
        mock_gcm.side_effect = lambda *a, **ka: mock_method

        self.assertEqual(([], []), send_to_gcm(['fake_gcm_id'], {'payload': 'asdf'}))

    @patch('restriccion_scl.libs.notifications.GCM')
    def test_libs_notifications_send_to_gcm_unregistered_or_invalid_devices(self, mock_gcm):
        mock_method = Mock()
        mock_method.json_request = Mock(return_value={
            'errors': {
                'NotRegistered': ['gcm_not_registered'],
                'InvalidRegistration': ['gcm_invalid_registration']
            }
        })
        mock_gcm.side_effect = lambda *a, **ka: mock_method

        expected_value = (
            [],
            ['gcm_not_registered', 'gcm_invalid_registration']
        )

        self.assertEqual(expected_value, send_to_gcm(['fake_gcm_id'], {'payload': 'asdf'}))

    @patch('restriccion_scl.libs.notifications.GCM')
    def test_libs_notifications_send_to_gcm_receiving_canonical_ids_response(self, mock_gcm):
        mock_method = Mock()
        mock_method.json_request = Mock(return_value={
            'canonical': {
                'gcm_id_to_remove': 'gcm_to_remain_3',
            }
        })
        mock_gcm.side_effect = lambda *a, **ka: mock_method

        expected_value = (
            ['gcm_to_remain_3'],
            ['gcm_id_to_remove']
        )

        self.assertEqual(expected_value, send_to_gcm(['fake_gcm_id'], {'payload': 'asdf'}))
