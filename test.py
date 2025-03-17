from data_file import ZZData

from element_ctrl import element_operate

ele = element_operate()
ele.log.start_log()
ele.check_data_to_mysql()