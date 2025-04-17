from data_file import ZZData

from element_ctrl import element_operate

ele = element_operate()
ele.log.start_log()

ele.de_open_exist_page()
ele.login_zz()


