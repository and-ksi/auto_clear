import logging
import os
from datetime import datetime
import configparser
import tkinter as tk
import requests
import pyodbc
import win32com.client as win32


class Post_Message:
    def __init__(self):
        self.log = Log_save(l_level="Debug")
        self.url = "https://wxpusher.zjiecode.com/api/send/message"
        self.appToken = "AT_ctBuoL9g9rFvk8uBogW0Bd0WSC6QMhuE"
        uid_conf = ConfigManager()
        self.name_uid = uid_conf.get_all_uid()
        pass

    def post_error(self, message):
        data = {
            "appToken": f"{self.appToken}",
            "content": f"<h1>运行错误,程序已经停止！</h1><br/><p style=\"color:red;\">{message}</p>",
            "summary": "<span style='color:red;'>py错误，已停止</span>",
            "contentType": 2,
            "topicIds": [],
            "uids": [],
            "verifyPay": False,
            "verifyPayType": 0
        }
        for uid in self.name_uid:
            data["uids"].append(uid[1])

        # 发送 POST 请求
        response = requests.post(self.url, json=data)
        # 检查响应状态码
        if response.status_code == 200:
            self.log.log_message("post请求成功！")
            self.log.log_message("响应数据：", response.json())
        else:
            self.log.log_message(f"请求失败，状态码：{response.status_code}")
            self.log.log_message("错误信息：", response.text)
        pass

    def error_alart(self, title="Error", message="这是一个保持在桌面显示的弹窗", error_mark=0):
        # self.log.log_message(message=message, mark=4)
        self.post_error(message)
        """显示一个保持在桌面显示的弹窗"""
        try:
            def keep_on_top(root):
                """使窗口保持在最前端"""
                root.attributes("-topmost", True)
                root.after(1000, lambda: keep_on_top(root))

            def close_window(root):
                """关闭窗口"""
                root.destroy()

            root = tk.Tk()
            root.title("线索清洗出错")

            # 将窗口设置为全屏
            root.attributes("-fullscreen", True)

            # 创建一个标签显示消息，并设置背景为红色，文字为黑色
            label = tk.Label(root, text="线索清洗出错", font=("Helvetica", 24), bg="red", fg="black")  # 字体大小适当调大以适
            label.pack(expand=True)

            # 创建一个关闭按钮
            close_button = tk.Button(root, text="关闭", command=lambda: close_window(root), font=("Helvetica", 24),
                                     bg="white", fg="black")
            close_button.pack()

            # 窗口保持在最前端
            keep_on_top(root)

            # 启动主循环
            root.mainloop()
        except:
            pass
        if error_mark:
            return error_mark
        else:
            raise SystemExit


class ConfigManager:
    def __init__(self):
        # 获取当前程序的运行路径
        current_directory = os.getcwd()
        # 定义日志目录为当前路径下的 log 文件夹
        config_file = os.path.join(current_directory, 'config.ini')
        self.config_file = config_file
        self.config = configparser.ConfigParser()

        # 如果配置文件存在，则读取它
        if os.path.exists(config_file):
            self.config.read(config_file)
        else:
            # 创建一个默认的配置文件
            self.default_config()
            self.save_config()

    def add_or_update_name(self, name, level=0):
        """
        参数为(name, level=0)，如果名字已经存在，直接修改名字后的数字为level；
        如果名字不存在，把名字和level代表的数字添加到config文件中
        """
        if not self.config.has_section('NAME_LIST'):
            self.config.add_section('NAME_LIST')

        self.config['NAME_LIST'][name] = str(level)
        self.save_config()

    def get_all_names(self):
        """
        调用后，返回一个二维数组，关于名字和数字的
        """
        if not self.config.has_section('NAME_LIST'):
            return []

        return [[name, int(level)] for name, level in self.config.items('NAME_LIST')]

    def remove_name(self, name):
        """
        参数为name，调用后，从config中删除name和后面的数字
        """
        if self.config.has_section('NAME_LIST') and self.config.has_option('NAME_LIST', name):
            self.config.remove_option('NAME_LIST', name)
            self.save_config()

    def add_string_group(self, name, label, value):
        """
        写入时只需要输入三个字符串，自动按照当前内容顺序生成从1开始的id
        """
        if not self.config.has_section('RULES'):
            self.config.add_section('RULES')

        # 获取当前最大 ID
        max_id = 0
        if len(self.config.items('RULES')) > 0:
            max_id = max(int(key.split('_')[0]) for key in self.config['RULES'].keys())

        new_id = max_id + 1
        self.config['RULES'][f'{new_id}_name'] = name
        self.config['RULES'][f'{new_id}_label'] = label
        self.config['RULES'][f'{new_id}_value'] = value
        self.save_config()

    def get_all_string_groups(self):
        """
        读取时会返回四维数组所有内容
        """
        if not self.config.has_section('RULES'):
            return []

        groups = {}
        for key, value in self.config.items('RULES'):
            group_id, attr = key.split('_')
            if group_id not in groups:
                groups[group_id] = {}
            groups[group_id][attr] = value

        return [[int(group_id), data['name'], data['label'], data['value']] for group_id, data in groups.items()]

    def remove_string_group(self, group_id):
        """
        删除时会删除指定id的数组，并把剩余的数组按照顺序重新把id排序
        """
        if not self.config.has_section('RULES'):
            return

        keys_to_remove = [key for key in self.config['RULES'].keys() if key.startswith(f'{group_id}_')]
        for key in keys_to_remove:
            self.config.remove_option('RULES', key)

        # 重新排序剩余的数组
        groups = self.get_all_string_groups()
        self.config.remove_section('RULES')
        self.config.add_section('RULES')
        for new_id, group in enumerate(groups, 1):
            self.config['RULES'][f'{new_id}_name'] = group[1]
            self.config['RULES'][f'{new_id}_label'] = group[2]
            self.config['RULES'][f'{new_id}_value'] = group[3]

        self.save_config()

    def add_name_uid(self, name, uid):
        if not self.config.has_section('NAME_UIDs'):
            self.config.add_section('NAME_UIDs')
        self.config['NAME_UIDs'][name] = str(uid)
        self.save_config()
        pass

    def get_all_uid(self):
        if not self.config.has_section('NAME_UIDs'):
            return []

        return [[name, uid] for name, uid in self.config.items('NAME_UIDs')]
        pass

    def remove_uid(self, name):
        if self.config.has_section('NAME_UIDs') and self.config.has_option('NAME_UIDs', name):
            self.config.remove_option('NAME_UIDs', name)
            self.save_config()
        pass

    def default_config(self):
        self.config['NAME_LIST'] = {
            '韩敏': '100',
            '王亚城': '1',
            '刘毅强': '1',
            '王亮': '1',
            '董金涛': '1',
            '王云田': '1',
            '鲍国庆': '1',
            '韩鹏远': '1',
        }
        self.config['NAME_UIDs'] = {
            '韩敏': 'UID_sNCsMWsVb2G0g6DEJpDAHT5vGs9f',
            '清洗员': 'UID_dBjKN9UIkvXggPC0NipFYGXBTAJw'
        }

    def save_config(self):
        """
        保存配置到文件
        """
        with open(self.config_file, 'w') as configfile:
            self.config.write(configfile)


class Log_save:
    def __init__(self, l_level=None):
        # 记录日志文件名以及位置，但不创建日志记录器
        current_directory = os.getcwd()
        log_directory = os.path.join(current_directory, 'log')
        current_time = datetime.now().strftime("%Y%m%d")
        self.log_filename = f'zzwork-{current_time}.log'
        self.log_file_path = os.path.join(log_directory, self.log_filename)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)

        self.l_level = l_level
        self.logger = None

    def _initialize_logger(self):
        # 创建新的日志记录器
        self.logger = logging.getLogger(__name__ + str(id(self)))
        file_handler = logging.FileHandler(self.log_file_path)
        file_handler.setLevel(logging.DEBUG if self.l_level else logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s',
                                      datefmt='%Y-%m-%d %H:%M:%S')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        self.logger.setLevel(logging.DEBUG if self.l_level else logging.INFO)

        # 存储处理程序以便以后关闭
        self.file_handler = file_handler

    def close(self):
        if self.logger:
            self.file_handler.close()
            self.logger.removeHandler(self.file_handler)

    def start_log(self):
        self._initialize_logger()
        self.logger.info("***********************************************")
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.logger.info(f"Log start in {current_time}")
        self.close()

    def log_message(self, message, mark=2):
        self._initialize_logger()
        if mark == 1:
            self.logger.debug(f"{message}")
        elif mark == 2:
            self.logger.info(f"{message}")
        elif mark == 3:
            self.logger.warning(f"{message}")
        elif mark == 4:
            self.logger.error(f"{message}")
        else:
            self.logger.error(f"Log mark error!")
        self.close()


class ZZData:
    log = Log_save()
    labels_title = ["手机号", "姓名", "客户经理", "客户级别", "意向车系", "来源平台", "参与活动", "线索类别",
                    "购车地区", "线索创建时间", "有效跟进时间"]

    def __init__(self):
        self.error = Post_Message()
        # 获取当前程序的运行路径
        current_directory = os.getcwd()
        # 定义日志目录为当前路径下的 log 文件夹
        db_directory = os.path.join(current_directory, 'database')

        db_filename = f'zzwork-database.accdb'
        db_file_path = os.path.join(db_directory, db_filename)
        if not os.path.exists(db_file_path):
            os.makedirs(db_directory)

        self.db_path = db_file_path

        # 检查数据库文件是否存在
        if not os.path.exists(self.db_path):
            self.create_database()

        connection_string = r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=' + self.db_path
        try:
            self.conn = pyodbc.connect(connection_string)
            self.log.log_message("Connected to database successfully")
        except pyodbc.Error as e:
            print("Error while connecting to database:", e)
            self.log.log_message(f"Error while connecting to database: {e}", 4)
            self.error.error_alart(message=f"Error while connecting to database: {e}")

        self.czzdata = self.conn.cursor()
        self.create_table()
        pass

    def create_database(self):
        # 使用win32com.client创建一个空的Access数据库
        access = win32.Dispatch('Access.Application')
        # access.DBEngine.CreateDatabase(self.db_path, win32com.client.constants.dbLangGeneral)
        access.DBEngine.CreateDatabase(self.db_path, ';LANGID=0x0409')
        access.Quit()
        self.log.log_message(f"Database created at {self.db_path}")
        pass

    def create_table(self):
        create_table_query = ''' 
            CREATE TABLE zzData ( id AUTOINCREMENT PRIMARY KEY, 
            手机号 TEXT, 
            姓名 TEXT, 
            客户经理 TEXT, 
            客户级别 TEXT, 
            意向车系 TEXT, 
            来源平台 TEXT, 
            参与活动 TEXT, 
            线索类别 TEXT, 
            购车地区 TEXT, 
            线索创建时间 TEXT, 
            有效跟进时间 TEXT ) 
            '''
        try:
            self.czzdata.execute(create_table_query)
            self.conn.commit()
            self.log.log_message("Table created successfully", 1)
        except pyodbc.Error as e:
            # 如果表已经存在，忽略错误
            if "already exists" in str(e):
                self.log.log_message(f"Table already exists, skipping creation.")
            else:
                self.log.log_message(f"Error while creating table: {e}", 4)
                self.error.error_alart(message=f"Error while creating table: {e}")

    pass

    def add_or_update(self, phone, label, value):
        self.czzdata.execute('SELECT * FROM zzData WHERE 手机号=?', (phone,))
        record = self.czzdata.fetchone()
        if record:
            # 更新记录
            self.czzdata.execute(f'UPDATE zzData SET {label}=? WHERE 手机号=?', (value, phone))
            self.log.log_message(f"UPDATE zzData SET {label}={value} WHERE 手机号={phone}", 1)
        else:
            # 插入新记录
            self.czzdata.execute(f'INSERT INTO zzData (手机号, {label}) VALUES (?, ?)', (phone, value))
            self.log.log_message(f"INSERT INTO zzData (手机号, {label}) VALUES ({phone}, {value})", 1)
        self.conn.commit()

    def add_or_update_batch(self, phone, data):
        self.czzdata.execute('SELECT * FROM zzData WHERE 手机号=?', (phone,))
        record = self.czzdata.fetchone()
        if record:
            # 更新记录
            for label, value in data:
                self.log.log_message(f"UPDATE zzData SET {label}={value} WHERE 手机号={phone}")
                self.czzdata.execute(f'UPDATE zzData SET {label}=? WHERE 手机号=?', (value, phone))
        else:
            # 插入新记录
            columns = ['手机号'] + [label for label, value in data]
            placeholders = ', '.join(['?'] * len(columns))
            values = [str(phone)] + [str(value) for label, value in data]  # 确保所有值为字符串
            self.log.log_message(f"INSERT INTO zzData ({', '.join(columns)}) VALUES ({', '.join(values)})")
            sql_query = f'INSERT INTO zzData ({", ".join(columns)}) VALUES ({placeholders})'
            self.czzdata.execute(sql_query, values)
        self.conn.commit()

    def query_value(self, phone, label):
        self.czzdata.execute(f'SELECT {label} FROM zzData WHERE 手机号=?', (phone,))
        result = self.czzdata.fetchone()
        return result[0] if result else None

    def query_values(self, phone, labels=None):
        if labels is None:
            labels = self.labels_title
        values = []
        for label in labels:
            value = self.query_value(phone, label)
            values.append(value)
        return values
