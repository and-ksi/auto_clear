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
    print("1")
    ele = element_operate()
    ele.work_flow()
    pass

def main():
    # 仅在此处选择要运行的函数
    test()
    # 其他函数不会自动执行


if __name__ == "__main__":  # 明确程序入口
    main()  # 只执行 main() 中的内容