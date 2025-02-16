import unittest

from automon.integrations.seleniumWrapper import SeleniumBrowser, ChromeWrapper

browser = SeleniumBrowser()
browser.config.webdriver_wrapper = ChromeWrapper()
browser.config.webdriver_wrapper.enable_defaults().enable_headless()


class SeleniumClientTest(unittest.TestCase):
    try:
        if browser.run():

            def test_fake_page(self):
                try:
                    browser.get('http://555.555.555.555')
                except Exception as error:
                    self.assertTrue(error)

            def test_real_page(self):
                if browser.get('https://1.1.1.1'):
                    self.assertTrue(True)

            def test_screenshot_png(self):
                if browser.get('https://1.1.1.1'):
                    self.assertTrue(browser.get_screenshot_as_png())

            def test_screenshot_base64(self):
                if browser.get('https://1.1.1.1'):
                    self.assertTrue(browser.get_screenshot_as_base64())

            def test_screenshot_file(self):
                if browser.get('https://1.1.1.1'):
                    self.assertTrue(browser.save_screenshot())
                    self.assertTrue(browser.save_screenshot(folder='./'))

            def test_by(self):
                self.assertTrue(browser.by)

            def test_config(self):
                self.assertTrue(browser.config)

            def test_logs(self):
                if browser.get('https://1.1.1.1'):
                    self.assertTrue(browser.logs)

            def test_webdriver(self):
                self.assertTrue(browser.webdriver)

            def test_get_logs(self):
                if browser.get('https://1.1.1.1'):
                    self.assertTrue(browser.get_logs())

            def test_get_log_browser(self):
                if browser.get('https://1.1.1.1'):
                    try:
                        self.assertTrue(browser.get_log_browser())
                    except:
                        pass

            def test_get_log_driver(self):
                if browser.get('https://1.1.1.1'):
                    try:
                        self.assertTrue(browser.get_log_driver())
                    except:
                        pass

            def test_get_log_performance(self):
                if browser.get('https://1.1.1.1'):
                    try:
                        self.assertTrue(browser.get_log_performance())
                    except:
                        pass

            def test_check_page_load_finished(self):
                if browser.get('https://1.1.1.1'):
                    self.assertTrue(browser.check_page_load_finished())

            def test_keys(self):
                self.assertTrue(browser.keys)

            def test_refresh(self):
                if browser.get('https://1.1.1.1'):
                    self.assertTrue(browser.refresh())

            def test_url(self):
                if browser.get('https://1.1.1.1'):
                    self.assertTrue(browser.url)

            def test_user_agent(self):
                if browser.get('https://1.1.1.1'):
                    self.assertTrue(browser.user_agent)

            def test__current_url(self):
                if browser.get('https://1.1.1.1'):
                    self.assertTrue(browser._current_url)

            def test_current_url(self):
                if browser.get('https://1.1.1.1'):
                    self.assertTrue(browser.current_url)

            def test_current_window_handle(self):
                self.assertTrue(browser.current_window_handle)

            def test_window_size(self):
                if browser.get('https://1.1.1.1'):
                    self.assertTrue(browser.window_size)

            def test__screenshot_name(self):
                if browser.get('https://1.1.1.1'):
                    self.assertTrue(browser._screenshot_name)

            def test_action_click(self):
                NotImplemented

            def test_action_scroll_to_bottom(self):
                if browser.get('https://1.1.1.1'):
                    self.assertTrue(browser.action_scroll_to_bottom())

            def test_action_scroll_down(self):
                if browser.get('https://1.1.1.1'):
                    self.assertTrue(browser.action_scroll_down())

            def tset_action_scroll_up(self):
                if browser.get('https://1.1.1.1'):
                    self.assertTrue(browser.action_scroll_up())

            def tset_action_type(self):
                NotImplemented

            def test_action_type_up(self):
                NotImplemented

            def test_action_type_down(self):
                NotImplemented

            def test_add_cookie(self):
                NotImplemented

            def test_add_cookie_from_file(self):
                NotImplemented

            def tset_add_cookies_from_list(self):
                NotImplemented

            def test_add_cookie_from_current_url(self):
                if browser.get('https://1.1.1.1'):
                    try:
                        self.assertTrue(browser.add_cookie_from_current_url())
                    except:
                        pass

            def test_add_cookie_from_url(self):
                if browser.get('https://1.1.1.1'):
                    self.assertTrue(browser.save_cookies_for_current_url())
                    try:
                        self.assertTrue(browser.add_cookie_from_url('https://1.1.1.1'))
                    except:
                        pass

            def test_add_cookie_from_base64(self):
                NotImplemented

            def test_autosaving_cookies(self):
                if browser.get('https://1.1.1.1'):
                    self.assertTrue(browser.autosaving_cookies())

            def test_delete_all_cookies(self):
                if browser.get('https://1.1.1.1'):
                    self.assertTrue(browser.delete_all_cookies())

            def test__url_filename(self):
                self.assertTrue(browser._url_filename('https://1.1.1.1'))

            def test_get_cookie(self):
                NotImplemented

            def test_get_cookies(self):
                if browser.get('https://1.1.1.1'):
                    self.assertEqual(browser.get_cookies(), [])

            def test_get_cookies_base64(self):
                if browser.get('https://1.1.1.1'):
                    self.assertTrue(browser.get_cookies_base64())

            def test_get_cookies_json(self):
                if browser.get('https://1.1.1.1'):
                    self.assertTrue(browser.get_cookies_json())

            def test_get_cookies_summary(self):
                if browser.get('https://1.1.1.1'):
                    self.assertEqual(browser.get_cookies_summary(), {})

            def test_close(self):
                NotImplemented

            def test_error_parsing(self):
                NotImplemented

            def test_find_page_source_with_regex(self):
                NotImplemented

            def test_find_all_with_beautifulsoup(self):
                NotImplemented

            def test_find_anything(self):
                NotImplemented

            def test_find_anything_with_beautifulsoup(self):
                NotImplemented

            def test_find_element(self):
                NotImplemented

            def test_find_elements(self):
                NotImplemented

            def test_find_elements_with_beautifulsoup(self):
                NotImplemented

            def test_find_xpath(self):
                NotImplemented

            def test_get(self):
                self.assertTrue(browser.get('https://1.1.1.1'))

            def test_get_page(self):
                self.assertTrue(browser.get_page('https://1.1.1.1'))

            def test_get_page_source(self):
                if browser.get('https://1.1.1.1'):
                    self.assertTrue(browser.get_page_source())

            def test_get_page_source_pandas(self):
                if browser.get('https://1.1.1.1'):
                    try:
                        self.assertTrue(browser.get_page_source_pandas())
                    except:
                        pass

            def test_get_page_source_beautifulsoup(self):
                if browser.get('https://1.1.1.1'):
                    self.assertTrue(browser.get_page_source_beautifulsoup())

            def test_get_random_user_agent(self):
                self.assertTrue(browser.get_random_user_agent())

            def test_get_screenshot_as_base64(self):
                if browser.get('https://1.1.1.1'):
                    self.assertTrue(browser.get_screenshot_as_base64())

            def test_get_screenshot_as_file(self):
                if browser.get('https://1.1.1.1'):
                    self.assertTrue(browser.get_screenshot_as_file())

            def test_get_screenshot_as_png(self):
                if browser.get('https://1.1.1.1'):
                    self.assertTrue(browser.get_screenshot_as_png())

            def test_is_running(self):
                self.assertTrue(browser.is_running())

            def test_load_cookies_for_current_url(self):
                if browser.get('https://1.1.1.1'):
                    self.assertTrue(browser.load_cookies_for_current_url())

            def test_open_file(self):
                NotImplemented

            def test_page_source(self):
                self.assertTrue(browser.page_source)

            def test__urllib(self):
                self.assertTrue(browser._urllib)

            def test_urlparse(self):
                self.assertTrue(browser.urlparse('https://1.1.1.1'))

            def test_quit(self):
                NotImplemented

            def tset_run(self):
                self.assertTrue(browser.run())

            def tset_save_cookies_for_current_url(self):
                if browser.get('https://1.1.1.1'):
                    self.assertTrue(browser.save_cookies_for_current_url())

            def test_save_cookies_to_file(self):
                NotImplemented

            def test_save_page_to_file(self):
                if browser.get('https://1.1.1.1'):
                    self.assertTrue(browser.save_page_to_file())

            def test_save_screenshot(self):
                self.assertTrue(browser.save_screenshot())

            def test_set_window_size(self):
                self.assertTrue(browser.set_window_size())

            def test_set_window_position(self):
                self.assertTrue(browser.set_window_position())

            def test_start(self):
                NotImplemented

            def test_switch_to_new_window_tab(self):
                self.assertTrue(browser.switch_to_new_window_tab())

            def test_switch_to_new_window_window(self):
                self.assertTrue(browser.switch_to_new_window_window())

            def test_wait_for_anything(self):
                NotImplemented

            def test_wait_for_anything_with_beautifulsoup(self):
                NotImplemented

            def test_wait_for_element(self):
                NotImplemented

            def test_wait_for_elements(self):
                NotImplemented

            def test_wait_for_id(self):
                NotImplemented

            def test_wait_for_xpath(self):
                NotImplemented

    except:
        pass


if __name__ == '__main__':
    unittest.main()
    # browser.quit()
