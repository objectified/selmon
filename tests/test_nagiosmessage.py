import unittest
from selmon.nagios.nagiosmessage import NagiosMessage


class TestNagiosMessage(unittest.TestCase):

    def test_raise_status(self):
        message = NagiosMessage()
        message.raise_status(NagiosMessage.NAGIOS_STATUS_WARNING)
        message.raise_status(NagiosMessage.NAGIOS_STATUS_CRITICAL)
        self.assertEqual(message.status_code, NagiosMessage.NAGIOS_STATUS_CRITICAL)

    def test_raise_status_highest_wins(self):
        message = NagiosMessage()
        message.raise_status(NagiosMessage.NAGIOS_STATUS_CRITICAL)
        message.raise_status(NagiosMessage.NAGIOS_STATUS_WARNING)
        self.assertEqual(message.status_code, NagiosMessage.NAGIOS_STATUS_CRITICAL)

    def test_add_multiple_messages_and_perfdata(self):
        message = NagiosMessage()
        message.add_msg('message 1')
        message.add_msg('message 2')
        message.add_perfdata('test_data', NagiosMessage.UOM_SEC, 2, 3, 5)

        message_string_repr = str(message)
        self.assertTrue("'test_data'=2s;3;5;;" in message_string_repr)
        self.assertTrue('message 1' in message_string_repr)
        self.assertTrue('message 2' in message_string_repr)
