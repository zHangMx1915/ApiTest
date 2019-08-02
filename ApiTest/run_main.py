# -*-coding:utf_8-*-
from file_tools import operation_csv, operation_json
from core import runmethod
from test_report import send_email, send_log
import time
from tools import assertion, rely
from file_tools.case_operation import case_generate


case_num = []
test_html_list = []


# 测试报告一
def report(i, re_data, final, smu):
    re_sum = []
    re_sum.append(i['CaseId'])
    re_sum.append(i['名称'])
    re_sum.append(i['api'])
    re_sum.append(i['请求类型'])
    re_sum.append(i['请求数据'])
    re_sum.append(i['依赖id'])
    # re_sum.append(re_data['status'])
    try:
        re_sum.append((re_data.json())['status'])
    except BaseException:
        re_sum.append(re_data.encoding)
    if smu is True:
        re_sum.append(re_data)
    else:
        re_sum.append(smu)
    re_sum.append(final)
    case_num.append(re_sum)


# 测试报告一
def report_yuanzu(i, re_data, finai, num=2):
    data_2 = "用例集" + i['CaseId'][0] + ',' + i['CaseId'] + '<br/>' + i['名称']
    re_sum = (num, data_2, str(re_data.text), '\n\n' + str(finai))
    test_html_list.append(re_sum)


def get_case(i, url, case_list, data):
    cookie, rely_run = None, None
    if i['run'] == 'yes':
        if i['依赖id']:
            data, cookie = rely.rely_api(case_list, i, url, i['依赖参数'])
            # report_yuanzu(i, cookie, finai, s)  # 报告二
        re_data, cookie = runmethod.run_url(i['请求类型'], url + i['api'], data, cookie)
        try:
            re_data_sum = re_data.json()
        except:
            re_data_sum = re_data.text
        smu = assertion.re_requests(i['预期结果'].strip(), re_data_sum)
        # smu = assertion.compare_json_data(re_data_sum, i['预期结果'].strip())   # 验证返回完整数据以及数据类型， strip(): 首尾去空格
        if smu is True:
            s, finai = 0, 'Pass: ' + i['预期结果']
        else:
            s, finai = 1, (
            'Fail: ', '▇▇▇ No expected results，预期Include：' + i['预期结果'].strip(), '-->>>实际：' + str(re_data_sum))
        # report(i, re_data, s, smu)                # 报告一
        report_yuanzu(i, re_data, finai, s)  # 报告二
        print(i['CaseId'], finai)
        return smu


def run_case(file_name, url_name):
    case_list = operation_csv.read_csv(file_name)
    url = operation_json.get_config(url_name)
    for i in case_list:
        data = operation_json.check_data(i)
        smu = get_case(i, url, case_list, data)
        # newCase
        if smu and data:
            new = case_generate.ProduRun()
            later = new.new_case(i, data)
            for j in later:
                get_case(j[0], url, case_list, j[1])


if __name__ == '__main__':
    start = time.process_time()     # 开始时间
    file_case = 'ApiCase.csv'
    url_case = "url_IP"    # 'url_IP'  "url_name"
    run_case(file_case, url_case)
    end = time.process_time()       # 结束时间
    # 报告一
    send_log.send_log(start, end, test_html_list)
    # 报告二
    # send_log.send_log_tow(start, end, case_num)
    # send_email.file_mail("TestReport", operation_json.get_config('email'))    # 发送邮件
