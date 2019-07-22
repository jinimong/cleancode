import os

from django.test import LiveServerTestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


class NewVisitiorTest(StaticLiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        staging_server = os.environ.get('STAGING_SERVER')
        if staging_server:
            cls.server_url = 'http://{}'.format(staging_server)
            cls.live_server_url = ''
            return
        super().setUpClass()
        cls.server_url = cls.live_server_url


    @classmethod
    def tearDownClass(cls):
        if cls.server_url == cls.live_server_url:
            super().tearDownClass()

    
    def setUp(self):
        self.browser = webdriver.Chrome('chromedriver')
        self.browser.implicitly_wait(3)


    def tearDown(self):
        self.browser.quit()


    def check_for_row_in_list_table(self, row_text):
        table = self.browser.find_element_by_id('id_list_table')
        rows = table.find_elements_by_tag_name('tr')
        self.assertIn(row_text, [row.text for row in rows])


    def test_can_start_a_list_and_retrieve_it_later(self):
        self.browser.get(self.server_url)

        # To-Do 입력 텍스트 상자 체크
        inputbox = self.browser.find_element_by_id('id_new_item')
        self.assertEqual(
            inputbox.get_attribute('placeholder'),
            '작업 아이템 입력')

        # 사용자 - edith
        # 엔터키를 누르면 새로운 URL로 바뀐다. 그리고 작업 목록에
        # "1: 공작깃털 사기" 아이템이 추가된다.
        inputbox.send_keys('공작깃털 사기')
        inputbox.send_keys(Keys.ENTER)
        self.check_for_row_in_list_table('1: 공작깃털 사기')
        
        # 에디스의 전용 URL 을 얻는다.
        edith_list_url = self.browser.current_url
        self.assertRegex(edith_list_url, '/lists/.+')

        # 추가 아이템을 입력할 수 있는 텍스트 상자가 아직 존재한다.
        inputbox = self.browser.find_element_by_id('id_new_item')
        # "2: 공작깃털을 이용해서 그물 만들기" 아이템이 추가된다.
        inputbox.send_keys('공작깃털을 이용해서 그물 만들기')
        inputbox.send_keys(Keys.ENTER)
        self.check_for_row_in_list_table('2: 공작깃털을 이용해서 그물 만들기')
        self.check_for_row_in_list_table('1: 공작깃털 사기')

        # 사용자 - francis
        # 새로운 사용자 프란시스가 사이트에 접속한다.
        ## 새로운 브라우저 세션을 이용해서 에디스의 정보가
        ## 쿠키를 통해 유입되는 것을 방지한다.
        self.browser.quit()
        self.browser = webdriver.Chrome('chromedriver')

        # 프란시스가 홈페이지에 접속한다.
        # 에디스의 리스트는 보이지 않는다.
        self.browser.get(self.server_url)
        page_text = self.browser.find_element_by_tag_name('body').text
        self.assertNotIn('공작깃털 사기', page_text)
        self.assertNotIn('그물 만들기', page_text)

        # 프란시스의 To-Do 입력
        inputbox = self.browser.find_element_by_id('id_new_item')
        inputbox.send_keys('우유 사기')
        inputbox.send_keys(Keys.ENTER)

        # 프란시스의 전용 URL 을 얻는다.
        francis_list_url = self.browser.current_url
        self.assertRegex(francis_list_url, '/lists/.+')
        self.assertNotEqual(francis_list_url, edith_list_url)

        # 에디스의 입력 흔적이 없음을 재확인
        page_text = self.browser.find_element_by_tag_name('body').text
        self.assertNotIn('공작깃털 사기', page_text)
        self.assertIn('우유 사기', page_text)


    def test_layout_and_styling(self):
        # 에디스는 메인페이지를 방문한다
        self.browser.get(self.server_url)
        self.browser.set_window_size(1024, 768)

        # 에디스는 입력상자가 가운데 배치된 것을 본다
        inputbox = self.browser.find_element_by_id('id_new_item')
        self.assertAlmostEqual(
            inputbox.location['x'] + inputbox.size['width'] / 2,
            512,
            delta=10
        )

        # 에디스는 새로운 리스트를 시작하고 입력상자가
        # 가운데 배치된 것을 확인한다
        inputbox.send_keys('testing\n')
        inputbox = self.browser.find_element_by_id('id_new_item')
        self.assertAlmostEqual(
            inputbox.location['x'] + inputbox.size['width'] / 2,
            512,
            delta=10
        )
