# coding=utf-8
import time
import random
import requests
import pandas as pd
from requests.exceptions import RequestException
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import WebDriverException

def get_one_page(url):
    try:
        response = requests.get(url)
        response.encoding = 'gbk'
        if response.status_code == 200:
            return response.text
        print('requests error')
        return None
    except RequestException:
        return None


class spider_TB:
    def __init__(self, start_page, end_page):
        self.login_url = 'https://login.taobao.com/member/login.jhtml'
        self.user = ''
        self.pwd = ''
        self.search_key = '手机'
        self.result_path = '../data/tb.csv'
        self.start_page = start_page
        self.end_page = end_page

        options = webdriver.ChromeOptions()
        # options.add_argument('headless')
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        # options.add_experimental_option('prefs', {'profile.managed_default_content_settings.images': 2}) 
        
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 60)

        self.login()
        self.search()
        self.parse()
        
        self.driver.quit()

    def wait_css(self, css):
        return self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, css)))

    def clean(self, s):
        return s.replace('&nbsp;', '')

    def update_detail(self, detail, left, right):
        if '型号' in left:
            detail['型号'] = self.clean(right)
        elif '品牌' in left and 'CPU' not in left:
            detail['品牌'] = self.clean(right)
        elif '内存' in left:
            detail['运行内存'] = self.clean(right)
        elif '容量' in left:
            detail['机身存储'] = self.clean(right)

    def get_detail(self, html):
        is_taobao = 1 if 'taobao' in self.driver.current_url else 0
        detail = {}
        if is_taobao:
            flag = True
            try:
                ps = self.driver.find_elements_by_css_selector('.tb-attributes-list > li > p')
                for p in ps:
                    lst = str(p.text).split(':')
                    if len(lst) != 2:
                        continue
                    left, right = lst
                    self.update_detail(detail, left, right.strip())
            except NoSuchElementException:
                flag = False
            
            if not flag:
                try:
                    lis = self.driver.find_element_by_css_selector('.attributes-list > li')
                    for li in lis:
                        lst = str(li.text).split(':')
                        if len(lst) != 2:
                            continue
                        left, right = lst
                        self.update_detail(detail, left, right.strip())
                except NoSuchElementException:
                    pass
        else:
            self.wait_css('#J_Detail > .J_DetailSection tr')
            trs = self.driver.find_elements_by_css_selector('#J_Detail > .J_DetailSection tr')
            for tr in trs:
                try:
                    ths = tr.find_elements_by_css_selector('th')
                    tds = tr.find_elements_by_css_selector('td')
                    for td in tds:
                        right = td.get_attribute('innerHTML')
                    for th in ths:
                        left = th.get_attribute('innerHTML')
                        self.update_detail(detail, left, right)
                except NoSuchElementException:
                    continue
        return detail

    def login(self):
        self.driver.get(self.login_url)
        
        pwd_login = self.wait_css('.qrcode-login > .login-links > .forget-pwd')
        pwd_login.click()
        time.sleep(random.randint(3, 7))

        weibo_login = self.wait_css('.weibo-login')
        weibo_login.click()
        time.sleep(random.randint(3, 7))

        user = self.wait_css('.username > .W_input')
        user.send_keys(self.user)
        time.sleep(random.randint(3, 7))

        pwd = self.wait_css('.password > .W_input')
        pwd.send_keys(self.pwd)
        time.sleep(random.randint(3, 7))

        submit = self.wait_css('.btn_tip > a > span')
        submit.click()
        time.sleep(random.randint(3, 7))

        self.wait_css('.site-nav-bd > ul.site-nav-bd-l > li#J_SiteNavLogin > div.site-nav-menu-hd > div.site-nav-user > a.site-nav-login-info-nick ')
        print('login successfully!')
        
    def search(self):
        input = self.wait_css('.search-combobox-input')
        input.send_keys(self.search_key)
        time.sleep(random.randint(3, 7))

        search = self.wait_css('.btn-search')
        search.click()
        time.sleep(random.randint(3, 7))

        sorts = self.driver.find_elements_by_css_selector('.sorts > .sort > .J_Ajax')
        for sort in sorts:
            if '销量' in sort.get_attribute('innerHTML'):
                sort.click()
                time.sleep(random.randint(3, 7))
                self.driver.refresh()
                break

    def save_checkpoint(self, index, result):
        df_cur = pd.DataFrame(result)
        if df_cur.shape[1] != 6:
            return False
        if index > 1:
            df_old = pd.read_csv(self.result_path, usecols=[1,2,3,4,5,6])
            df = pd.concat([df_old, df_cur])
            df.to_csv(self.result_path)
        else:
            df = df_cur
            df.to_csv(self.result_path)
        print('page', index, 'has been finished.')
        return True

    def parse(self):
        cnt = 0
        handle = self.driver.current_window_handle
        if self.start_page != 1:
            self.driver.execute_script('window.scrollTo(0, document.body.scrollHeight)')
            time.sleep(random.randint(3, 7))
            self.driver.execute_script('window.scrollTo(0, 0)')
        for page in range(self.start_page, self.end_page + 1):
            result = []
            if page > 1:
                input = self.wait_css('.J_Input')
                input.clear()
                input.send_keys(page)
                time.sleep(random.randint(3, 7))
                submit = self.wait_css('.J_Submit')
                submit.click()
                # self.driver.refresh()
                time.sleep(random.randint(5, 10))

            self.wait_css('.J_MouserOnverReq')
            items = self.driver.find_elements_by_css_selector('.J_MouserOnverReq')
            for item in items:
                price = item.find_element_by_css_selector('.price > strong').text
                deal = item.find_element_by_css_selector('.deal-cnt').text
                url = item.find_element_by_css_selector('.row-2 > .J_ClickStat')
                url.click()

                handles = self.driver.window_handles
                for i in handles:
                    if i != handle:
                        self.driver.switch_to.window(i)
                        try:
                            detail = self.get_detail(self.driver.page_source)
                        except WebDriverException:
                            detail = {}
                        self.driver.close()
                        self.driver.switch_to.window(handle)

                info = {
                    '价格': price,
                    '销量': deal
                }
                info.update(detail)

                cnt = cnt + 1
                print(page, cnt, info)
                result.append(info)
                time.sleep(random.randint(3, 7))

            if not self.save_checkpoint(page, result):
                print('failed on page', page)
                break  


class spider_JD:
    def __init__(self, start_page, end_page):
        self.start_page = start_page
        self.end_page = end_page
        self.url = 'https://www.jd.com/'
        self.result_path = '../data/jd.csv'

        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_experimental_option('prefs', {'profile.managed_default_content_settings.images': 2}) 
        
        self.driver = webdriver.Chrome(options=options)
        self.driver.implicitly_wait(60)
        self.wait = WebDriverWait(self.driver, 60)

        self.driver.get(self.url)
        self.search()
        self.parse()
        
        self.driver.quit()

    def wait_css(self, css):
        return self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, css)))

    def search(self):
        input = self.wait_css('input.text')
        input.send_keys('手机')

        submit = self.wait_css('button.button')
        submit.click()

        self.wait_css('.f-sort .fs-tit')
        sorts = self.driver.find_elements_by_css_selector('.f-sort .fs-tit')
        for sort in sorts:
            if '评论数' in sort.get_attribute('innerHTML'):
                sort.click()                
                self.driver.refresh()
                break

    def get_detail(self, url):
        html = get_one_page(url)
        detail = {}
        if html is None:
            return detail
        soup = BeautifulSoup(html, 'html.parser')
        infos = soup.select('#detail .clearfix')
        for info in infos:
            try:
                dt = info.select('dt')[0].string
                dd = info.select('dd')[0].string
                if '产品名称' in dt:
                    detail['产品名称'] = dd
                elif '品牌' in dt and 'CPU' not in dt:
                    detail['品牌'] = dd
                elif '机身存储' in dt:
                    detail['机身存储'] = dd
                elif '运行内存' in dt:
                    detail['运行内存'] = dd
            except IndexError:
                continue
        return detail
    
    def save_checkpoint(self, index, result):
        df_cur = pd.DataFrame(result)
        if df_cur.shape[1] != 6:
            return False
        if index > 1:
            df_old = pd.read_csv(self.result_path, usecols=[1,2,3,4,5,6])
            df = pd.concat([df_old, df_cur])
            df.to_csv(self.result_path)
        else:
            df = df_cur
            df.to_csv(self.result_path)
        print('page', index, 'has been finished.')
        return True

    def parse(self):
        cnt = 0
        for page in range(self.start_page, self.end_page + 1):
            result = []
            if page > 1:
                input = self.wait_css('.p-skip > .input-txt')
                input.clear()
                input.send_keys(page)
                submit = self.wait_css('.p-skip > .btn')
                submit.click()
                self.driver.refresh()
                time.sleep(random.randint(3, 7))

            self.driver.execute_script('window.scrollTo(0, document.body.scrollHeight)')
            time.sleep(3)
            self.driver.execute_script('window.scrollTo(0, document.body.scrollHeight)')
            time.sleep(3)
            self.driver.execute_script('window.scrollTo(0, 0)')

            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            items = soup.select('.gl-item')
            for item in items:
                price = item.select('.p-price > strong > i')[0].string
                deal = item.select('.p-commit > strong > a')[0].string
                url = item.select('.p-name > a')[0]['href']
                if 'https:' not in url:
                    url = 'https:' + url
                detail = self.get_detail(url)

                info = {
                    '价格': price,
                    '销量': deal
                }
                info.update(detail)

                cnt = cnt + 1
                print(page, cnt, info)
                result.append(info)  
                time.sleep(1)  

            if not self.save_checkpoint(page, result):
                print('failed on page', page)
                break


if __name__ == '__main__':
    spider_tb = spider_TB(1, 2)
    # spider_jd = spider_JD(1, 59)