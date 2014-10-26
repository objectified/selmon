import unittest
import time
from selmon.nagios.nagiosmessage import NagiosMessage
from selmon.nagios.contextmanagers import benchmark


class ContextManagersTest(unittest.TestCase):

    def test_benchmark_status(self):
        message = NagiosMessage()

        with benchmark(message, 'my_benchmark', warning=1, critical=2):
            time.sleep(1)

        self.assertEqual(message.status_code, NagiosMessage.NAGIOS_STATUS_WARNING)

        with benchmark(message, 'my_benchmark', warning=1, critical=2):
            time.sleep(2)

        self.assertEqual(message.status_code, NagiosMessage.NAGIOS_STATUS_CRITICAL)

