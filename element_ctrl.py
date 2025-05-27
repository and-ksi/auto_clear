# "D:\file\python\project\zz_work\chrome\chrome.exe" --remote-debugging-port=11248 --user-data-dir="D:\file\python\project\zz_work\chrome\usr_data"

import os
import re
import sys
import time
import tkinter as tk

from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.service import Service
# from selenium.common.exceptions import NoSuchElementException

from data_file import Log_save
from data_file import Post_Message
from data_file import ZZData
from data_file import ConfigManager

debug_port = 11248
# usr_dir = "user-data-dir=D:\\file\\python\\project\\zz_work\\chrome-win64\\usr_data"
# binary_location = "D:\\file\\python\\project\\zz_work\\chrome-win64\\chrome.exe"
# chrome_driver_location = "D:\\file\\python\\project\\zz_work\\chrome-win64\\chromedriver.exe"
# work_url = "https://zz-dealer.bydauto.com.cn"
# work_url = "https://zz-dealer.bydauto.com.cn/#/login"
end_time = 18
visiable_value = 1


# error_time = 100 : 到达当天清洗结束时间
# error_time = 0 : 可以忽略的错误 \\ 无错误
# error_time = 101 : 直接结束程序并且把错误上报

class element_operate:
    def __init__(self):
        # debug
        self.log = Log_save(2)
        # self.zzdata = ZZData()
        self.data = []
        self.driver = None
        self.timeout = 6
        self.step = 0
        self.error_time = 0
        self.error = Post_Message()
        self.manager = None
        self.passager = None
        self.phone = ""
        self.error_log_text = None
        self.error_t = 0

        config = ConfigManager()
        self.work_url = config.get_data('ACCOUNT', 'work_url')
        current_directory = os.getcwd()
        if sys.platform.startswith("win"):
            self.binary_location = os.path.join(current_directory, 'chrome', 'chrome.exe')
            self.chrome_driver_location = os.path.join(current_directory, 'chrome', 'chromedriver.exe')
        else:
            self.binary_location = os.path.join(current_directory, 'chrome', 'chrome')
            self.chrome_driver_location = os.path.join(current_directory, 'chrome', 'chromedriver')
        self.usr_dir = os.path.join(current_directory, 'chrome', 'usr_data')

    def switch_in(self):
        visiable = int(
            input("是否需要显示浏览器？输入1浏览器将一直显示，输入0将隐藏浏览器显示。（隐藏显示可避免被他人误关闭）"))
        mark = int(input(
            "是否要开始读取今日线索数据？输入1开始读取，输入2跳过。(读取数据必会显示浏览器，请在浏览器打开后，筛选出想要读取的数据，之后点击弹窗的确定后开始读取到数据库。)"))
        if mark == 1:
            self.check_data_to_mysql()
        else:
            self.work_flow(visiable)
        pass

    def work_flow(self, vis):
        try:
            self.log.start_log()
            self.error_time = 0
            self.open_new_web(visible=vis)
            self.click_on_head(2)
            self.check_clue_loop()
        finally:
            self.save_page_pic()
            self.error.post_error(message="程序已经停止，看看什么情况")
            if self.error_time:
                self.error.error_alart(message=f"程序运行出错，error_time = {self.error_time}.详情查看log文件。")

    def save_page_pic(self):
        if not os.path.exists('pic'):
            os.makedirs('pic')

        # 获取当前日期和时间，并格式化文件名
        current_time = datetime.now().strftime("%Y%m%d-%H%M%S")
        screenshot_filename = f"{current_time}.png"
        # 截图并保存到 pic 文件夹
        screenshot_path = os.path.join('pic', screenshot_filename)
        self.driver.save_screenshot(screenshot_path)

        self.log.log_message(f"截图已保存到 {screenshot_path}")

    def check_clue_loop(self):
        self.step = 2
        # while 1:
        while time.time() < get_today_18_timestamp(4):
            self.driver.refresh()
            self.click_on_head(2)
            self.click_on_subhead(2)
            tol_time = time.time()
            self.click_on_radio_button(1)
            time.sleep(0.3)
            mark = self.check_item_count()
            if mark:
                log_text = f"准备清洗线索：++++++++++++++++++++++++++++++++++++++++"
                self.log.log_message(log_text)
                dis = self.clue_clear()
                if dis:
                    self.clue_follow()

            self.click_on_head(2)
            self.click_on_subhead(2)
            self.click_on_radio_button(2)
            time.sleep(0.3)
            mark = self.check_item_count()
            if mark:
                log_text = f"准备分配线索：+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-"
                self.log.log_message(log_text)
                self.clue_distribute()
                self.clue_follow()
        pass

    def disable_check_clue_loop(self):
        self.step = 2
        while time.time() < get_today_18_timestamp(4):
            self.driver.refresh()
            self.click_on_head(2)
            self.click_on_subhead(2)
            tol_time = time.time()
            while time.time() < get_today_18_timestamp(4):
                mark = 0
                self.click_on_radio_button(6)
                time.sleep(0.3)
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
                    log_text = f"准备分配线索：____________________________________________"
                    self.log.log_message(log_text)
                    self.clue_distribute()
                    # self.zzdata.add_or_update_batch(self.phone, self.data)

                    self.clue_follow()
                    self.click_on_head(2)
                    self.click_on_subhead(2)

                if time.time() - tol_time > 300:
                    break

                # 检查待清洗
                mark = 0
                self.click_on_radio_button(6)
                time.sleep(0.3)
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
                    log_text = f"准备清洗线索：++++++++++++++++++++++++++++++++++++++++"
                    self.log.log_message(log_text)
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
                self.log.log_message(f"success clue_follow！\n------------------------------------")
                self.step = 2
                return
            except:
                error_text = f"线索跟进失效第{retries + 1}次，请及时跟进，客户：{self.passager}-{self.phone}"
                self.log.log_message(error_text, 4)
                self.driver.refresh()  # 直接使用 driver.refresh()  刷新页面
                retries += 1
                time.sleep(1)
        self.error_time = 101
        raise Exception("操作失败，已达最大重试次数")
        pass

    def clue_distri(self, correct_label):
        self.phone = self.read_label_in_table("手机号")
        self.manager = self.read_label_in_table("姓名")

        xpath_exp = ".//input[contains(@placeholder, '选择客户经理')]"
        ele = self.try_find_clickable_element_from(correct_label, xpath_exp)
        self.try_click_element(ele)

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
                        if entry[1] == 0:
                            name_list.append([name, 999999, index])
                        else:
                            # 计算数字之和并新建一个数组
                            name_list.append([name, number / entry[1], index])
                        print(f"新数组: {name_list}")
                        break
            else:
                self.log.log_message("Nod find name and number from total number.", 4)

        log_text = f"name_list_mid = {name_list_mid}; name_list = {name_list}"
        self.log.log_message(log_text, 1)

        min_num = 999999
        min_index = -1
        min_name = []

        # 识别特殊分配规则
        rules = config.get_all_string_groups()
        if rules:
            pass

        for min_name in name_list:
            if min_name[1] < min_num:
                min_num = min_name[1]
                min_index = min_name[2]
        for sub_name in name_list_mid:
            if len(sub_name) > 0 and sub_name[0] == min_name[0]:
                min_num = -1
                break

        if min_num < 0:
            # self.data.append(["客户经理", ele_dropdowns[min_index].text])
            self.try_click_element(ele_dropdowns[min_index])
        else:
            self.error.error_alart("min_num > 0")

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

                # xpath_exp = "//div[contains(@class, 'el-dialog') and contains(@aria-label, '线索详情')]"
                # trouble: 这里可能有问题1
                xpath_exp = "//div[contains(@class, 'el-dialog') and not(contains(@style, 'display: none;')) and .//span[text()='线索详情']]"
                correct_label = self.try_find_element(xpath_exp)
                # xpath_exp = ".//div[contains(@class, 'el-select') and contains(@class, 'el-select--mini') and contains(text(), '选择客户经理')]"

                self.clue_distri(correct_label)

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
                self.log.log_message(f"success clue_distribute！{self.passager}-{self.phone}")
                return
            except:
                self.log.log_message(f"线索分配第{retries + 1}次重试...", 4)
                self.driver.refresh()  # 直接使用 driver.refresh()  刷新页面
                retries += 1
                time.sleep(1)

                # 筛选并删除匹配特定字符串的项
                # filtered_data = self.data
                # filtered_data = [item for item in filtered_data if item[0] != "手机号"]
                # filtered_data = [item for item in filtered_data if item[0] != "客户经理"]
                # self.data = filtered_data
        self.error_time = 101
        raise Exception("操作失败，已达最大重试次数")
        pass

    def check_version_before_clear(self):
        self.click_on_head(2)
        self.click_on_subhead(2)
        time.sleep(0.5)

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

        now_time = self.read_label_in_table("线索创建时间")

        xpath_exp = ".//input[contains(@placeholder, '选择客户经理')]"
        ele = self.try_find_clickable_element_from(correct_label, xpath_exp)
        if ele:
            return True
        else:
            return False

    def clue_clear(self, max_retries=2):
        self.step = 3
        retries = 0
        dis = True

        dis = self.check_version_before_clear()

        while retries < max_retries:
            try:

                xpath_exp = "//div[contains(@class, 'el-dialog__wrapper') and not(contains(@style, 'display: none;')) and .//span[text()='线索详情']]"
                correct_label = self.try_find_element(xpath_exp)

                # 线索时间判断
                now_time = self.read_label_in_table("线索创建时间")
                # self.data.append(["线索创建时间", now_time])
                # value = re.match(r"^[^\-]+", name).group().strip()
                # self.data.append(["姓名", value])

                if convert_to_timestamp(now_time) >= get_today_18_timestamp():
                    self.error_time = 100
                    log_text = f"今日线索清洗完毕。"
                    self.log.log_message(log_text)
                    raise Exception(log_text)

                value = self.read_label_in_table("意向车系")
                self.log.log_message(f"意向车系value = {value}")
                if value == "" or value is None:
                    self.log.log_message(f"None of car choice")
                    # xpath_exp = ".//i[contains(@class, 'el-select__caret') and contains(@class, 'el-input__icon') and contains(@class, 'el-icon-arrow-up')]"
                    xpath_exp = ".//input[@placeholder='选择意向车系']"
                    content = self.try_find_clickable_element_from(correct_label, xpath_exp)

                    self.try_click_element(content)
                    # 点出选择菜单
                    # 选择好车系
                    # el-select-dropdown el-popper is-multiple
                    xpath_exp = ".//div[contains(@class, 'el-select-dropdown') and contains(@class, 'el-popper') and contains(@class, 'is-multiple') and not(contains(@style, 'display: none;'))]"
                    element_sele = self.try_find_element(xpath_exp)
                    # el-select-dropdown__item
                    xpath_exp = ".//li[contains(@class, 'el-select-dropdown__item')]"
                    ele = self.try_find_element_from(element_sele, xpath_exp)
                    # self.data.append(["意向车系", ele.text])
                    self.try_click_element(ele)
                # else:
                #     self.data.append(["意向车系", value])
                #
                # try:
                #     value = self.read_label_in_table("参与活动")
                #     self.data.append(["参与活动", value])
                # except:
                #     pass
                # try:
                #     value = self.read_label_in_table("来源平台")
                #     self.data.append(["来源平台", value])
                # except:
                #     pass
                # try:
                #     value = self.read_label_in_table("线索类别")
                #     self.data.append(["线索类别", value])
                # except:
                #     pass
                if dis:
                    self.clue_distri(correct_label)

                texture = "线索清洗au"
                xpath_exp = "//textarea[@placeholder='请输入备注内容']"
                textarea = self.try_find_element_from(correct_label, xpath_exp)
                textarea.clear()
                textarea.send_keys(texture)
                time.sleep(0.5)
                xpath_exp = ".//span[contains(text(), '确定')]"
                element = self.try_find_clickable_element_from(correct_label, xpath_exp)
                self.try_click_element(element)
                time.sleep(0.5)
                xpath_exp = ".//div[contains(@class, 'el-message-box__wrapper') and contains(@aria-label, '提示')]"
                element_sure = self.try_find_clickable_element(xpath_exp)
                xpath_exp = ".//span[contains(text(), '确定')]"
                # xpath_exp = "//button[span[text()='确定']]"
                element = self.try_find_clickable_element_from(element_sure, xpath_exp)
                self.try_click_element(element)
                self.log.log_message(f"success clue_clear！")

                return dis
            except:
                self.log.log_message(f"线索清洗第{retries + 1}次重试...", 4)
                self.driver.refresh()
                retries += 1
                time.sleep(1)
                self.click_on_head(2)
                self.click_on_subhead(2)
                time.sleep(0.5)

        self.error_time = 101
        raise Exception("操作失败，已达最大重试次数")
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
                self.log.log_message(f"success check_item_count : {int(match.group())}")
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
        xpath_expression = "//span[contains(@class, 'click_link')]"
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

    def wait_load_mask(self):
        start_time = time.time()
        xpath_expression = "//div[contains(@class, 'el-loading-mask') and contains(@style, 'display: none;')]"
        while not self.try_find_element_nerror(xpath_expression):
            if time.time() - start_time > self.timeout:
                self.log.log_message(message="等待表格加载时间过久，检查网络连接。", mark=3)
                # raise Exception("等待超时")
                return False
            time.sleep(0.5)
        return True

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

        try:
            self.wait_load_mask()
        except:
            self.driver.refresh()
            time.sleep(1)
            xpath_expression = f"//label[contains(@class, 'el-radio-button') and contains(@class, 'el-radio-button--small') and .//span[text()='{keyword}']]"
            element = self.try_find_clickable_element(xpath_expression)
            self.try_click_element(element)
            key = self.wait_load_mask()
            if key:
                pass
            else:
                self.error_time = 101

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
        return True

    def wait_window(self, title="error", textf="待点击"):
        def on_confirm():
            root.quit()

        root = tk.Tk()
        root.title(title)
        root.geometry("300x150")

        label = tk.Label(root, text=textf, font=("Helvetica", 14))
        label.pack(pady=20)

        confirm_button = tk.Button(root, text="确认", command=on_confirm, font=("Helvetica", 12))
        confirm_button.pack(pady=10)
        root.mainloop()
        # 关闭窗口
        root.destroy()
        pass

    def login_zz(self):
        self.step = 1
        # self.open_new_web(login_mark=1)
        # self.wait_window("等待登录", "请等待弹出的智蛛页面加载完毕，之后手动登录。成功后点击确认继续运行程序。")
        config = ConfigManager()
        account = config.get_account()

        xpath_exp = "//input[@class='mobile' and @placeholder='请输入手机号码']"
        ele = self.try_find_element(xpath_exp)
        ele.clear()
        ele.send_keys(account[0])

        xpath_exp = "//input[@class='mobile' and @placeholder='请输入密码']"
        ele = self.try_find_element(xpath_exp)
        ele.clear()
        ele.send_keys(account[1])

        xpath_exp = ".//button[contains(@class, 'el-button')]//span[text()='登录']"
        login = self.try_find_clickable_element(xpath_exp)
        self.try_click_element(login)
        time.sleep(0.5)

        xpath_exp = "//div[contains(@class, 'send') and contains(text(), '发送验证码')]"
        code = self.try_find_element_nerror(xpath_exp)
        if code:
            self.try_click_element(code)
            # start_time = time.time()
            # while time.time() - start_time < 300:
            #     code = config.get_code()
            #     if code == "":
            #         time.sleep(1)
            #     else:
            #         break
            # if code == "":
            #     error_message = "验证码过期，请重新获取！"
            #     self.error.error_alart(error_message)

            code = input("请输入验证码：")

            xpath_exp = "//input[@class='sms' and @placeholder='请输入验证码']"
            ele = self.try_find_element(xpath_exp)
            ele.clear()
            ele.send_keys(code)
            xpath_exp = ".//button[contains(@class, 'el-button') and contains(@class, 'code-btn')]//span[normalize-space()='登录']"
            ele = self.try_find_element(xpath_exp)
            self.try_click_element(ele)

    def open_new_web(self, visible=visiable_value, login_mark=None, max_retries=2):
        self.step = 0
        if not visible:
            self.log.log_message("ready open_new_web_invisible")
            # 配置 Chrome 浏览器的数据路径和无头模式
            chrome_options = webdriver.ChromeOptions()
            chrome_options.binary_location = self.binary_location
            chrome_options.add_argument(f"user-data-dir={self.usr_dir}")  # 这里替换为你的 Chrome 数据路径
            chrome_options.add_argument("--headless=new")  # 启用无头模式
            chrome_options.add_argument("--disable-gpu")  # 如果需要
            chrome_options.add_argument("--window-size=1920,1080")  # 设置窗口大小，确保某些无头模式下的操作可以顺利进行
        else:
            self.log.log_message("ready open_new_web_visible")
            # 配置 Chrome 浏览器的数据路径
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument(f"user-data-dir={self.usr_dir}")  # 这里替换为你的 Chrome 数据路径
            chrome_options.binary_location = self.binary_location
            chrome_options.add_argument("--window-size=1920,1080")  # 设置窗口大小，确保某些无头模式下的操作可以顺利进行
        # 初始化 WebDriver（以 Chrome 为例）
        service = Service(self.chrome_driver_location)  # 指定 chromedriver 位置
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        # 打开指定的 URL
        self.driver.implicitly_wait(self.timeout)
        try:
            # 打开指定的 URL
            self.driver.get(self.work_url)
            print("Page loaded successfully.")
            # 等待页面加载
        except Exception as e:
            print(f"Error occurred: {e}")
        # 设置隐式等待时间为10秒

        retries = 0
        while retries < max_retries:
            try:
                self.login_zz()
                self.check_on_page()
                self.log.log_message("success open_new_web")
                return
            except:
                if self.click_on_head(2):
                    self.check_on_page()
                    self.log.log_message("success open_new_web")
                    return
                self.log.log_message(f"打开新页面第{retries + 1}次重试...", 4)
                retries += 1
                time.sleep(1)
        self.error_time = 101
        raise Exception("操作失败，已达最大重试次数")

    def de_open_exist_page(self):
        self.log.log_message("ready de_open_exist_page", 1)
        chrome_options = Options()
        chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{debug_port}")
        service = Service(self.chrome_driver_location)  # 指定 chromedriver 位置
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
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

    def try_find_element_nerror(self, xpath_exp: str):
        element = None
        while True:
            try:
                element = WebDriverWait(self.driver, self.timeout).until(
                    EC.presence_of_element_located((By.XPATH, xpath_exp))
                )

                debug_text = f"查找-元素（xpath = {xpath_exp}）查找成功，当前步骤：{self.step}\n"
                self.log.log_message(debug_text)
                return element
            except:
                pass
            error_text = f"查找fail-元素（{xpath_exp}）未能成功找到或显示，超时时间 {self.timeout} 秒。当前步骤：{self.step}\n"
            self.log.log_message(error_text, 4)
            return None
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
                # WebDriverWait(self.driver, self.timeout).until(
                #     EC.element_to_be_clickable((By.XPATH, xpath_exp))
                # )
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
                    EC.presence_of_all_elements_located((By.XPATH, xpath_exp)))
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

    def try_click_element(self, element):
        """
        尝试点击传入的元素：
        1. 先尝试 Selenium 默认点击 `element.click()`
        2. 如果失败，使用 JavaScript 点击 `driver.execute_script("arguments[0].click();", element)`
        3. 如果仍失败，抛出错误
        """
        start_time = time.time()
        count = 0

        while True:
            try:
                count += 1
                debug_text = f"点击-尝试点击元素（{element.text if element.text else '无文本'}），当前步骤：{self.step}, 第{count}次尝试"
                self.log.log_message(debug_text)

                # 尝试 Selenium 默认点击
                element.click()
                time.sleep(0.5)
                return

            except WebDriverException as e:
                self.log.log_message("点击失败，尝试使用 JavaScript 点击", 2)

                try:
                    # 使用 JavaScript 进行点击
                    self.driver.execute_script("arguments[0].click();", element)
                    time.sleep(0.5)
                    return

                except WebDriverException as js_e:
                    self.log.log_message(f"JavaScript 点击失败: {js_e}", 3)
                    # 超时，抛出异常
                    if time.time() - start_time > self.timeout:
                        error_text = f"点击-元素（{element.text if element.text else '无文本'}: {element}）点击失败，超时时间 {self.timeout} 秒。当前步骤：{self.step}. 错误信息: {e}"
                        self.log.log_message(error_text, 3)
                        raise Exception(error_text)

                time.sleep(0.5)  # 等待后重试

    def find_second_subele(self, label, class_n, pa_ele):

        xpath_exp = f"//*[contains(@class, '{class_n}') and .//*[contains(text(), '{label}')]]"
        ele = self.try_find_element_from(pa_ele, xpath_exp)
        # 然后在parent_element下查找第二个子元素
        second_child_xpath = "./* [position()=2]"
        second_child_element = self.try_find_element_from(ele, second_child_xpath)
        return second_child_element

    def check_data_to_mysql(self):
        zzdata = ZZData()

        self.log.start_log()
        phone = ""
        self.error_time = 0
        count = 0
        self.open_new_web(visible=1, login_mark=1)
        self.wait_window("等待打开待扫描页面", "打开待扫描页面后关闭")
        total = self.check_item_count()
        while 1:
            time.sleep(0.5)
            expath_exp = "//*[contains(@class, 'click_link')]"
            table_links = self.try_find_elements(expath_exp)
            row = 0
            len_ele = len(table_links)
            while row < len_ele:
                table_links = self.try_find_elements(expath_exp)
                link = table_links[row]
                row += 1
                data = []
                "车友383479 - 15391000937"
                phone = re.search(r'-\s*(\S+)', link.text).group(1)
                name = re.match(r"^[^\-]+", link.text).group().strip()
                data.append([zzdata.labels_title[0], phone])
                data.append([zzdata.labels_title[1], name])

                self.try_click_element(link)
                xpath_exp = f"//div[contains(@class, 'whiteBox')]//*[contains(text(), '{phone}')]"
                pa_ele = self.try_find_element(xpath_exp)
                ta_ele = self.find_second_subele('客户经理', 'pure-g', pa_ele)
                data.append(['客户经理', ta_ele.text])
                ta_ele = self.find_second_subele('客户级别', 'pure-g', pa_ele)
                data.append(['客户级别', ta_ele.text])
                ta_ele = self.find_second_subele('意向车系', 'pure-g', pa_ele)
                car = ta_ele.text.split(',')[0]
                data.append(['意向车系', car])
                time.sleep(0.5)
                self.click_table_link()  # 点击线索详情
                xpath_exp = f"//div[contains(@class, 'el-dialog') and .//*[contains(text(), '线索详情')]]"
                pa_ele = self.try_find_element(xpath_exp)
                ta_ele = self.find_second_subele('来源平台', 'el-form-item', pa_ele)
                data.append(['来源平台', ta_ele.text])
                ta_ele = self.find_second_subele('线索类别', 'el-form-item', pa_ele)
                data.append(['线索类别', ta_ele.text])
                try:
                    self.driver.implicitly_wait(0.5)
                    ta_ele = self.find_second_subele('参与活动', 'el-form-item', pa_ele)
                    self.driver.implicitly_wait(self.timeout)
                    data.append(['参与活动', ta_ele.text])
                except:
                    pass
                ta_ele = self.find_second_subele('线索创建时间', 'el-form-item', pa_ele)
                data.append(['线索创建时间', ta_ele.text])

                zzdata.add_or_update_batch(phone, data)
                count += 1
                xpath_exp = ".//button/span[contains(text(), '关闭')]"
                ta_ele = self.try_find_element_from(pa_ele, xpath_exp)
                self.try_click_element(ta_ele)
                self.click_on_head(3)
                self.wait_load_mask()

            xpath_exp = "//button[contains(@class, 'btn-next')]"
            next = self.try_find_element(xpath_exp)
            if count >= total and zzdata.phone_exist(phone):
                self.log.log_message("完成全部线索登记。")
                self.log.log_message("线索完成登记")
                exit()
            try:
                self.try_click_element(next)
            except:
                self.log.log_message("线索完成登记")
                exit()
            self.wait_load_mask()

    def check_clue_server(self):
        self.open_new_web(0)
        nowtime = time.time()
        mark = None
        ele = None
        while 1:
            while get_today_18_timestamp(4) > time.time() > get_today_18_timestamp(4, 9):
                self.driver.refresh()
                self.click_on_head(2)
                self.click_on_subhead(2)
                self.click_on_radio_button(1)
                total = self.check_item_count()
                if total > 0:
                    xpath_exp = "//span[contains(@class, 'click_link')]"
                    eles = self.try_find_elements(xpath_exp)
                    mark = 0

                    for entry in eles:
                        if entry.text == ele:
                            mark = 1
                            if time.time() - nowtime > 180:
                                self.error.post_error(message="有线索3分钟没动了，看看是不是程序停止了。")
                            break
                    if mark != 1:
                        ele = eles[0].text
                        nowtime = time.time()
                else:
                    nowtime = time.time()
            time.sleep(60)


def convert_to_timestamp(time_str):
    # 提取日期和时间部分（忽略星期）
    datetime_part = " ".join(time_str.split()[:2])
    # 解析为datetime对象
    dt = datetime.strptime(datetime_part, "%Y-%m-%d %H:%M:%S")
    # 转换为时间戳
    return dt.timestamp()


def get_today_18_timestamp(mini=0, etime=end_time):
    # 获取当前日期对象
    today = datetime.today()
    # 替换时间为18:00:00
    target_time = today.replace(hour=etime, minute=mini, second=0, microsecond=0)
    # 转换为时间戳
    return target_time.timestamp()
