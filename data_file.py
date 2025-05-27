import logging
import os
from datetime import datetime
import configparser
import tkinter as tk
import requests
import mysql.connector
import sys
from mysql.connector import errorcode


class Post_Message:
    def __init__(self):
        self.log = Log_save(l_level="Debug")
        config = ConfigManager()
        self.url = config.get_data('ACCOUNT', 'post_url')
        self.appToken = config.get_data('ACCOUNT', 'post_apptoken')
        uid_conf = ConfigManager()
        self.name_uid = uid_conf.get_all_uid()
        pass

    def post_error(self, message, title="py错误，已停止"):
        data = {
            "appToken": f"{self.appToken}",
            "content": f"<h1>程序已经停止！</h1><br/><p style=\"color:red;\">{message}</p>",
            f"summary": f"<span style='color:red;'>{title}</span>",
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
            self.log.log_message(f"错误信息： {response.text}")
        pass

    def error_alart(self, title="Error", message="这是一个保持在桌面显示的弹窗", error_mark=0):
        # self.log.log_message(message=message, mark=4)
        self.post_error(message)
        """显示一个保持在桌面显示的弹窗"""
        try:
            if sys.platform.startswith("win"):

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
        # 配置文件路径
        self.config_file = os.path.join(current_directory, 'config.ini')
        self.config = configparser.ConfigParser()

        # 如果配置文件存在，则使用 UTF-8 读取它
        if os.path.exists(self.config_file):
            with open(self.config_file, "r", encoding="utf-8") as f:
                self.config.read_file(f)
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

        return [[name, float(level)] for name, level in self.config.items('NAME_LIST')]

    def remove_name(self, name):
        """
        参数为name，调用后，从config中删除name和后面的数字
        """
        if self.config.has_section('NAME_LIST') and self.config.has_option('NAME_LIST', name):
            self.config.remove_option('NAME_LIST', name)
            self.save_config()

    def get_account(self):
        if not self.config.has_section('ACCOUNT'):
            return ["", ""]  # 返回空值，避免 KeyError

        account = self.config.get('ACCOUNT', 'account', fallback="")
        password = self.config.get('ACCOUNT', 'password', fallback="")
        return [account, password]

    def change_account(self, account, password):
        if not self.config.has_section('ACCOUNT'):
            self.config.add_section('ACCOUNT')

        self.config['ACCOUNT']['account'] = account
        self.config['ACCOUNT']['password'] = password
        self.save_config()

    def get_code(self):
        # 重新读取配置文件，确保获取最新的内容
        self.config = configparser.ConfigParser()
        with open(self.config_file, "r", encoding="utf-8") as f:
            self.config.read_file(f)
        if not self.config.has_section('ACCOUNT'):
            return ""  # 返回空字符串，避免 KeyError
        # 获取 code 值，去除前后空格
        code = self.config.get('ACCOUNT', 'code', fallback="").strip()
        # 检查是否为 6 位
        if len(code) != 6:
            return ""  # 长度不符合则返回空值，但 **不删除 code**
        # 清空 code（只有在长度为 6 的情况下才删除）
        self.config.set('ACCOUNT', 'code', '')
        # 保存修改
        with open(self.config_file, 'w', encoding='utf-8') as configfile:
            self.config.write(configfile)  # 确保清空数据生效
        return code

    def get_data(self, section, key):
        if not self.config.has_section(section):
            return None
        ret = self.config.get(section, key, fallback="")
        return ret

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
        self.config['ACCOUNT'] = {
            'account': '17314368529',
            'password': 'and123456',
            'code': ''
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
        sanitized_message = self.sanitize_message(message)
        self._initialize_logger()
        if mark == 1:
            self.logger.debug(f"{sanitized_message}")
        elif mark == 2:
            self.logger.info(f"{sanitized_message}")
        elif mark == 3:
            self.logger.warning(f"{sanitized_message}")
        elif mark == 4:
            self.logger.error(f"{sanitized_message}")
        else:
            self.logger.error(f"Log mark error!")
        self.close()

    def sanitize_message(self, message):
        return message.encode("utf-8", errors="replace").decode("utf-8")


class ZZData:
    log = Log_save()
    labels_title = ["手机号", "姓名", "客户经理", "客户级别", "意向车系", "来源平台", "参与活动", "线索类别",
                    "购车地区", "线索创建时间", "有效跟进时间"]

    def __init__(self):
        self.error = Post_Message()

        config = ConfigManager()
        self.sql_usr = config.get_data('ACCOUNT', 'sql_usr')
        self.sql_password = config.get_data('ACCOUNT', 'sql_password')
        self.sql_host = config.get_data('ACCOUNT', 'sql_host')
        self.sql_database = config.get_data('ACCOUNT', 'sql_database')

        # 设置MySQL连接参数
        self.db_config = {
            'user': self.sql_usr,
            'password': self.sql_password,
            'host': self.sql_host,
            'database': self.sql_database
        }

        # 创建数据库连接
        try:
            self.conn = mysql.connector.connect(**self.db_config)
            self.log.log_message("Connected to database successfully")
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                self.log.log_message("Something is wrong with your user name or password", 4)
                self.error.error_alart(message="Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                self.log.log_message("Database does not exist. Creating database...", 4)
                self.create_database()  # **实际调用创建数据库**
                # **尝试重新连接**
                try:
                    self.conn = mysql.connector.connect(**self.db_config)
                    self.log.log_message("Reconnected to newly created database")
                except mysql.connector.Error as err:
                    self.log.log_message(f"Failed to reconnect after creating database: {err}", 4)
                    self.error.error_alart(message=f"Failed to reconnect: {err}")
            else:
                self.log.log_message(repr(err), 4)
                self.error.error_alart(message=repr(err))

        self.create_table()

    def create_database(self):
        try:
            db_config_no_db = self.db_config.copy()
            if "database" in db_config_no_db:
                db_config_no_db.pop("database")  # **确保不会 KeyError**

            conn_no_db = mysql.connector.connect(**db_config_no_db)
            cursor = conn_no_db.cursor()
            cursor.execute(f"CREATE DATABASE {self.sql_database} DEFAULT CHARACTER SET 'utf8'")
            self.log.log_message("Database created successfully")
            cursor.close()
            conn_no_db.close()
        except mysql.connector.Error as err:
            self.log.log_message(f"Failed creating database: {err}", 4)
            self.error.error_alart(message=f"Failed creating database: {err}")

    def create_table(self):
        create_table_query = '''
            CREATE TABLE IF NOT EXISTS zzData (
                id INT AUTO_INCREMENT PRIMARY KEY,
                手机号 VARCHAR(255),
                姓名 VARCHAR(255),
                客户经理 VARCHAR(255),
                客户级别 VARCHAR(255),
                意向车系 VARCHAR(255),
                来源平台 VARCHAR(255),
                参与活动 VARCHAR(255),
                线索类别 VARCHAR(255),
                购车地区 VARCHAR(255),
                线索创建时间 VARCHAR(255),
                有效跟进时间 VARCHAR(255)
            )
        '''
        try:
            cursor = self.conn.cursor()
            cursor.execute(create_table_query)
            self.conn.commit()
            self.log.log_message("Table created successfully")
            cursor.close()
        except mysql.connector.Error as err:
            self.log.log_message(f"Error while creating table: {err}", 4)
            self.error.error_alart(message=f"Error while creating table: {err}")

    def add_or_update(self, phone, label, value):
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM zzData WHERE 手机号=%s', (phone,))
            record = cursor.fetchone()
            if record:
                # 更新记录
                cursor.execute(f'UPDATE zzData SET {label}=%s WHERE 手机号=%s', (value, phone))
                self.log.log_message(f"UPDATE zzData SET {label}={value} WHERE 手机号={phone}")
            else:
                # 插入新记录
                cursor.execute(f'INSERT INTO zzData (手机号, {label}) VALUES (%s, %s)', (phone, value))
                self.log.log_message(f"INSERT INTO zzData (手机号, {label}) VALUES ({phone}, {value})")
            self.conn.commit()
            cursor.close()
        except mysql.connector.Error as err:
            self.log.log_message(f"Error while adding or updating: {err}", 4)
            self.error.error_alart(message=f"Error while adding or updating: {err}")

    def remove_duplicates(self, data):
        seen = set()
        result = []
        for item in data:
            if item[0] not in seen:
                result.append(item)
                seen.add(item[0])
        return result

    def add_or_update_batch(self, phone, sdata):
        data = self.remove_duplicates(sdata)
        cursor = None
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM zzData WHERE 手机号=%s', (phone,))
            record = cursor.fetchone()
            if record:
                # 更新记录
                for label, value in data:
                    self.log.log_message(f"UPDATE zzData SET {label}={value} WHERE 手机号={phone}")
                    cursor.execute(f'UPDATE zzData SET {label}=%s WHERE 手机号=%s', (value, phone))
            else:
                # 插入新记录
                columns = [label for label, value in data if label != '手机号']  # 排除手机号
                placeholders = ', '.join(['%s'] * len(columns))
                values = [value for label, value in data if label != '手机号']  # 排除手机号
                columns_str = ', '.join(['手机号'] + columns)
                placeholders_str = '%s, ' + placeholders
                values.insert(0, phone)
                self.log.log_message(f"INSERT INTO zzData ({columns_str}) VALUES ({placeholders_str})", 1)
                sql_query = f'INSERT INTO zzData ({columns_str}) VALUES ({placeholders_str})'
                cursor.execute(sql_query, values)
            self.conn.commit()
            cursor.close()
        except mysql.connector.Error as err:
            cursor.close()
            self.log.log_message(f"Error while batch adding or updating: {err}", 4)
            self.error.error_alart(message=f"Error while batch adding or updating: {err}")

    def query_value(self, phone, label):
        try:
            cursor = self.conn.cursor()
            cursor.execute(f'SELECT {label} FROM zzData WHERE 手机号=%s', (phone,))
            result = cursor.fetchone()
            cursor.close()
            return result[0] if result else None
        except mysql.connector.Error as err:
            self.log.log_message(f"Error while querying value: {err}", 4)
            self.error.error_alart(message=f"Error while querying value: {err}")
            return None

    def query_values(self, phone, labels=None):
        if labels is None:
            labels = self.labels_title
        values = []
        try:
            for label in labels:
                value = self.query_value(phone, label)
                values.append(value)
            return values
        except mysql.connector.Error as err:
            self.log.log_message(f"Error while querying values: {err}", 4)
            self.error.error_alart(message=f"Error while querying values: {err}")
            return values

    def __del__(self):
        # 在析构方法中关闭数据库连接
        try:
            if self.conn:
                self.conn.close()
            self.log.log_message("数据库连接已关闭")
        except Exception as e:
            self.log.log_message(f"关闭数据库连接时发生错误: {e}", 4)
            self.error.error_alart(message=f"关闭数据库连接时发生错误: {e}")

    def phone_exist(self, phone):
        try:
            cursor = self.conn.cursor()
            query = "SELECT 1 FROM zzData WHERE 手机号 = %s LIMIT 1"
            cursor.execute(query, (phone,))
            result = cursor.fetchone()
            cursor.close()
            return result is not None
        except mysql.connector.Error as err:
            self.log.log_message(f"Error occurred while checking phone existence: {err}", 4)
            self.error.error_alart(message=f"Error occurred while checking phone existence: {err}")
            return
