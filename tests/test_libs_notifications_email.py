from mock import Mock, patch
import moment

from .base_tests import BaseTestCase
from restriccion_scl.libs.notifications import send_to_email_addresses


class TestLibsNotificationsEmail(BaseTestCase):

    def test_libs_notifications_send_emails_empty_params(self):
        self.assertEqual([], send_to_email_addresses(None, None))
        self.assertEqual([], send_to_email_addresses('', None))
        self.assertEqual([], send_to_email_addresses(None, {}))
        self.assertEqual([], send_to_email_addresses('', {}))

    @patch('restriccion_scl.libs.notifications.smtplib.SMTP')
    def test_libs_notifications_send_emails_ok(self, mock_smtp):
        expected_emails = ["fake@email.com"]
        self.assertEqual(expected_emails, send_to_email_addresses(expected_emails, {"text": "test_template"}))
