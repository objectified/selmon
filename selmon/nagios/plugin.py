import argparse
from selmon.nagios.nagiosmessage import NagiosMessage
from selenium import webdriver
from selenium.webdriver.remote.remote_connection import RemoteConnection
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import sys
import signal


class Plugin(object):
    """
    Base object for creating a Nagios plugin that use Selenium Webdriver for
    web application monitoring. Basic usage involves creating a class that
    inherits from `Plugin` and implements the run() method. After creating
    the class, instantiate it and call its start() method (do NOT call the
    run() method directly, run() gets called by start()).

    The following example illustrates how to build a plugin that monitors
    duckduckgo.com, searches for 'selenium' and verifies that the text
    'selenium' is present on the result page

    from selenium.webdriver.common.keys import Keys
    from selmon.nagios.plugin import Plugin
    from selmon.nagios.contextmanagers import benchmark


    class DuckduckGoMonitor(Plugin):

        def run(self):
            driver = self.get_driver()

            with benchmark(self.nagios_message, 'open_homepage', warning=2):
                driver.get('https://duckduckgo.com/')

            search_elem = driver.find_element_by_name('q')
            search_elem.send_keys('selenium')

            with benchmark(self.nagios_message, 'submit_form'):
                search_elem.send_keys(Keys.RETURN)

            body_elem = driver.find_element_by_css_selector('body')

            self.verify_text_present_in_elem(body_elem, 'selenium')


    ddg_monitor = DuckduckGoMonitor()
    ddg_monitor.start()
    """

    capabilities_mapping = {
        'chrome': DesiredCapabilities.CHROME,
        'firefox': DesiredCapabilities.FIREFOX,
        'android': DesiredCapabilities.ANDROID,
        'phantomjs': DesiredCapabilities.PHANTOMJS,
        'opera': DesiredCapabilities.OPERA,
        'htmlunit': DesiredCapabilities.HTMLUNIT,
        'htmlunit_withjs': DesiredCapabilities.HTMLUNITWITHJS,
        'ie': DesiredCapabilities.INTERNETEXPLORER,
        'ipad': DesiredCapabilities.IPAD,
        'iphone': DesiredCapabilities.IPHONE,
        'safari': DesiredCapabilities.SAFARI
    }

    def __init__(self):
        """
        Plugin constructor. Since this base object gets inherited, there is no need to take care of
        command line arguments, as the base object already does it for you. Run the following to see
        what parameters your script automatically expects while inheriting from Plugin:
        ./yourscript.py -h
        """
        self.nagios_message = NagiosMessage()

        self.arg_parser = argparse.ArgumentParser(add_help=True)
        self.arg_parser.add_argument('-H', '--host',
                            help='selenium webdriver remote host', required=True)
        self.arg_parser.add_argument('-t', '--timeout',
                            help='timeout in seconds to use for whole execution', required=True, type=int)
        self.arg_parser.add_argument('-b', '--browser',
                             help='browser to use, possible values: %s' % ','.join(self.capabilities_mapping.keys()),
                             required=True)

        # can be overridden in subclass
        self.add_extra_args()

        self.args = self.arg_parser.parse_args()

        if self.args.browser not in self.capabilities_mapping.keys():
            self.nagios_message.add_msg('browser is invalid: %s' % self.args.browser)
            self.nagios_message.raise_status(NagiosMessage.NAGIOS_STATUS_UNKNOWN)
            sys.exit(self.nagios_message.status_code)

        self.global_timeout = self.args.timeout

        self.driver = None
        try:
            self.conn = RemoteConnection(self.args.host)
            self.driver = webdriver.Remote(self.conn, DesiredCapabilities.CHROME)
        except Exception as e:
            if not e.args:
                e.args = ('No message in exception',)

            self.nagios_message.add_msg('Connection to Selenium Server failed with exception: %s, message: %s' %
                                        (str(type(e)), e.args[0]))
            self.nagios_message.raise_status(NagiosMessage.NAGIOS_STATUS_UNKNOWN)
            if self.driver:
                self.driver.quit()
            print self.nagios_message
            sys.exit(self.nagios_message.status_code)

    def get_driver(self):
        """
        Returns the Selenium Remote webdriver instance
        """
        return self.driver

    def verify_equals(self, label, actual_value, expected_value,
                      error_status=NagiosMessage.NAGIOS_STATUS_CRITICAL):
        """
        Creates a test that checks for object equality. The error_status parameter
        defines what Nagios status is returned when the test fails (use NAGIOS_STATUS_*
        constants defined in NagiosMessage)
        """
        if actual_value != expected_value:
            self.nagios_message.add_msg('Test failed: %s, expected: %s, actual: %s' %
                                        (label, expected_value, actual_value))
            self.nagios_message.raise_status(error_status)
            return False

        return True

    def verify_text_present_in_elem(self, elem, text,
                                    error_status=NagiosMessage.NAGIOS_STATUS_CRITICAL):
        """
        Verifies that the given text is present in the `text` property of a Selenium
        Element object. The error_status parameter defines what Nagios status is returned
        when the test fails (use NAGIOS_STATUS_* constants defined in NagiosMessage)
        """
        if not text in elem.text:
            self.nagios_message.add_msg('Text not present: %s' % text)
            self.nagios_message.raise_status(error_status)
            return False

        return True

    def run(self):
        """
        Override this method in your own plugin, then call start() on the newly created
        object (not run() itself!)
        """
        pass

    def add_extra_args(self):
        """
        To add extra arguments to your plugin, override this method and add arguments
        to self.arg_parser (an argparse ArgumentParser object). The argument values
        will be available in self.args
        """
        pass

    def start(self):
        """
        Call the start() method for actual execution of the plugin. It calls the run()
        method, creates a Nagios message and outputs it. Appropriate exit codes are
        determined during the test run and the plugin exits accordingly.
        """
        def timeout_handler(signum, frame):
            raise TimeoutException()

        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(self.global_timeout)

        try:
            self.run()
        except TimeoutException:
            self.nagios_message.add_msg('Global timeout of %s seconds reached' % self.global_timeout)
            self.nagios_message.raise_status(NagiosMessage.NAGIOS_STATUS_CRITICAL)
        except Exception as e:
            message = e.message
            if not message:
                message = 'No message in exception'
            self.nagios_message.add_msg('FAILED: Exception of type: %s, message: %s' %
                                        (e.__class__.__name__, message))
            self.nagios_message.raise_status(NagiosMessage.NAGIOS_STATUS_CRITICAL)
        finally:
            self.driver.quit()

            print self.nagios_message
            sys.exit(self.nagios_message.status_code)

    def _get_deferred_element_by(self, search, by, timeout=5):
        elem = WebDriverWait(self.driver, timeout).until(
            expected_conditions.presence_of_element_located((by, search)),
            'Timeout occurred while waiting for element: %s' % search
        )
        return elem

    def get_deferred_element_by_xpath(self, xpath, timeout=5):
        return self._get_deferred_element_by(xpath, By.XPATH, timeout)

    def get_deferred_element_by_class(self, class_name, timeout=5):
        return self._get_deferred_element_by(class_name, By.CLASS_NAME, timeout)

    def get_deferred_element_by_css_selector(self, selector, timeout=5):
        return self._get_deferred_element_by(selector, By.CSS_SELECTOR, timeout)

    def get_deferred_element_by_id(self, id, timeout=5):
        return self._get_deferred_element_by(id, By.ID, timeout)

    def get_deferred_element_by_link_text(self, link_text, timeout=5):
        return self._get_deferred_element_by(link_text, By.LINK_TEXT, timeout)

    def get_deferred_element_by_tag_name(self, tag_name, timeout=5):
        return self._get_deferred_element_by(tag_name, By.TAG_NAME, timeout)

    def get_deferred_element_by_name(self, name, timeout=5):
        return self._get_deferred_element_by(name, By.NAME, timeout)


class TimeoutException(Exception):
    pass
