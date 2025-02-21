start_time = time.time()
while mark == self.check_item_count():
    if time.time() - start_time > self.timeout:
        self.driver.refresh()
        self.click_on_radio_button(6)
        start_time = time.time()
    time.sleep(0.5)

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