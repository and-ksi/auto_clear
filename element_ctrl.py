# "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=11248 --user-data-dir="D:\file\python\selenium_chrome"

import re
import time
import tkinter as tk
import requests

from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
# from selenium.common.exceptions import NoSuchElementException

from data_file import Log_save
from data_file import Post_Message
from data_file import ZZData
from data_file import ConfigManager

debug_port = 11248
usr_dir = "user-data-dir=D:\\file\\python\\chrome-win64"
work_url = "https://zz-dealer.bydauto.com.cn"
# work_url = "https://zz-dealer.bydauto.com.cn/#/login"
end_time = 18
visiable_value = 1


# error_time = 100 : 到达当天清洗结束时间
# error_time = 0 : 可以忽略的错误 \\ 无错误
# error_time = 101 : 直接结束程序并且把错误上报

class element_operate:
    def __init__(self):
        # debug
        self.log = Log_save()
        self.driver = None
        self.timeout = 6
        self.step = 0
        self.error_time = 0
        self.error = Post_Message()
        self.manager = None
        self.passager = None
        self.phone = ""
        self.error_log_text = None
        pass

    def work_flow(self):
        try:
            self.log.start_log()
            self.error_time = 0
            self.open_new_web(visible=visiable_value)
            self.check_clue_loop()
        finally:
            if self.error_time:
                self.error.error_alart(message=f"程序运行出错，error_time = {self.error_time}.详情查看log文件。")
                if visiable_value:
                    # 切换为有头模式
                    self.driver.execute_cdp_cmd("Browser.setWindowBounds", {
                        "windowId": self.driver.window_handles[0],
                        "bounds": {
                            "width": 1920,
                            "height": 1080
                        }
                    })
                    self.driver.execute_cdp_cmd("Browser.setWindowVisible", {
                        "visible": True
                    })
                exit()
                pass

    def check_clue_loop(self):
        self.step = 2
        while time.time() < get_today_18_timestamp(4):
            self.click_on_head(2)
            self.click_on_subhead(2)
            while time.time() < get_today_18_timestamp(4):
                mark = 0
                self.click_on_radio_button(6)
                start_time = time.time()
                while mark == self.check_item_count():
                    if time.time() - start_time > self.timeout:
                        self.driver.refresh()
                        self.click_on_radio_button(6)
                        start_time = time.time()
                    time.sleep(0.5)
                mark = self.check_item_count()
                self.click_on_radio_button(2)
                start_time = time.time()
                while mark == self.check_item_count():
                    if time.time() - start_time > self.timeout:
                        self.driver.refresh()
                        self.click_on_radio_button(2)
                        start_time = time.time()
                    time.sleep(0.5)
                mark = self.check_item_count()
                if mark > 0:
                    self.clue_distribute()
                    self.clue_follow()
                    self.click_on_head(2)
                    self.click_on_subhead(2)
                # 检查待清洗
                mark = 0
                self.click_on_radio_button(6)
                start_time = time.time()
                while mark == self.check_item_count():
                    if time.time() - start_time > self.timeout:
                        self.driver.refresh()
                        self.click_on_radio_button(6)
                        start_time = time.time()
                    time.sleep(0.5)
                mark = self.check_item_count()
                self.click_on_radio_button(1)
                start_time = time.time()
                while mark == self.check_item_count():
                    if time.time() - start_time > self.timeout:
                        self.driver.refresh()
                        self.click_on_radio_button(1)
                        start_time = time.time()
                    time.sleep(0.5)
                mark = self.check_item_count()
                if mark > 0:
                    self.clue_clear()

        pass

    def __disable_check_clue_loop(self):
        self.step = 2
        self.click_on_head(2)
        self.click_on_subhead(2)
        while True:
            # 检查待分配
            mark = 0
            self.click_on_radio_button(6)
            start_time = time.time()
            while mark == self.check_item_count():
                if time.time() - start_time > self.timeout:
                    self.driver.refresh()
                    self.click_on_radio_button(6)
                    start_time = time.time()
                time.sleep(0.5)
            mark = self.check_item_count()
            self.click_on_radio_button(2)
            start_time = time.time()
            while mark == self.check_item_count():
                if time.time() - start_time > self.timeout:
                    self.driver.refresh()
                    self.click_on_radio_button(2)
                    start_time = time.time()
                time.sleep(0.5)
            mark = self.check_item_count()
            if mark > 0:
                self.clue_distribute()
                self.clue_follow()
                self.click_on_head(2)
                self.click_on_subhead(2)
            # 检查待清洗
            mark = 0
            self.click_on_radio_button(6)
            start_time = time.time()
            while mark == self.check_item_count():
                if time.time() - start_time > self.timeout:
                    self.driver.refresh()
                    self.click_on_radio_button(6)
                    start_time = time.time()
                time.sleep(0.5)
            mark = self.check_item_count()
            self.click_on_radio_button(1)
            start_time = time.time()
            while mark == self.check_item_count():
                if time.time() - start_time > self.timeout:
                    self.driver.refresh()
                    self.click_on_radio_button(1)
                    start_time = time.time()
                time.sleep(0.5)
            mark = self.check_item_count()
            if mark > 0:
                self.clue_clear()
        pass

    def clue_follow(self, max_retries=2):
        retries = 0
        self.step = 5
        while retries < max_retries:
            try:
                self.click_on_head(2)
                self.click_on_subhead(1)

                start_time = time.time()
                while not self.check_item_count():
                    time.sleep(0.5)
                    # test = time.time() - start_time
                    # error_text = f"线索跟进页面数字提取失败一次。{test} = {time.time()} - {start_time}"
                    # self.log.log_message(error_text, 1)
                    if time.time() - start_time > self.timeout:
                        error_text = f"线索跟进页面刷新失败"
                        self.log.log_message(error_text, 4)
                        self.error_time = 101
                        raise Exception("操作失败")

                xpath_expression = f"//*[contains(@class, 'click_link') and contains(text(), '{self.phone}')]"
                element = self.try_find_element(xpath_expression)
                self.try_click_element(element)

                # xpath_exp = "//button[contains(@class, 'el-button') and contains(@class, 'filter-item') and contains(@class, 'el-button--text') and contains(@class, 'el-button--medium') and span[text()='跟进']]"
                xpath_exp = "//button[contains(@class, 'el-button filter-item el-button--text el-button--medium') and .//span[text()='跟进']]"
                element = self.try_find_clickable_element(xpath_exp)
                self.try_click_element(element)
                xpath_exp = "//div[contains(@class, 'el-dialog') and not(contains(@style, 'display: none;')) and contains(@aria-label, '完成跟进')]"
                correct_label = self.try_find_element(xpath_exp)
                xpath_exp = "//span[contains(@class, 'el-radio-button__inner') and text()='邀约到店']"
                element_ways = self.try_find_element_from(correct_label, xpath_exp)
                self.try_click_element(element_ways)

                # "//textarea[@placeholder='请输入备注内容']"
                texture = "线索清洗au"
                xpath_exp = "//textarea[@placeholder='请输入备注内容']"
                textarea = self.try_find_element_from(correct_label, xpath_exp)
                textarea.clear()
                textarea.send_keys(texture)
                xpath_exp = ".//span[contains(text(), '确定')]"
                element = self.try_find_element_from(correct_label, xpath_exp)
                self.try_click_element(element)

                # xpath_exp = ".//div[contains(@class, 'el-message-box__wrapper') and contains(@aria-label, '提示')]"
                # element_sure = self.try_find_element(xpath_exp)
                # xpath_exp = ".//span[contains(text(), '确定')]"
                # # xpath_exp = "//button[span[text()='确定']]"
                # element = self.try_find_element_from(element_sure, xpath_exp)
                # self.click_element(element)
                self.log.log_message(f"success clue_follow！\n______________________________________________")
                self.step = 2
                return
            except:
                error_text = f"线索跟进失效第{retries + 1}次，请及时跟进，客户：{self.passager}"
                self.log.log_message(error_text, 4)
                self.driver.refresh()  # 直接使用 driver.refresh()  刷新页面
                retries += 1
                time.sleep(1)
        self.error_time = 101
        raise Exception("操作失败，已达最大重试次数")
        pass

    def __disable_clue_follow(self):
        self.click_on_subhead(1)

        while not self.check_item_count():
            time.sleep(0.5)
        self.click_table_link(1)

        # xpath_exp = "//button[contains(@class, 'el-button') and contains(@class, 'filter-item') and contains(@class, 'el-button--text') and contains(@class, 'el-button--medium') and span[text()='跟进']]"
        xpath_exp = "//button[contains(@class, 'el-button filter-item el-button--text el-button--medium') and .//span[text()='跟进']]"
        element = self.try_find_clickable_element(xpath_exp)
        self.try_click_element(element)
        xpath_exp = "//div[contains(@class, 'el-dialog') and not(contains(@style, 'display: none;')) and contains(@aria-label, '完成跟进')]"
        correct_label = self.try_find_element(xpath_exp)
        xpath_exp = "//span[contains(@class, 'el-radio-button__inner') and text()='邀约到店']"
        element_ways = self.try_find_element_from(correct_label, xpath_exp)
        self.try_click_element(element_ways)

        # "//textarea[@placeholder='请输入备注内容']"
        texture = "线索清洗auto"
        xpath_exp = "//textarea[@placeholder='请输入备注内容']"
        textarea = self.try_find_element_from(correct_label, xpath_exp)
        textarea.clear()
        textarea.send_keys(texture)
        xpath_exp = ".//span[contains(text(), '确定')]"
        element = self.try_find_element_from(correct_label, xpath_exp)
        self.try_click_element(element)

        # xpath_exp = ".//div[contains(@class, 'el-message-box__wrapper') and contains(@aria-label, '提示')]"
        # element_sure = self.try_find_element(xpath_exp)
        # xpath_exp = ".//span[contains(text(), '确定')]"
        # # xpath_exp = "//button[span[text()='确定']]"
        # element = self.try_find_element_from(element_sure, xpath_exp)
        # self.click_element(element)
        self.log.log_message(f"success clue_follow！")

    def clue_distribute(self, max_retries=2):
        retries = 0
        while retries < max_retries:
            try:
                self.step = 4
                self.click_on_head(2)
                self.click_on_subhead(2)
                self.click_on_radio_button(2)

                start_time = time.time()
                while not self.check_item_count():
                    time.sleep(0.5)
                    if time.time() - start_time > self.timeout:
                        error_text = f"线索分配页面无数据"
                        self.log.log_message(error_text, 4)
                        self.error_time = 101
                        raise Exception("操作失败")

                self.log.log_message(f"start clue_distribute")
                table_link = self.click_table_link(1)
                name = table_link.text
                # name = "test debug"
                self.passager = name
                pattern = r'-(\d+)$'
                # 使用正则表达式匹配
                match = re.search(pattern, name)
                self.phone = match.group(1)

                log_text = f"准备线索分配：{name}"
                self.log.log_message(log_text)
                # xpath_exp = "//div[contains(@class, 'el-dialog') and contains(@aria-label, '线索详情')]"
                # trouble: 这里可能有问题1
                xpath_exp = "//div[contains(@class, 'el-dialog') and not(contains(@style, 'display: none;')) and .//span[text()='线索详情']]"
                correct_label = self.try_find_element(xpath_exp)
                # xpath_exp = ".//div[contains(@class, 'el-select') and contains(@class, 'el-select--mini') and contains(text(), '选择客户经理')]"
                xpath_exp = ".//input[contains(@placeholder, '选择客户经理')]"
                element = self.try_find_element_from(correct_label, xpath_exp)
                self.try_click_element(element)

                xpath_exp = ".//div[contains(@class, 'el-select-dropdown el-popper') and not(contains(@style, 'display: none;'))]"
                ele_mo_dropdown = self.try_find_element(xpath_exp)
                xpath_exp = ".//li[contains(@class, 'el-select-dropdown__item')]"
                ele_dropdowns = self.try_find_elements_from(ele_mo_dropdown, xpath_exp)

                while ele_dropdowns[0].text == "":
                    time.sleep(0.1)
                config = ConfigManager()
                name_list_mid = config.get_all_names()
                self.log.log_message(f"name_list_mid = {name_list_mid}", 1)
                name_list = []

                for index, element_sub in enumerate(ele_dropdowns):
                    text = element_sub.text
                    name_match = re.search(r'[\u4e00-\u9fff]+', text)
                    number_match = re.search(r'\d+', text)
                    self.log.log_message(f"text = {text}, name_match = {name_match}, number_match = {number_match}", 1)
                    if name_match and number_match:
                        name = name_match.group()
                        number = int(number_match.group())
                        # 查找名字是否在二维数组中
                        for entry in name_list_mid:
                            self.log.log_message(f"entry = {entry}, name = {name}, number = {number}", 1)
                            if entry[0] == name:
                                # 计算数字之和并新建一个数组
                                name_list.append([name, entry[1] + number, index])
                                print(f"新数组: {name_list}")
                                break
                    else:
                        self.log.log_message("Nod find name and number from total number.", 4)

                log_text = f"name_list_mid = {name_list_mid}; name_list = {name_list}"
                self.log.log_message(log_text, 1)

                min_num = 999999
                min_index = -1
                min_name = ""
                for min_name in name_list:
                    if min_name[1] < min_num:
                        min_num = min_name[1]
                        min_index = min_name[2]
                for sub_name in name_list_mid:
                    if len(sub_name) > 0 and sub_name[0] == min_name[0]:
                        min_num = -1
                        break

                if min_num < 0:
                    self.try_click_element(ele_dropdowns[min_index])
                else:
                    self.error.error_alart("min_num < 0")

                # 添加数据到数据库中

                texture = "线索清洗au"
                xpath_exp = "//textarea[@placeholder='请输入备注内容']"
                textarea = self.try_find_element_from(correct_label, xpath_exp)
                textarea.clear()
                textarea.send_keys(texture)
                # 点击确定，确定，未验证
                xpath_exp = ".//span[contains(text(), '确定')]"
                element = self.try_find_element_from(correct_label, xpath_exp)
                self.try_click_element(element)
                xpath_exp = ".//div[contains(@class, 'el-message-box__wrapper') and contains(@aria-label, '提示')]"
                element_sure = self.try_find_element(xpath_exp)
                xpath_exp = ".//span[contains(text(), '确定')]"
                # xpath_exp = "//button[span[text()='确定']]"
                element = self.try_find_element_from(element_sure, xpath_exp)
                self.try_click_element(element)
                self.log.log_message(f"success clue_clear！{name}")
                return
            except:
                self.log.log_message(f"线索分配第{retries + 1}次重试...", 4)
                self.driver.refresh()  # 直接使用 driver.refresh()  刷新页面
                retries += 1
                time.sleep(1)
        self.error_time = 101
        raise Exception("操作失败，已达最大重试次数")
        pass

    def __disable_clue_distribute(self):
        self.step = 4
        self.log.log_message(f"start clue_distribute")
        table_link = self.click_table_link(1)
        name = table_link.text
        # name = "test debug"
        log_text = f"准备线索分配：{name}"
        self.log.log_message(log_text)
        # xpath_exp = "//div[contains(@class, 'el-dialog') and contains(@aria-label, '线索详情')]"
        # trouble: 这里可能有问题1
        xpath_exp = "//div[contains(@class, 'el-dialog') and not(contains(@style, 'display: none;')) and .//span[text()='线索详情']]"
        correct_label = self.try_find_element(xpath_exp)
        # xpath_exp = ".//div[contains(@class, 'el-select') and contains(@class, 'el-select--mini') and contains(text(), '选择客户经理')]"
        xpath_exp = ".//input[contains(@placeholder, '选择客户经理')]"
        element = self.try_find_element_from(correct_label, xpath_exp)
        self.try_click_element(element)

        xpath_exp = ".//div[contains(@class, 'el-select-dropdown el-popper') and not(contains(@style, 'display: none;'))]"
        ele_mo_dropdown = self.try_find_element(xpath_exp)
        xpath_exp = ".//li[contains(@class, 'el-select-dropdown__item')]"
        ele_dropdowns = self.try_find_elements_from(ele_mo_dropdown, xpath_exp)
        # 一种成功的查找方法，备用
        # xpath_exp = ".//div[contains(@class, 'el-select-dropdown') and contains(@class, 'el-popper')]"
        # element_seles = self.try_find_elements(xpath_exp)
        # element_sele = element_seles[-1]
        # xpath_exp = ".//li[contains(@class, 'el-select-dropdown__item')]"
        # ele_dropdowns = self.try_find_elements_from(element_sele, xpath_exp)
        while ele_dropdowns[0].text == "":
            time.sleep(0.1)
        config = ConfigManager()
        name_list_mid = config.get_all_names()
        self.log.log_message(f"name_list_mid = {name_list_mid}")
        name_list = []

        for index, element_sub in enumerate(ele_dropdowns):
            text = element_sub.text
            name_match = re.search(r'[\u4e00-\u9fff]+', text)
            number_match = re.search(r'\d+', text)
            self.log.log_message(f"text = {text}, name_match = {name_match}, number_match = {number_match}", 1)
            if name_match and number_match:
                name = name_match.group()
                number = int(number_match.group())
                # 查找名字是否在二维数组中
                for entry in name_list_mid:
                    self.log.log_message(f"entry = {entry}, name = {name}, number = {number}", 1)
                    if entry[0] == name:
                        # 计算数字之和并新建一个数组
                        name_list.append([name, entry[1] + number, index])
                        print(f"新数组: {name_list}")
                        break
            else:
                self.log.log_message("Nod find name and number from total number.", 4)

        log_text = f"name_list_mid = {name_list_mid}; name_list = {name_list}"
        self.log.log_message(log_text)

        min_num = 999999
        min_index = -1
        min_name = ""
        for min_name in name_list:
            if min_name[1] < min_num:
                min_num = min_name[1]
                min_index = min_name[2]
        for sub_name in name_list_mid:
            if len(sub_name) > 0 and sub_name[0] == min_name[0]:
                min_num = -1
                break

        if min_num < 0:
            self.try_click_element(ele_dropdowns[min_index])
        else:
            self.error.error_alart("min_num < 0")

        # 添加数据到数据库中

        texture = "线索清洗auto"
        xpath_exp = "//textarea[@placeholder='请输入备注内容']"
        textarea = self.try_find_element_from(correct_label, xpath_exp)
        textarea.clear()
        textarea.send_keys(texture)
        # 点击确定，确定，未验证
        xpath_exp = ".//span[contains(text(), '确定')]"
        element = self.try_find_element_from(correct_label, xpath_exp)
        self.try_click_element(element)
        xpath_exp = ".//div[contains(@class, 'el-message-box__wrapper') and contains(@aria-label, '提示')]"
        element_sure = self.try_find_element(xpath_exp)
        xpath_exp = ".//span[contains(text(), '确定')]"
        # xpath_exp = "//button[span[text()='确定']]"
        element = self.try_find_element_from(element_sure, xpath_exp)
        self.try_click_element(element)
        self.log.log_message(f"success clue_clear！{name}")

        pass

    def test_clue_distribute(self):
        xpath_exp = "//div[contains(@class, 'el-dialog') and not(contains(@style, 'display: none;')) and .//span[text()='线索详情']]"
        correct_label = self.try_find_element(xpath_exp)
        # xpath_exp = ".//div[contains(@class, 'el-select') and contains(@class, 'el-select--mini') and contains(text(), '选择客户经理')]"
        xpath_exp = ".//input[contains(@placeholder, '选择客户经理')]"
        element = self.try_find_element_from(correct_label, xpath_exp)
        self.try_click_element(element)
        xpath_exp = ".//div[contains(@class, 'el-select-dropdown el-popper') and not(contains(@style, 'display: none;'))]"
        ele_mo_dropdown = self.try_find_element(xpath_exp)
        xpath_exp = ".//li[contains(@class, 'el-select-dropdown__item')]"
        ele_dropdowns = self.try_find_elements_from(ele_mo_dropdown, xpath_exp)
        self.try_click_element(ele_dropdowns[0])
        pass

    def clue_clear(self, max_retries=2):
        self.step = 3
        retries = 0
        log_text = f"准备清洗线索：____________________________________________"
        self.log.log_message(log_text)
        while retries < max_retries:
            try:
                self.click_on_head(2)
                self.click_on_subhead(2)

                start_time = time.time()
                while not self.check_item_count():
                    time.sleep(0.5)
                    if time.time() - start_time > self.timeout:
                        error_text = f"线索清洗页面无数据"
                        self.log.log_message(error_text, 4)
                        self.error_time = 101
                        raise Exception("操作失败")

                table_link = self.click_table_link(1)
                name = table_link.text
                log_text = f"准备清洗线索：{name}"
                self.log.log_message(log_text)

                xpath_exp = "//div[contains(@class, 'el-dialog__wrapper') and not(contains(@style, 'display: none;')) and .//span[text()='线索详情']]"
                correct_label = self.try_find_element(xpath_exp)

                # 线索时间判断
                now_time = self.read_label_in_table("线索创建时间")
                if convert_to_timestamp(now_time) >= get_today_18_timestamp():
                    self.error_time = 100
                    log_text = f"今日线索清洗完毕。"
                    self.log.log_message(log_text)
                    raise Exception(log_text)

                value = self.read_label_in_table("意向车系")
                self.log.log_message(f"意向车系value = {value}")
                if value == "" or value is None:
                    self.log.log_message(f"None of car choice")
                    xpath_exp = ".//i[contains(@class, 'el-select__caret') and contains(@class, 'el-input__icon') and contains(@class, 'el-icon-arrow-up')]"
                    # 按理说是可以点击了，但是需要确定一下
                    content = self.try_find_elements_from(correct_label, xpath_exp)
                    self.try_click_element(content[len(content) - 1])
                    # 点出选择菜单
                    # 选择好车系
                    # el-select-dropdown el-popper is-multiple
                    xpath_exp = ".//div[contains(@class, 'el-select-dropdown') and contains(@class, 'el-popper') and contains(@class, 'is-multiple') and not(contains(@style, 'display: none;'))]"
                    element_sele = self.try_find_element(xpath_exp)
                    # el-select-dropdown__item
                    xpath_exp = ".//li[contains(@class, 'el-select-dropdown__item')]"
                    ele = self.try_find_element_from(element_sele, xpath_exp)
                    self.try_click_element(ele)
                    pass
                texture = "线索清洗au"
                xpath_exp = "//textarea[@placeholder='请输入备注内容']"
                textarea = self.try_find_element_from(correct_label, xpath_exp)
                textarea.clear()
                textarea.send_keys(texture)
                xpath_exp = ".//span[contains(text(), '确定')]"
                element = self.try_find_clickable_element_from(correct_label, xpath_exp)
                self.try_click_element(element)
                xpath_exp = ".//div[contains(@class, 'el-message-box__wrapper') and contains(@aria-label, '提示')]"
                element_sure = self.try_find_clickable_element(xpath_exp)
                xpath_exp = ".//span[contains(text(), '确定')]"
                # xpath_exp = "//button[span[text()='确定']]"
                element = self.try_find_clickable_element_from(element_sure, xpath_exp)
                self.try_click_element(element)
                self.log.log_message(f"success clue_clear！{name}")

                return
            except:
                self.log.log_message(f"线索清洗第{retries + 1}次重试...", 4)
                self.driver.refresh()
                retries += 1
                time.sleep(1)
        self.error_time = 101
        raise Exception("操作失败，已达最大重试次数")
        pass

    def __disable_clue_clear(self):
        self.step = 3
        table_link = self.click_table_link(1)
        name = table_link.text
        log_text = f"准备清洗线索：{name}"
        self.log.log_message(log_text)
        xpath_exp = "//div[contains(@class, 'el-dialog__wrapper') and not(contains(@style, 'display: none;')) and .//span[text()='线索详情']]"
        correct_label = self.try_find_element(xpath_exp)

        value = self.read_label_in_table("意向车系")
        self.log.log_message(f"value = {value}")
        if value == "" or value is None:
            self.log.log_message(f"None of car choice")
            xpath_exp = ".//i[contains(@class, 'el-select__caret') and contains(@class, 'el-input__icon') and contains(@class, 'el-icon-arrow-up')]"
            # 按理说是可以点击了，但是需要确定一下
            content = self.try_find_elements_from(correct_label, xpath_exp)
            self.try_click_element(content[len(content) - 1])
            # 点出选择菜单
            # 选择好车系
            # el-select-dropdown el-popper is-multiple
            xpath_exp = ".//div[contains(@class, 'el-select-dropdown') and contains(@class, 'el-popper') and contains(@class, 'is-multiple') and not(contains(@style, 'display: none;'))]"
            element_sele = self.try_find_element(xpath_exp)
            # el-select-dropdown__item
            xpath_exp = ".//li[contains(@class, 'el-select-dropdown__item')]"
            ele = self.try_find_element_from(element_sele, xpath_exp)
            self.try_click_element(ele)
            pass
        texture = "线索清洗auto"
        xpath_exp = "//textarea[@placeholder='请输入备注内容']"
        textarea = self.try_find_element_from(correct_label, xpath_exp)
        textarea.clear()
        textarea.send_keys(texture)
        xpath_exp = ".//span[contains(text(), '确定')]"
        element = self.try_find_clickable_element_from(correct_label, xpath_exp)
        self.try_click_element(element)
        xpath_exp = ".//div[contains(@class, 'el-message-box__wrapper') and contains(@aria-label, '提示')]"
        element_sure = self.try_find_clickable_element(xpath_exp)
        xpath_exp = ".//span[contains(text(), '确定')]"
        # xpath_exp = "//button[span[text()='确定']]"
        element = self.try_find_clickable_element_from(element_sure, xpath_exp)
        self.try_click_element(element)
        self.log.log_message(f"success clue_clear！{name}")

    pass

    def test_clue_clear(self):
        xpath_exp = "//div[contains(@class, 'el-dialog__wrapper') and not(contains(@style, 'display: none;')) and .//span[text()='线索详情']]"
        # trouble: 不确定是哪个线索详情，似乎不一样
        correct_label = self.try_find_element(xpath_exp)

        xpath_exp = ".//i[contains(@class, 'el-select__caret') and contains(@class, 'el-input__icon') and contains(@class, 'el-icon-arrow-up')]"
        # 按理说是可以点击了，但是需要确定一下
        content = self.try_find_elements_from(correct_label, xpath_exp)
        self.try_click_element(content[len(content) - 1])
        # 点出选择菜单
        # 选择好车系
        # el-select-dropdown el-popper is-multiple
        xpath_exp = ".//div[contains(@class, 'el-select-dropdown') and contains(@class, 'el-popper') and contains(@class, 'is-multiple') and not(contains(@style, 'display: none;'))]"
        element_sele = self.try_find_element(xpath_exp)
        # el-select-dropdown__item
        xpath_exp = ".//li[contains(@class, 'el-select-dropdown__item')]"
        ele = self.try_find_element_from(element_sele, xpath_exp)
        self.try_click_element(ele)
        pass

    def read_label_in_table(self, label, count=0):
        self.log.log_message("start read_label_from_popup_safely!")
        # trouble: 不确定是哪个线索详情，似乎不一样
        xpath_exp = "//div[contains(@class, 'el-dialog') and not(contains(@style, 'display: none;')) and contains(@aria-label, '线索详情')]"
        table = self.try_find_element(xpath_exp)
        # "el-form-item form_item"
        xpath_exp = f".//div[contains(@class, 'el-form-item') and contains(@class, 'form_item') and .//label[contains(text(), '{label}')]]"
        element = self.try_find_element_from(table, xpath_exp)
        # el-form-item__content
        xpath_exp = ".//div[contains(@class, 'el-form-item__content')]"
        value = self.try_find_element_from(element, xpath_exp).text
        self.log.log_message(f"success read_label_from_popup_safely! label = {label}, value = {value}")
        return value

    def read_labels_in_table(self, title):
        self.log.log_message("ready to read_customer_in_table")
        st = []
        for label in title:
            value = self.read_label_in_table(f"{label}", 0)
            self.log.log_message(f"label = {label}, value = {value}")
            if value:
                st.append([label, value])
        self.log.log_message("success to read_customer_in_table")
        return st

    # 线索分配读取弹出表格内容
    def read_clue_clear_customer(self):
        title = ["姓名", "意向车系", "来源平台", "参与活动", "线索类别", "购车地区", "线索创建时间"]
        st = self.read_labels_in_table(title)
        phone = self.read_label_in_table("手机号")
        self.log.log_message(f"手机号 = {phone}")
        zdata = ZZData()
        self.log.log_message(f"st = {st}", 1)
        zdata.add_or_update_batch(phone, st)
        self.log.log_message(f"success read_clue_clear_customer")
        return phone

    def check_item_count(self):
        self.log.log_message(f"ready check_item_count", 1)
        # 查找元素并提取文本
        xpath_exp = "//span[@class='el-pagination__total']"
        element = self.try_find_element(xpath_exp)
        if element:
            text = element.text
            match = re.search(r'\d+', text)
            if match:
                self.log.log_message(f"success check_item_count : {int(match.group())}", 1)
                return int(match.group())
            else:
                error_text = "Match int error!"
                self.log.log_message(error_text, 4)
                self.error_time = 101
                raise Exception(error_text)
                # self.error.error_alart(message="Match int error!")
                # return None
            # print("提取到的文本：", text)
        else:
            error_text = "Not find paginatino__total!"
            self.log.log_message(error_text, 4)
            self.error_time = 101
            raise Exception(error_text)
            # self.error.error_alart(message="Not find paginatino__total!")
            # return None

    def click_table_link(self, key=0):
        debug_text = f"ready click_table_link {key}"
        self.log.log_message(debug_text, 1)
        xpath_expression = "//*[contains(@class, 'click_link')]"
        elements = self.try_find_elements(xpath_expression)
        length = len(elements)
        element = None
        if key == 0 and length > 2:
            # 点击线索详情时使用
            element = elements[length - 3]
            self.try_click_element(element)
        elif key > 0 and length > 0:
            element = elements[key - 1]
            self.try_click_element(element)
        else:
            error_text = f"Error for click_table_link! key = {key}"
            self.log.log_message(error_text, 4)
            self.error_time = 101
            raise Exception(error_text)
        debug_text = f"success click_table_link {key}"
        self.log.log_message(debug_text, 1)
        return element

    def click_on_radio_button(self, child):
        debug_text = f"ready click_on_radio_button {child}, step = {self.step}"
        self.log.log_message(debug_text, 1)
        if child == 1:
            keyword = "待清洗"
        elif child == 2:
            keyword = "待分配"
        elif child == 3:
            keyword = "有效"
        elif child == 4:
            keyword = "无效"
        elif child == 5:
            keyword = "未接通"
        elif child == 6:
            keyword = "全部"
        else:
            keyword = None
            error_text = f"Radio button keyword error!"
            self.log.log_message(error_text, 4)
            self.error_time = 101
            raise Exception(error_text)
        # //label[contains(@class, 'el-radio-button') and contains(@class, 'el-radio-button--small') and .//span[text()='待分配']]
        xpath_expression = f"//label[contains(@class, 'el-radio-button') and contains(@class, 'el-radio-button--small') and .//span[text()='{keyword}']]"
        element = self.try_find_clickable_element(xpath_expression)
        self.try_click_element(element)
        debug_text = f"success click_on_radio_button {child} = {keyword}"
        self.log.log_message(debug_text, 1)

    def click_on_subhead(self, child):
        debug_text = f"ready click_on_subhead {child}, in step {self.step}"
        self.log.log_message(debug_text, 1)
        if child == 1:
            keyword = "跟进任务"
        elif child == 2:
            keyword = "线索处理"
        else:
            keyword = None
            error_text = "Subhead keyword error!"
            self.log.log_message(error_text, 4)
            self.error_time = 101
            raise Exception(error_text)
        debug_text = f"ready click_on_subhead {keyword}"
        self.log.log_message(debug_text, 1)
        xpath_expression = f"//li[contains(@class, 'el-menu-item') and contains(text(), '{keyword}')]"
        element = self.try_find_clickable_element(xpath_expression)
        self.try_click_element(element)
        self.log.log_message(f"success click_on_subhead {child} = {keyword}", 1)

    def click_on_head(self, child):
        debug_text = f"ready click_on_head {child}, in step: {self.step}"
        self.log.log_message(debug_text, 1)
        if child == 1:
            keyword = "概览"
        elif child == 2:
            keyword = "工作任务"
        elif child == 3:
            keyword = "客户档案"
        else:
            keyword = None
            error_text = f"Head keyword error!"
            self.log.log_message(error_text, 4)
            self.error_time = 101
            raise Exception(error_text)
        debug_text = f"ready click_on_head {keyword}"
        self.log.log_message(debug_text, 1)
        # 使用CSS选择器和JavaScript定位包含字样“概览”的元素并点击
        xpath_expression = f"//li[contains(@class, 'el-menu-item') and contains(text(), '{keyword}')]"
        element = self.try_find_clickable_element(xpath_expression)
        self.try_click_element(element)
        debug_text = f"success click_on_head {child} = {keyword}"
        self.log.log_message(debug_text, 1)

    def login_zz(self):
        self.step = 1

        def on_confirm():
            root.quit()

        root = tk.Tk()
        root.title("等待登录")
        root.geometry("300x150")

        label = tk.Label(root, text="请等待弹出的智蛛页面加载完毕，之后手动登录。成功后点击确认继续运行程序。",
                         font=("Helvetica", 14))
        label.pack(pady=20)

        confirm_button = tk.Button(root, text="确认", command=on_confirm, font=("Helvetica", 12))
        confirm_button.pack(pady=10)
        root.mainloop()
        # 关闭窗口
        root.destroy()
        pass

    def open_new_web(self, visible=None, max_retries=2):
        self.step = 0
        if visible:
            self.log.log_message("ready open_new_web_invisible")
            # 配置 Chrome 浏览器的数据路径和无头模式
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument(usr_dir)  # 这里替换为你的 Chrome 数据路径
            chrome_options.add_argument("--headless")  # 启用无头模式
            chrome_options.add_argument("--disable-gpu")  # 如果需要
            chrome_options.add_argument("--window-size=1920,1080")  # 设置窗口大小，确保某些无头模式下的操作可以顺利进行
        else:
            self.log.log_message("ready open_new_web_visible")
            # 配置 Chrome 浏览器的数据路径
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument(usr_dir)  # 这里替换为你的 Chrome 数据路径
            chrome_options.add_argument("--window-size=1920,1080")  # 设置窗口大小，确保某些无头模式下的操作可以顺利进行
        # 初始化 WebDriver（以 Chrome 为例）
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        # 打开指定的 URL
        self.driver.implicitly_wait(self.timeout)
        try:
            # 打开指定的 URL
            self.driver.get(work_url)
            print("Page loaded successfully.")
            # 等待页面加载
        except Exception as e:
            print(f"Error occurred: {e}")
        # 设置隐式等待时间为10秒

        # el-button el-button--default

        retries = 0
        while retries < max_retries:
            try:
                xpath_exp = ".//button[contains(@class, 'el-button el-button--default')]"
                login = self.try_find_clickable_element(xpath_exp)
                if login:
                    time.sleep(2)
                    self.try_click_element(login)
                self.check_on_page()
                self.log.log_message("success open_new_web")
                return
            except:
                self.log.log_message(f"打开新页面第{retries + 1}次重试...", 4)
                retries += 1
                time.sleep(1)
        self.error_time = 101
        raise Exception("操作失败，已达最大重试次数")

    def __disable_open_new_web(self, visible=None):
        self.step = 0
        if visible:
            self.log.log_message("ready open_new_web_invisible")
            # 配置 Chrome 浏览器的数据路径和无头模式
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument(usr_dir)  # 这里替换为你的 Chrome 数据路径
            chrome_options.add_argument("--headless")  # 启用无头模式
            chrome_options.add_argument("--disable-gpu")  # 如果需要
            chrome_options.add_argument("--window-size=1920,1080")  # 设置窗口大小，确保某些无头模式下的操作可以顺利进行
        else:
            self.log.log_message("ready open_new_web_visible")
            # 配置 Chrome 浏览器的数据路径
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument(usr_dir)  # 这里替换为你的 Chrome 数据路径
        # 初始化 WebDriver（以 Chrome 为例）
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        # 打开指定的 URL
        self.driver.get(work_url)
        # 设置隐式等待时间为10秒
        self.driver.implicitly_wait(self.timeout)
        # el-button el-button--default
        xpath_exp = ".//button[contains(@class, 'el-button el-button--default')]"
        login = self.try_find_clickable_element(xpath_exp)
        if login:
            time.sleep(2)
            self.try_click_element(login)
        self.check_on_page()
        self.log.log_message("success open_new_web")

    def de_open_exist_page(self):
        self.log.log_message("ready de_open_exist_page", 1)
        chrome_options = Options()
        chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{debug_port}")
        self.driver = webdriver.Chrome(options=chrome_options)
        # 设置隐式等待时间为10秒
        self.driver.implicitly_wait(self.timeout)
        self.check_on_page()
        self.log.log_message("success de_open_exist_page", 1)

    def check_on_page(self):
        if not self.driver:
            # print(f"driver还没有定义。")
            # self.error.error_alart(message="driver未定义。")
            error_text = "driver还没有定义。"
            self.log.log_message(error_text, 4)
            self.error_time = 101
            raise Exception(error_text)
        self.log.log_message(self.driver.current_url)
        self.log.log_message(self.driver.title)

    def try_find_element(self, xpath_exp: str):
        element = None
        while True:
            try:
                element = WebDriverWait(self.driver, self.timeout).until(
                    EC.visibility_of_element_located((By.XPATH, xpath_exp))
                )

                debug_text = f"查找-元素（xpath = {xpath_exp}）查找成功，当前步骤：{self.step}\n"
                self.log.log_message(debug_text)
                return element
            except:
                error_text = f"查找fail-元素（{xpath_exp}）未能成功找到或显示，超时时间 {self.timeout} 秒。当前步骤：{self.step}\n"
                self.log.log_message(error_text, 4)
                raise Exception(error_text)
        pass

    def is_element_clickable(self, element):
        """
        传入一个element，返回这个元素是否可以被点击。
        等待时间为self.timeout。
        """
        try:
            WebDriverWait(self.driver, self.timeout).until(
                EC.element_to_be_clickable(element)
            )
            return True
        except:
            return False
        pass

    def try_find_clickable_element(self, xpath_exp: str):
        while True:
            try:
                debug_text = f"查找-尝试查找并确认元素是否可点击（{xpath_exp}），当前步骤：{self.step}"
                self.log.log_message(debug_text)
                element = WebDriverWait(self.driver, self.timeout).until(
                    EC.visibility_of_element_located((By.XPATH, xpath_exp))
                )
                WebDriverWait(self.driver, self.timeout).until(
                    EC.element_to_be_clickable((By.XPATH, xpath_exp))
                )
                return element
            except Exception as e:
                error_text = f"查找fail-元素未能成功找到或点击，超时时间 {self.timeout} 秒。当前步骤：{self.step}. 错误信息: {e}\n"
                self.log.log_message(error_text, 4)
                raise Exception(error_text)
        pass

    def try_find_clickable_element_from(self, parent, xpath_exp: str):
        while True:
            try:
                debug_text = f"查找-尝试在父元素中查找并确认子元素是否可点击（{xpath_exp}），当前步骤：{self.step}"
                self.log.log_message(debug_text)
                element = WebDriverWait(self.driver, self.timeout).until(
                    EC.visibility_of_element_located((By.XPATH, xpath_exp))
                )
                child_element = parent.find_element(By.XPATH, xpath_exp)
                WebDriverWait(self.driver, self.timeout).until(
                    EC.element_to_be_clickable(child_element)
                )
                return child_element
            except Exception as e:
                error_text = f"查找fail-子元素未能成功找到或不可点击，超时时间 {self.timeout} 秒。当前步骤：{self.step}. 错误信息: {e}\n"
                self.log.log_message(error_text, 4)
                # self.error_correct(error_text)
                raise Exception(error_text)

    def try_find_elements(self, xpath_exp: str):
        elements = []
        while True:
            try:
                debug_text = f"查找-尝试查找多个元素（{xpath_exp}），当前步骤：{self.step}"
                self.log.log_message(debug_text)
                elements = WebDriverWait(self.driver, self.timeout).until(
                    EC.visibility_of_all_elements_located((By.XPATH, xpath_exp))
                )
                return elements
            except Exception as e:
                error_text = f"查找fail-多个元素（{xpath_exp}）未能成功找到或显示，超时时间 {self.timeout} 秒。当前步骤：{self.step}."
                self.log.log_message(error_text, 3)
                # self.error_correct(error_text)
                raise Exception(error_text)
                # return []  # 返回空数组

    def try_find_element_from(self, parent_element, xpath_exp: str):
        element = None
        while True:
            try:
                debug_text = f"查找-尝试查找父元素中的子元素（{xpath_exp}），当前步骤：{self.step}"
                self.log.log_message(debug_text)

                # 在parent_element下查找子元素
                element = parent_element.find_element(By.XPATH, xpath_exp)

                # 确认子元素是否可见
                if element.is_displayed():
                    return element
                else:
                    raise Exception("子元素不可见")
            except Exception as e:
                error_text = f"查找fail-子元素（{xpath_exp}）未能成功找到或显示，超时时间 {self.timeout} 秒。当前步骤：{self.step}. 错误信息: {e}\n"
                self.log.log_message(error_text, 3)
                # self.error_correct(error_text)
                raise Exception(error_text)

    def try_find_elements_from(self, parent, xpath_exp: str):

        elements = []
        while True:
            try:
                debug_text = f"查找-尝试查找父元素中的多个子元素（{xpath_exp}），当前步骤：{self.step}"
                self.log.log_message(debug_text)
                elements = WebDriverWait(parent, 0.5).until(
                    EC.presence_of_all_elements_located((By.XPATH, xpath_exp))
                )
                visible_elements = [el for el in elements if el.is_displayed()]
                if visible_elements:
                    return visible_elements
            except Exception as e:
                error_text = f"查找fail-多个子元素（{xpath_exp}）未能成功找到或显示，超时时间 {self.timeout} 秒。当前步骤：{self.step}. 错误信息: {e}"
                self.log.log_message(error_text, 3)
                raise Exception(error_text)

    def __disable_try_find_elements_from(self, parent_element, xpath_exp: str):
        """
        在parent_element下寻找xpath_exp对应的所有子元素，并且保证每个子元素已经显示出来。
        若子元素未能成功显示，等待0.5s后重新寻找，若总寻找时间已经超过self.timeout，则返回空数组。
        """
        start_time = time.time()
        elements = []
        while True:
            try:
                debug_text = f"尝试查找父元素中的多个子元素（{xpath_exp}），当前步骤：{self.step}"
                self.log.log_message(debug_text)
                elements = WebDriverWait(self.driver, 0.5).until(
                    EC.visibility_of_all_elements_located((By.XPATH, xpath_exp))
                )
                return parent_element.find_elements(By.XPATH, xpath_exp)
            except Exception as e:
                if time.time() - start_time > self.timeout:
                    error_text = f"多个子元素（{xpath_exp}）未能成功找到或显示，超时时间 {self.timeout} 秒。当前步骤：{self.step}. 错误信息: {e}"
                    self.log.log_message(error_text, 3)
                    # self.error_correct(error_text)
                    return []  # 返回空数组
                time.sleep(0.5)  # 等待0.5秒后重新尝试

    def try_click_element(self, element):
        """
        尝试点击传入的元素，如果点击失败，最多尝试2秒，之后抛出错误。
        """
        start_time = time.time()
        count = 0
        while True:
            try:
                count = count + 1
                debug_text = f"点击-尝试点击元素（{element.text if element.text else '无文本'}），当前步骤：{self.step}, 第{count}次尝试"
                self.log.log_message(debug_text)
                element.click()
                return
            except WebDriverException as e:
                if time.time() - start_time > self.timeout:
                    error_text = f"点击-元素（{element.text if element.text else '无文本'}: {element}）点击失败，超时时间 {self.timeout} 秒。当前步骤：{self.step}. 错误信息: {e}"
                    self.log.log_message(error_text, 3)
                    raise Exception(error_text)
                time.sleep(0.5)  # 等待0.5秒后重新尝试
        pass


def convert_to_timestamp(time_str):
    # 提取日期和时间部分（忽略星期）
    datetime_part = " ".join(time_str.split()[:2])
    # 解析为datetime对象
    dt = datetime.strptime(datetime_part, "%Y-%m-%d %H:%M:%S")
    # 转换为时间戳
    return dt.timestamp()


def get_today_18_timestamp(mini=0):
    # 获取当前日期对象
    today = datetime.today()
    # 替换时间为18:00:00
    target_time = today.replace(hour=end_time, minute=mini, second=0, microsecond=0)
    # 转换为时间戳
    return target_time.timestamp()
