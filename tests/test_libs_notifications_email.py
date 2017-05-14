from unittest.mock import Mock, patch

from .base_tests import BaseTestCase

from restriccion.libs.notifications import send_to_email_addresses


class TestLibsNotificationsEmail(BaseTestCase):

    def test_libs_notifications_send_emails_empty_params(self):
        self.assertEqual([], send_to_email_addresses(None, None))
        self.assertEqual([], send_to_email_addresses('', None))
        self.assertEqual([], send_to_email_addresses(None, {}))
        self.assertEqual([], send_to_email_addresses('', {}))

    @patch('restriccion.libs.notifications.smtplib.SMTP')
    def test_libs_notifications_send_emails_ok(self, mock_smtp):
        expected_emails = ["fake@email.com"]
        self.assertEqual(expected_emails, send_to_email_addresses(expected_emails, {"text": "test_template"}))

    @patch('restriccion.libs.notifications.smtplib')
    def test_libs_notifications_send_emails_error(self, mock_smtplib):
        mock_class = Mock()
        mock_class.sendmail = Mock(side_effect=Exception())
        mock_smtplib.SMTP = lambda *a: mock_class

        expected_emails = ["fake@email.com"]
        self.assertEqual([], send_to_email_addresses(expected_emails, {"text": "test_template"}))

    @patch('restriccion.libs.notifications.CONFIG', new={'notifications': {'email': {'enabled': False}}})
    def test_libs_notifications_send_emails_disabled(self):
        expected_emails = ["fake@email.com"]
        self.assertEqual([], send_to_email_addresses(expected_emails, {"text": "test_template"}))
