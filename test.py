from element_ctrl import element_operate
from data_file import Post_Message
import time


# def testclickonhead():
#     test = element_operate()
#     test.log.start_log()
#     test.open_new_web()
#     test.login_zz()
#     test.check_clue_loop()

def test():
    ele = element_operate()
    ele.switch_in()
    pass


def save_data_to_mysql():
    ele = element_operate()
    ele.log.start_log()
    ele.check_data_to_mysql()


def main():

    #test()
    save_data_to_mysql()
    # save_data_to_mysql()


if __name__ == "__main__":  # 明确程序入口
    main()  # 只执行 main() 中的内容
