from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By


class SelmonRemoteDriver(webdriver.Remote):

    """
    This class extends Selenium's RemoteConnection class, to provide a number
    of convenience functions for use with monitoring
    """

    def is_text_present_in_elem(self, elem, text):
        """
        Verifies that the given text is present in the `text` property of a
        Selenium Element object. The error_status parameter defines what Nagios
        status is returned when the test fails (use NAGIOS_STATUS_* constants
        defined in NagiosMessage) """
        if text not in elem.text:
            return False

        return True

    def verify_broken_images(self):
        """
        Verifies if the current page has broken images. Adds information to the
        NagiosMessage object, and raises its exit status to the status given to
        the error_status kwarg (defaults to warning)
        """
        broken_images = self.get_broken_images()
        if len(broken_images) > 0:
            return broken_images

        return None

    def get_broken_images(self):
        """
        Get broken images from current web location. There is no natural way to
        do this through Selenium. The way this method works, is that it
        retrieves all src/naturalHeight/naturalWidth properties of all image
        objects from the DOM, iterates over the properties for each image, and
        checks if its naturalWidth and naturalHeight properties are both zero.
        If so, it's probably a broken image, and it will be reported as such. It
        explicitly executes all logic inside the browser to avoid Selenium call
        overhead.
        """
        broken_images = []

        images = self.execute_script("""
            var imageinfo = new Array();
            for(var i = 0; i < document.images.length; i++) {
                imageinfo.push({
                    src: document.images[i].src,
                    naturalHeight: document.images[i].naturalHeight,
                    naturalWidth: document.images[i].naturalWidth
                });
            }
            return imageinfo;""")

        for image in images:
            natural_width = int(image['naturalWidth'])
            natural_height = int(image['naturalHeight'])

            if not natural_width and not natural_height:
                broken_images.append(image['src'])

        return broken_images

    def _find_deferred_element_by(self, search, by, timeout=5):
        elem = WebDriverWait(self, timeout).until(
            expected_conditions.presence_of_element_located((by, search)),
            'Timeout occurred while waiting for element: %s' % search
        )
        return elem

    def find_deferred_element_by_xpath(self, xpath, timeout=5):
        return self._find_deferred_element_by(xpath, By.XPATH, timeout)

    def find_deferred_element_by_class(self, class_name, timeout=5):
        return self._find_deferred_element_by(
            class_name,
            By.CLASS_NAME,
            timeout)

    def find_deferred_element_by_css_selector(self, selector, timeout=5):
        return self._find_deferred_element_by(
            selector,
            By.CSS_SELECTOR,
            timeout)

    def find_deferred_element_by_id(self, id, timeout=5):
        return self._find_deferred_element_by(id, By.ID, timeout)

    def find_deferred_element_by_link_text(self, link_text, timeout=5):
        return self._find_deferred_element_by(link_text, By.LINK_TEXT, timeout)

    def find_deferred_element_by_tag_name(self, tag_name, timeout=5):
        return self._find_deferred_element_by(tag_name, By.TAG_NAME, timeout)

    def find_deferred_element_by_name(self, name, timeout=5):
        return self._find_deferred_element_by(name, By.NAME, timeout)
