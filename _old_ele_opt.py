# "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=11248 --user-data-dir="D:\file\python\selenium_chrome"

import re
import time
import tkinter as tk
import requests

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
# from selenium.common.exceptions import NoSuchElementException

from data_any import ConfigManager
from data_any import ZZData
from log_save import Log_save

debug_port = 11248
usr_dir = "user-data-dir=D:\\file\\python\\selenium_chrome"
work_url = "https://zz-dealer.bydauto.com.cn/#/activity/clue-clear"

class Page_Driver:
    def __init__(self):
        # debug
        self.log = Log_save(l_level="Debug")
        self.driver = None
        self.timeout = 8

    def de_open_exist_page(self):
        self.log.log_message("ready de_open_exist_page", 1)
        chrome_options = Options()
        chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{debug_port}")
        self.driver = webdriver.Chrome(options=chrome_options)
        # 设置隐式等待时间为10秒
        self.driver.implicitly_wait(self.timeout)
        self.check_on_page()
        self.log.log_message("success de_open_exist_page", 1)

    def open_new_web_visible(self):
        self.log.log_message("ready open_new_web_visible", 1)
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
        login = self.try_find_element(xpath_exp, 1)
        if login:
            time.sleep(2)
            self.click_element(login)
        self.check_on_page()
        self.log.log_message("success open_new_web_visible", 1)

    def open_new_web_invisible(self):
        self.log.log_message("ready open_new_web_invisible", 1)
        # 配置 Chrome 浏览器的数据路径和无头模式
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument(usr_dir)  # 这里替换为你的 Chrome 数据路径
        chrome_options.add_argument("--headless")  # 启用无头模式
        chrome_options.add_argument("--disable-gpu")  # 如果需要
        chrome_options.add_argument("--window-size=1920,1080")  # 设置窗口大小，确保某些无头模式下的操作可以顺利进行

        # 初始化 WebDriver（以 Chrome 为例）
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

        # 打开指定的 URL
        self.driver.get(work_url)

        # 设置隐式等待时间为10秒
        self.driver.implicitly_wait(self.timeout)

        # 查找并点击登录按钮
        xpath_exp = ".//button[contains(@class, 'el-button el-button--default')]"
        login = self.try_find_element(xpath_exp, 1)
        if login:
            self.click_element(login)

        self.check_on_page()
        self.log.log_message("success open_new_web_invisible", 1)

    def post_to_phone(self, message):
        # https://wxpusher.zjiecode.com/api/send/message
        # {
        #   "appToken":"AT_ctBuoL9g9rFvk8uBogW0Bd0WSC6QMhuE",
        #   "content":"<h1>运行错误</h1><br/><p style=\"color:red;\">name.csv读取出错</p>",
        #   "summary":"运行错误，已停止",
        #   "contentType":2,
        #   "topicIds":[
        #   ],
        #   "uids":[
        #       "UID_dBjKN9UIkvXggPC0NipFYGXBTAJw"
        #   ],
        #   "verifyPay":false,
        #   "verifyPayType":0
        # }

        # 定义目标 URL
        url = "https://wxpusher.zjiecode.com/api/send/message"

        # 定义要发送的数据
        data = {
            "appToken": "AT_ctBuoL9g9rFvk8uBogW0Bd0WSC6QMhuE",
            "content": f"<h1>运行错误</h1><br/><p style=\"color:red;\">{message}</p>",
            "summary": "py运行错误，已停止",
            "contentType": 2,
            "topicIds": [],
            "uids": [
                "UID_dBjKN9UIkvXggPC0NipFYGXBTAJw"
            ],
            "verifyPay": False,
            "verifyPayType": 0
        }

        # 发送 POST 请求
        response = requests.post(url, json=data)

        # 检查响应状态码
        if response.status_code == 200:
            print("请求成功！")
            print("响应数据：", response.json())
        else:
            print(f"请求失败，状态码：{response.status_code}")
            print("错误信息：", response.text)

        pass

    def error_alart(self, title="Error", message="这是一个保持在桌面显示的弹窗", error_mark=0):
        self.log.log_message(message=message, mark=4)
        self.post_to_phone(message)
        """显示一个保持在桌面显示的弹窗"""

        def keep_on_top(root):
            """使窗口保持在最前端"""
            root.attributes("-topmost", True)
            root.after(1000, lambda: keep_on_top(root))

        root = tk.Tk()
        root.title(title)
        label = tk.Label(root, text=message, font=("Helvetica", 16))
        label.pack(pady=20)
        root.resizable(False, False)
        keep_on_top(root)
        root.mainloop()
        if error_mark:
            return error_mark
        else:
            raise SystemExit

    def try_find_elements(self, xpath_expression, mark=None, time_wait=0.5):
        try:
            time.sleep(time_wait)
            elements = self.driver.find_elements(By.XPATH, xpath_expression)
            return elements
        except Exception as e:
            if mark:
                return None
            else:
                self.error_alart(message=f"Not find {xpath_expression} in try_find_elements!")

    # def try_find_elements(self, xpath_expression, mark=None):
    #     start_time = time.time()
    #     while time.time() - start_time < self.timeout:
    #         try:
    #             elements = self.driver.find_elements(By.XPATH, xpath_expression)
    #             non_empty_elements = [element for element in elements if element.text.strip() != ""]
    #             if non_empty_elements:
    #                 return non_empty_elements
    #             else:
    #                 self.log.log_message(f"找到的元素文本为空，继续查找...", 2)
    #         except NoSuchElementException:
    #             if mark:
    #                 return None
    #             else:
    #                 self.error_alart(message=f"Not find {xpath_expression} in try_find_elements!")
    #                 self.log.log_message(f"Error: 123", 2)
    #         time.sleep(0.5)  # 等待0.5秒再尝试
    #     return None

    def try_find_element(self, xpath_expression, mark=None, time_wait=0.5):
        try:
            time.sleep(time_wait)
            element = self.driver.find_element(By.XPATH, xpath_expression)
            return element
        except Exception as e:
            if mark:
                return None
            else:
                self.error_alart(message=f"Not find {xpath_expression} in try_find_element!")

    def try_find_element_from(self, ele, xpath_expression, mark=None, time_wait=0):
        try:
            time.sleep(time_wait)
            element = ele.find_element(By.XPATH, xpath_expression)
            return element
        except Exception as e:
            if mark:
                return None
            else:
                self.error_alart(message=f"Not find {xpath_expression} in try_find_element!")

    def try_find_elements_from(self, ele, xpath_expression, mark=None, time_wait = 0):
        try:
            time.sleep(time_wait)
            elements = ele.find_elements(By.XPATH, xpath_expression)
            return elements
        except Exception as e:
            if mark:
                return None
            else:
                self.error_alart(message=f"Not find {xpath_expression} in try_find_element!")

    # 检查当前页面内容
    def check_on_page(self):
        if self.driver == None:
            print(f"driver还没有定义。")
            self.error_alart(message="driver未定义。")
        self.log.log_message(self.driver.current_url)
        self.log.log_message(self.driver.title)
        # print(self.driver.current_url)
        # print(self.driver.title)

    def find_click_on_ele(self, xpath_expression):
        self.log.log_message(f"ready find_click_on_ele {xpath_expression}", 1)
        # self.driver.implicitly_wait(0)
        element = self.try_find_element(xpath_expression)
        if element:
            self.click_element(element)
        else:
            self.error_alart(message=f"Not find {xpath_expression}!")
        # self.driver.implicitly_wait(self.timeout)
        self.log.log_message(f"success find_click_on_ele {xpath_expression}", 1)

    def click_on_head(self, child):
        self.log.log_message(f"ready click_on_head {child}", 1)
        if child == 1:
            keyword = "概览"
        elif child == 2:
            keyword = "工作任务"
        elif child == 3:
            keyword = "客户档案"
        else:
            keyword = None
            self.error_alart(message="Head keyword error!")
        self.log.log_message(f"ready click_on_head {keyword}", 1)
        # 使用CSS选择器和JavaScript定位包含字样“概览”的元素并点击
        xpath_expression = f"//li[contains(@class, 'el-menu-item') and contains(text(), '{keyword}')]"
        self.find_click_on_ele(xpath_expression)
        self.log.log_message(f"success click_on_head {child} = {keyword}", 1)

    # 点击线索处理用的
    def click_on_subhead(self, child):
        self.log.log_message(f"ready click_on_subhead {child}", 1)
        if child == 1:
            keyword = "跟进任务"
        elif child == 2:
            keyword = "线索处理"
        else:
            keyword = None
            self.error_alart(message="Subhead keyword error!")
        self.log.log_message(f"ready click_on_subhead {keyword}", 1)
        xpath_expression = f"//li[contains(@class, 'el-menu-item') and contains(text(), '{keyword}')]"
        self.find_click_on_ele(xpath_expression)
        self.log.log_message(f"success click_on_subhead {child} = {keyword}", 1)

    def wait_table_load(self):
        time.sleep(0.5)
        try:
            self.log.log_message(f"ready to wait_table_load")
            # 等待最多 10 秒，直到目标元素出现
            wait = WebDriverWait(self.driver, 10)
            element = wait.until(ec.presence_of_element_located((By.XPATH, "//div[@class='el-loading-mask' and @style='display: none;']")))
            # 元素找到后可以执行其他操作
            self.log.log_message(f"success to wait_table_load")
        except Exception as e:
            # 如果未找到元素，运行 self.error_alart 函数
            self.error_alart(message="Weberror? Cant wait_ele_load")
        # return self.wait_ele_load("//div[contains(@class, 'el-loading-mask')]", "style", "display: none;")

    def debug_wait_table_load(self):
        count = 0
        while True:
            pass
        pass

    def check_item_count(self):
        self.log.log_message(f"ready check_item_count", 1)
        self.wait_table_load()
        # 查找元素并提取文本
        xpath_exp = "//span[@class='el-pagination__total']"
        element = self.try_find_element(xpath_exp)
        if element:
            text = element.text
            match = re.search(r'\d+', text)
            if match:
                self.log.log_message(f"success check_item_count", 1)
                return int(match.group())
            else:
                self.error_alart(message="Match int error!")
                return None
            # print("提取到的文本：", text)
        else:
            self.error_alart(message="Not find paginatino__total!")
            return None

    # 点击待清洗待分配
    def click_on_radio_button(self, child):
        self.log.log_message(f"ready click_on_radio_button {child}", 1)
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
            self.error_alart(message="Radio button keyword error!")
        self.log.log_message(f"ready click_on_radio_button {child} = {keyword}", 1)
        self.wait_table_load()
        # //label[contains(@class, 'el-radio-button') and contains(@class, 'el-radio-button--small') and .//span[text()='待分配']]
        xpath_expression = f"//label[contains(@class, 'el-radio-button') and contains(@class, 'el-radio-button--small') and .//span[text()='{keyword}']]"
        self.find_click_on_ele(xpath_expression)
        self.log.log_message(f"success click_on_radio_button {child} = {keyword}", 1)

    def element_displayed(self, element):
        start_time = time.time()
        while not(element.is_displayed()) and (time.time() - start_time < self.timeout):
            time.sleep(0.5)
        if time.time() - start_time >= self.timeout:
            self.error_alart(f"Can not find [{element.text}] displayed on screen!, {element}")


    def click_element(self, element, time_wait = 0):
        # self.element_displayed(element)
        time.sleep(time_wait)
        start_time = time.time()
        text = element.text
        while time.time() - start_time < self.timeout:
            try:
                # 滚动到元素位置
                self.log.log_message(f"[{text}] 元素准备点击！, {element}")
                self.driver.execute_script("arguments[0].scrollIntoView();", element)
                # 点击元素
                element.click()
                self.log.log_message(f"[{text}] 元素已点击！")
                return True
            except Exception as e:
                remaining_time = self.timeout - (time.time() - start_time)
                self.log.log_message(f"尝试点击元素[{text}]失败，继续尝试... 剩余时间: {remaining_time} 秒")
            time.sleep(0.5)  # 等待0.5秒再尝试

        # 超时处理
        self.error_alart(message=f"Weberror? Cant click_element {element}")
        return False

    def debug_find_table_link(self, key=0):
        xpath_expression = "//*[contains(@class, 'cl123ick_link')]"
        element = WebDriverWait(self.driver, 10).until(ec.presence_of_element_located((By.XPATH, xpath_expression)))
        element.click()

    def click_table_link(self, key=0):
        self.log.log_message(f"ready click_table_link {key}", 1)
        xpath_expression = "//*[contains(@class, 'click_link')]"
        elements = self.try_find_elements(xpath_expression)
        length = len(elements)
        if key == 0 and length > 2:
            element = elements[length - 3]
            self.click_element(element)
        elif key > 0 and length > 0:
            element = elements[key - 1]
            self.click_element(element)
        else:
            self.error_alart(f"Error for click_table_link! key = {key}")
        self.log.log_message(f"success click_table_link {key}", 1)

    # 等待表格转圈完毕

    def login(self):
        pass

    def clue_distribute(self):
        self.log.log_message(f"start clue_distribute")
        xpath_exp = ".//span[contains(@class, 'click_link')]"
        name_eles = self.try_find_elements(xpath_exp)
        name_ele = name_eles[0]
        name = name_ele.text
        time.sleep(1)
        self.click_table_link(key=1)
        # xpath_exp = "//div[contains(@class, 'el-dialog') and contains(@aria-label, '线索详情')]"
        xpath_exp = "//div[contains(@class, 'el-dialog__wrapper') and not(contains(@style, 'display: none;')) and .//span[text()='线索详情']]"
        correct_label = self.try_find_element(xpath_exp, None, 0.8)
        # xpath_exp = ".//div[contains(@class, 'el-select') and contains(@class, 'el-select--mini') and contains(text(), '选择客户经理')]"
        xpath_exp = ".//input[contains(@placeholder, '选择客户经理')]"
        element = self.try_find_element_from(correct_label, xpath_exp)
        self.click_element(element)
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

        min_num = 999999
        min_index = -1
        min_name = ""
        for min_name in name_list:
            if min_name[1] < min_num:
                min_num = min_name[1]
                min_index = min_name[2]
        for sub_name in name_list_mid:
            if len(sub_name) > 0 and sub_name[0] == min_name:
                min_num = -1
                break

        if min_num < 0:
            self.click_element(ele_dropdowns[min_index])
        else:
            self.error_alart("min_num < 0")

        # 添加数据到数据库中

        # "//textarea[@placeholder='请输入备注内容']"
        texture = "线索清洗auto"
        xpath_exp = "//textarea[@placeholder='请输入备注内容']"
        textarea = self.try_find_element_from(correct_label, xpath_exp)
        textarea.clear()
        textarea.send_keys(texture)
        # 点击确定，确定，未验证
        xpath_exp = ".//span[contains(text(), '确定')]"
        element = self.try_find_element_from(correct_label, xpath_exp)
        self.click_element(element)
        xpath_exp = ".//div[contains(@class, 'el-message-box__wrapper') and contains(@aria-label, '提示')]"
        element_sure = self.try_find_element(xpath_exp)
        xpath_exp = ".//span[contains(text(), '确定')]"
        # xpath_exp = "//button[span[text()='确定']]"
        element = self.try_find_element_from(element_sure, xpath_exp)
        self.click_element(element)
        self.log.log_message(f"success clue_clear！{name}")

    def debug_clue_distribute(self):
        xpath_exp = "//div[contains(@class, 'el-dialog') and contains(@aria-label, '线索详情')]"
        correct_label = self.try_find_element(xpath_exp)
        # xpath_exp = ".//div[contains(@class, 'el-select') and contains(@class, 'el-select--mini') and contains(text(), '选择客户经理')]"
        xpath_exp = ".//input[contains(@placeholder, '选择客户经理')]"
        element = self.try_find_element_from(correct_label, xpath_exp)
        self.click_element(element)
        xpath_exp = ".//div[contains(@class, 'el-select-dropdown') and contains(@class, 'el-popper') and not(contains(@style, 'display: none;'))]"
        element_sele = self.try_find_element(xpath_exp)
        xpath_exp = ".//li[contains(@class, 'el-select-dropdown__item')]"
        ele_dropdowns = self.try_find_elements_from(element_sele, xpath_exp)
        for element in ele_dropdowns:
            print(element.text)

    # 线索清洗实现函数
    def clue_clear(self):
        self.log.log_message(f"start clue_clear")
        xpath_exp = ".//span[contains(@class, 'click_link')]"
        name_eles = self.try_find_elements(xpath_exp)
        name_ele = name_eles[0]
        name = name_ele.text
        self.click_table_link(key=1)
        xpath_exp = "//div[contains(@class, 'el-dialog__wrapper') and not(contains(@style, 'display: none;')) and .//span[text()='线索详情']]"
        correct_label = self.try_find_element(xpath_exp)

        value = self.read_label_from_popup_safely("意向车系")
        print(f"value = {value}")
        if value == "" or value is None:
            self.log.log_message(f"None of car choice")
            xpath_exp = ".//label[contains(text(), '意向车系')]"
            element = self.try_find_element_from(correct_label, xpath_exp)
            xpath_exp = ".."
            parent_ele = self.try_find_element_from(element, xpath_exp)
            xpath_exp = ".//div[contains(@class, 'el-select') and contains(@class, 'el-select--mini')]"
            content = self.try_find_element_from(parent_ele, xpath_exp)
            self.click_element(content)
            # 点出选择菜单
            # 选择好车系
            # el-select-dropdown el-popper is-multiple
            xpath_exp = ".//div[contains(@class, 'el-select-dropdown') and contains(@class, 'el-popper') and contains(@class, 'is-multiple') and not(contains(@style, 'display: none;'))]"
            element_sele = self.try_find_element_from(element, xpath_exp)
            # el-select-dropdown__item
            xpath_exp = ".//li[contains(@class, 'el-select-dropdown__item')]"
            ele = self.try_find_element_from(element_sele, xpath_exp)
            self.click_element(ele)

        # "//textarea[@placeholder='请输入备注内容']"
        texture = "线索清洗auto"
        xpath_exp = "//textarea[@placeholder='请输入备注内容']"
        textarea = self.try_find_element_from(correct_label, xpath_exp)
        textarea.clear()
        textarea.send_keys(texture)
        xpath_exp = ".//span[contains(text(), '确定')]"
        element = self.try_find_element_from(correct_label, xpath_exp)
        self.click_element(element)
        xpath_exp = ".//div[contains(@class, 'el-message-box__wrapper') and contains(@aria-label, '提示')]"
        element_sure = self.try_find_element(xpath_exp)
        xpath_exp = ".//span[contains(text(), '确定')]"
        # xpath_exp = "//button[span[text()='确定']]"
        element = self.try_find_element_from(element_sure, xpath_exp)
        self.click_element(element)
        self.log.log_message(f"success clue_clear！{name}")

    def clue_follow(self):
        self.click_on_subhead(1)
        self.wait_table_load()
        self.click_table_link(1)
        # xpath_exp = "//button[contains(@class, 'el-button') and contains(@class, 'filter-item') and contains(@class, 'el-button--text') and contains(@class, 'el-button--medium') and span[text()='跟进']]"
        xpath_exp = "//button[contains(@class, 'el-button filter-item el-button--text el-button--medium') and .//span[text()='跟进']]"
        self.find_click_on_ele(xpath_exp)
        xpath_exp = "//div[contains(@class, 'el-dialog') and not(contains(@style, 'display: none;')) and contains(@aria-label, '完成跟进')]"
        correct_label = self.try_find_element(xpath_exp)
        xpath_exp = "//span[contains(@class, 'el-radio-button__inner') and text()='邀约到店']"
        element_ways = self.try_find_element_from(correct_label, xpath_exp)
        self.click_element(element_ways)

        # "//textarea[@placeholder='请输入备注内容']"
        texture = "线索清洗auto"
        xpath_exp = "//textarea[@placeholder='请输入备注内容']"
        textarea = self.try_find_element_from(correct_label, xpath_exp)
        textarea.clear()
        textarea.send_keys(texture)
        xpath_exp = ".//span[contains(text(), '确定')]"
        element = self.try_find_element_from(correct_label, xpath_exp)
        self.click_element(element)
        # xpath_exp = ".//div[contains(@class, 'el-message-box__wrapper') and contains(@aria-label, '提示')]"
        # element_sure = self.try_find_element(xpath_exp)
        # xpath_exp = ".//span[contains(text(), '确定')]"
        # # xpath_exp = "//button[span[text()='确定']]"
        # element = self.try_find_element_from(element_sure, xpath_exp)
        # self.click_element(element)
        self.log.log_message(f"success clue_follow！")

    def check_loop(self):
        self.click_on_head(2)
        self.click_on_subhead(2)
        while True:
            time.sleep(0.5)
            self.click_on_radio_button(2)
            if self.check_item_count() != 0:
                self.clue_distribute()
                self.clue_follow()
                self.driver.refresh()
                self.click_on_subhead(2)

            self.click_on_radio_button(1)
            if self.check_item_count() != 0:
                self.clue_clear()

    def ready_start(self):
        self.click_on_head(2)
        self.click_on_subhead(2)
        self.check_loop()
        pass

    def get_phone_from_text(self, text):
        phone_numbers = []
        for item in text:  # 使用正则表达式提取横杠后面的11位手机号
            match = re.search(r"- (\d{11})", item)
            if match:
                phone_number = int(match.group(1))
                phone_numbers.append(phone_number)
        return phone_numbers

    # def read_label_from_popup(self, key):
    #     xpath_exp = f"//label[contains(text(), '{key}')]/.."
    #     label = self.try_find_element(xpath_exp)
    #     xpath_exp = "el-form-item__content"
    #     return label.find_element(By.CLASS_NAME, "el-form-item__content").text

    # 仅可用于线索清洗时使用
    def read_label_from_popup_safely(self, label, count=0):
        self.log.log_message("start read_label_from_popup_safely!", 1)
        xpath_exp = "//div[contains(@class, 'el-dialog') and not(contains(@style, 'display: none;')) and contains(@aria-label, '线索详情')]"
        table = self.try_find_element(xpath_exp)
        # "el-form-item form_item"
        xpath_exp = f".//div[contains(@class, 'el-form-item') and contains(@class, 'form_item') and .//label[contains(text(), '{label}')]]"
        element = self.try_find_element_from(table, xpath_exp)
        # el-form-item__content
        xpath_exp = ".//div[contains(@class, 'el-form-item__content')]"
        value = self.try_find_element_from(element, xpath_exp).text
        self.log.log_message("success read_label_from_popup_safely!", 1)
        return value

    # title = ["id", "手机号", "姓名", "意向车系", "来源平台", "参与活动", "线索类别", "购车地区", "线索创建时间", "客户经理", "客户级别", "有效跟进时间"]
    def read_customer_in_table(self, title):
        self.log.log_message("read to read_customer_in_table", 1)
        self.driver.implicitly_wait(0)
        st = []
        for label in title:
            value = self.read_label_from_popup_safely(f"{label}", 0)
            self.log.log_message(f"label = {label}, value = {value}", 1)
            if value:
                st.append([label, value])
        # 恢复隐式等待
        self.driver.implicitly_wait(self.timeout)
        self.log.log_message("success to read_customer_in_table", 1)
        return st

    # 线索分配读取弹出表格内容
    def read_clue_clear_customer(self):
        title = ["姓名", "意向车系", "来源平台", "参与活动", "线索类别", "购车地区", "线索创建时间"]
        st = self.read_customer_in_table(title)
        phone = self.read_label_from_popup_safely("手机号")
        self.log.log_message(f"手机号 = {phone}", 1)
        zdata = ZZData()
        self.log.log_message(f"st = {st}", 1)
        zdata.add_or_update_batch(phone, st)
        self.log.log_message(f"success read_clue_clear_customer", 1)
        return phone

    def read_customer_manager(self):
        self.click_on_head(3)
        self.driver.refresh()
        self.wait_table_load()

        pass


#debug
def testclickonhead():
    test = Page_Driver()
    test.log.start_log()
    test.de_open_exist_page()
    # test.open_new_web_visible()
    # test.check_loop()
    test.debug_wait_table_load()


def main():
    testclickonhead()
    return


if __name__ == "__main__":
    main()
