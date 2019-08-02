# coding=utf-8
import time
from test_report import Test_Html, html

def send_log(start, end, test_html_list):
    # 报告二
    report = '../TestLog/创建用户测试报告%s.html' % time.strftime("%H-%M", time.localtime())
    stdout = open(report, 'wb')
    report = Test_Html.HTMLTestRunner(start, end, stdout, title='TestBaogao', description='用例执行情况')
    report.run(test_html_list)


def send_log_tow(start, end, case_num):
    run_time = end - start
    file_name = 'TestBaogao' + (time.strftime("%Y-%m-%d %H-%M", time.localtime()))         # 测试报告名称，当前时间
    html.generate_html(file_name, run_time, case_num)
