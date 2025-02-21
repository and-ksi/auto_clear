import sqlite3
import configparser
import os, re
from datetime import datetime
from log_save import Log_save
import pyodbc
import win32com.client as win32
import win32com

# 全局变量，指定配置文件路径
con_path = 'D:\\file\\python\\project\\zzwork\\zzwork\\config.ini'
dbase_path = 'D:\\file\\python\\project\\zzwork\\zzwork\\zzWork_Data.accdb'


class ZZData:
    log = Log_save()
    labels_title = ["手机号", "姓名", "客户经理", "客户级别", "意向车系", "来源平台", "参与活动", "线索类别",
                    "购车地区", "线索创建时间", "有效跟进时间"]

    def __init__(self, db_path=dbase_path):
        self.db_path = db_path

        # 检查数据库文件是否存在
        if not os.path.exists(self.db_path):
            self.create_database()

        connection_string = r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=' + self.db_path
        try:
            self.conn = pyodbc.connect(connection_string)
            print("Connected to database successfully")
            self.log.log_message("Connected to database successfully", 1)
        except pyodbc.Error as e:
            print("Error while connecting to database:", e)
            self.log.log_message(f"Error while connecting to database: {e}", 1)

        self.czzdata = self.conn.cursor()
        self.create_table()

    def create_database(self):
        # 使用win32com.client创建一个空的Access数据库
        access = win32.Dispatch('Access.Application')
        # access.DBEngine.CreateDatabase(self.db_path, win32com.client.constants.dbLangGeneral)
        access.DBEngine.CreateDatabase(self.db_path, ';LANGID=0x0409')
        access.Quit()
        self.log.log_message(f"Database created at {self.db_path}", 1)
        print(f"Database created at {self.db_path}")

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
            print("Table created successfully")
            self.log.log_message("Table created successfully", 1)
        except pyodbc.Error as e:
            # 如果表已经存在，忽略错误
            if "already exists" in str(e):
                print("Table already exists, skipping creation.")
                self.log.log_message(f"Table already exists, skipping creation.", 1)
            else:
                print("Error while creating table:", e)
                self.log.log_message(f"Error while creating table: {e}", 3)

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


class ConfigManager:
    def __init__(self, config_file=con_path):
        self.config_file = config_file
        self.config = configparser.ConfigParser()

        # 如果配置文件存在，则读取它
        if os.path.exists(config_file):
            self.config.read(config_file)
        else:
            # 创建一个默认的配置文件
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

    def save_config(self):
        """
        保存配置到文件
        """
        with open(self.config_file, 'w') as configfile:
            self.config.write(configfile)

