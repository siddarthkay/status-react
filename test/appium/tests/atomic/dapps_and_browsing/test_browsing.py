from tests import marks
from tests.base_test_case import SingleDeviceTestCase
from views.sign_in_view import SignInView


class TestBrowsing(SingleDeviceTestCase):
    @marks.testrail_id(5395)
    @marks.medium
    def test_back_forward_refresh_navigation_history_kept_after_relogin(self):
        sign_in = SignInView(self.driver)
        home = sign_in.create_user()
        dapp = home.dapp_tab_button.click()
        ru_url = 'https://ru.m.wikipedia.org'
        browsing = dapp.open_url(ru_url)
        browsing.element_by_text_part('Добро пожаловать').wait_for_element(20)

        browsing.just_fyi("Check next page")
        browsing.just_fyi('Navigate to next page and back')
        browsing.element_by_text_part('свободную энциклопедию').click()
        browsing.element_by_text_part('Свободный контент')
        browsing.browser_previous_page_button.click()
        browsing.wait_for_element_starts_with_text('свободную энциклопедию')

        browsing.just_fyi('Relogin and check that tap on "Next" navigates to next page')
        profile = home.profile_button.click()
        profile.switch_network()
        home.dapp_tab_button.click()
        browsing.open_tabs_button.click()
        dapp.element_by_text_part(ru_url).click()
        browsing.wait_for_element_starts_with_text('свободную энциклопедию')
        browsing.browser_next_page_button.click()
        browsing.element_by_text_part('Свободный контент').wait_for_element(30)

        browsing.just_fyi("Check refresh button")
        browsing.open_tabs_button.click()
        browsing.empty_tab_button.click()
        url = 'app.uniswap.org'
        element_on_start_page = dapp.element_by_text('Select a token')
        web_page = dapp.open_url(url)
        dapp.allow_button.click()
        element_on_start_page.scroll_and_click()

        # when bottom sheet is opened, elements by text couldn't be found
        element_on_start_page.wait_for_invisibility_of_element(20)
        web_page.browser_refresh_page_button.click()

        if not element_on_start_page.is_element_displayed(30):
            self.driver.fail("Page failed to be refreshed")

    @marks.testrail_id(5424)
    @marks.medium
    def test_open_url_with_non_english_text_connect_revoke_wallet_new_tab_open_chat_options(self):
        home = SignInView(self.driver).create_user()
        web_view = home.dapp_tab_button.click()
        browsing = web_view.open_url('www.wikipedia.org')
        wiki_texts = ['Español', '日本語', 'Français', '中文', 'Português']
        for wiki_text in wiki_texts:
            if not browsing.element_by_text_part(wiki_text).is_element_displayed(15):
                self.errors.append("%s is not shown" % wiki_text)

        web_view.just_fyi("Check that can connect wallet and revoke access")
        browsing.options_button.click()
        browsing.connect_account_button.click()
        browsing.allow_button.click()
        browsing.options_button.click()
        if not browsing.connected_account_button.is_element_displayed():
            self.driver.fail("Account is not connected")
        browsing.click_system_back_button()
        profile = browsing.profile_button.click()
        profile.privacy_and_security_button.click()
        profile.dapp_permissions_button.click()
        if not profile.element_by_text('wikipedia.org').is_element_displayed():
            self.errors.append("Permissions are not granted")
        profile.dapp_tab_button.click(desired_element_text=wiki_texts[0])
        browsing.options_button.click()
        browsing.connected_account_button.click()
        browsing.element_by_translation_id("revoke-access").click()
        browsing.options_button.click()
        if not browsing.connect_account_button.is_element_displayed():
            self.errors.append("Permission for account is not removed if using 'Revoke access' from dapp view")
        browsing.click_system_back_button()
        browsing.profile_button.click(desired_element_text='DApp permissions')
        if profile.element_by_text('wikipedia.org').is_element_displayed():
            self.errors.append("Permissions are not revoked")

        web_view.just_fyi("Check that can open chat view and send some message")
        profile.dapp_tab_button.click(desired_element_text=wiki_texts[0])
        browsing.options_button.click()
        browsing.open_chat_from_dapp_button.click()
        public_chat = browsing.get_chat_view()
        if not public_chat.element_by_text('#wikipedia-org').is_element_displayed():
            self.driver.fail("No redirect to public chat")
        message = public_chat.get_random_message()
        public_chat.send_message(message)
        public_chat.dapp_tab_button.click(desired_element_text=wiki_texts[0])
        browsing.options_button.click()
        browsing.open_chat_from_dapp_button.click()
        if not public_chat.chat_element_by_text(message).is_element_displayed():
            self.errors.append("Messages are not shown if open dapp chat from view")

        web_view.just_fyi("Check that can open new tab using 'New tab' from bottom sheet")
        profile.dapp_tab_button.click(desired_element_text=wiki_texts[0])
        browsing.options_button.click()
        browsing.new_tab_button.click()
        if not browsing.element_by_translation_id("open-dapp-store").is_element_displayed():
            self.errors.append("Was not redirected to home dapp store view using New tab")

        self.errors.verify_no_errors()

    # TODO: waiting mode (rechecked 23.11.21, valid)
    @marks.testrail_id(6300)
    @marks.skip
    @marks.medium
    def test_webview_security(self):
        home_view = SignInView(self.driver).create_user()
        daap_view = home_view.dapp_tab_button.click()

        browsing_view = daap_view.open_url('https://simpledapp.status.im/webviewtest/url-spoof-ssl.html')
        browsing_view.url_edit_box_lock_icon.click()
        if not browsing_view.element_by_translation_id("browser-not-secure").is_element_displayed():
            self.errors.append("Broken certificate displayed as secure connection \n")

        browsing_view.cross_icon.click()
        daap_view.open_url('https://simpledapp.status.im/webviewtest/webviewtest.html')
        browsing_view.element_by_text_part('204').click()
        if browsing_view.element_by_text_part('google.com').is_element_displayed():
            self.errors.append("URL changed on attempt to redirect to no-content page \n")

        browsing_view.cross_icon.click()
        daap_view.open_url('https://simpledapp.status.im/webviewtest/webviewtest.html')
        browsing_view.element_by_text_part('XSS check').click()
        browsing_view.open_in_status_button.click()
        if browsing_view.element_by_text_part('simpledapp.status.im').is_element_displayed():
            self.errors.append("XSS attemp succedded \n")
            browsing_view.ok_button.click()

        browsing_view.cross_icon.click()
        daap_view.open_url('https://simpledapp.status.im/webviewtest/url-blank.html')
        if daap_view.edit_url_editbox.text == '':
            self.errors.append("Blank URL value. Must show the actual URL \n")

        browsing_view.cross_icon.click()
        daap_view.open_url('https://simpledapp.status.im/webviewtest/port-timeout.html')
        # wait up  ~2.5 mins for port time out
        if daap_view.element_by_text_part('example.com').is_element_displayed(150):
            self.errors.append("URL spoof due to port timeout \n")

        self.errors.verify_no_errors()

    @marks.testrail_id(5456)
    @marks.medium
    def test_can_access_images_by_link(self):
        urls = {
            'https://cdn.dribbble.com/users/45534/screenshots/3142450/logo_dribbble.png':
                'url1.png',
            'https://steemitimages.com/DQmYEjeBuAKVRa3b3ZqwLicSHaPUm7WFtQqohGaZdA9ghjx/images%20(4).jpeg':
                'url3.png'
        }
        sign_in_view = SignInView(self.driver)
        home_view = sign_in_view.create_user()
        dapp_view = home_view.dapp_tab_button.click()
        from views.web_views.base_web_view import BaseWebView
        base_web = BaseWebView(self.driver)
        for url in urls:
            self.driver.set_clipboard_text(url)
            dapp_view.enter_url_editbox.click()
            dapp_view.paste_text()
            dapp_view.confirm()
            base_web.wait_for_d_aap_to_load(20)
            if dapp_view.web_page.is_element_differs_from_template(urls[url], 5):
                self.errors.append('Web page does not match expected template %s' % urls[url])
            base_web.browser_previous_page_button.click_until_presence_of_element(dapp_view.enter_url_editbox)
        self.errors.verify_no_errors()
