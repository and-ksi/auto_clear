import logging
import os
from datetime import datetime


class Log_save:
    def __init__(self, l_level=None):
        log_directory = 'D:\\file\\python\\project\\zzwork\\zzwork\\logs'
        current_time = datetime.now().strftime("%Y%m%d")
        log_filename = f'zzwork-{current_time}.log'
        log_file_path = os.path.join(log_directory, log_filename)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        # 创建新的日志处理器
        file_handler = logging.FileHandler(log_file_path)
        file_handler.setLevel(logging.DEBUG if l_level else logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                                      datefmt='%Y-%m-%d %H:%M:%S')
        file_handler.setFormatter(formatter)

        # 获取全局的日志记录器并添加新的处理器
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(file_handler)
        self.logger.setLevel(logging.DEBUG if l_level else logging.INFO)
        self.logger = logging.getLogger(__name__)

    def start_log(self):
        self.logger.info(f"***********************************************")
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.logger.info(f"Log start in {current_time}")

    def log_message(self, message, mark=2):
        # logger = self.logging.getLogger(__name__)
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
