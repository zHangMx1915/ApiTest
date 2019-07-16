# coding=utf-8
from file_tools import operation_csv, operation_json
from core import runmethod
from test_report import html, send_email
import time
import json
from tools import assertion


case_num = []


def get_rely_data(re_value, key_name):
    """
    :param re_value: 依赖的接口返回的值
    :param key_name: 需要查找的值
    :return: 返回查找到的值
    """
    rely_value = None
    for key, value in re_value.items():
        if key == key_name:
            rely_value = value
        elif type(value) is dict or key == key_name:
            rely_value = get_rely_data(value, key_name)
        elif type(value) is list or key == key_name:
            for i in value:
                rely_value = get_rely_data(i, key_name)
    return rely_value


def rely_api(case_list, rely_case, url, rely_data):
    """
    :param case_list: 用例文件
    :param rely_case: 有依赖的的用例
    :param url: url
    :param rely_data: 依赖的关键字
    :return: 从依赖接口返回的数据中查找到需要的值
    """
    datas = {}
    for i in case_list:
        if i['CaseId'] == rely_case['依赖id']:
            data = operation_json.check_data(i)
            re_value = runmethod.run_url(i['请求类型'], url + i['api'], data, i['header'])
            rely_value = get_rely_data(re_value, rely_data)
            datas[rely_data] = rely_value
            return datas


def report(i, re_data, final, smu):
    re_sum = []
    re_sum.append(i['CaseId'])
    re_sum.append(i['名称'])
    re_sum.append(i['api'])
    re_sum.append(i['请求类型'])
    re_sum.append(i['请求数据'])
    re_sum.append(i['依赖id'])
    re_sum.append(re_data['status'])
    if smu is True:
        re_sum.append(re_data)
    else:
        re_sum.append(smu)
    re_sum.append(final)
    case_num.append(re_sum)


def get_case(file_name, url_name):
    case_list = operation_csv.read_csv(file_name)
    url = operation_json.get_config(url_name)
    for i in case_list:
        if i['run'] == 'yes':
            data = operation_json.check_data(i)
            if i['依赖id']:
                data = rely_api(case_list, i, url, i['依赖参数'])
            re_data = runmethod.run_url(i['请求类型'], url + i['api'], data, i['header'])
            smu = assertion.compare_json_data(json.dumps(re_data, ensure_ascii=False), (i['预期结果']).strip())   # strip(): 首尾去空格
            if smu is True:
                report(i, re_data, 'pass', smu)
            else:
                report(i, re_data, 'fail', smu)
            print(i['CaseId'], smu)


if __name__ == '__main__':
    start = time.process_time()     # 开始时间
    file_case = 'ApiCase.csv'
    url_case = "url_name"    # 'url_IP'  "url_name"
    get_case(file_case, url_case)
    end = time.process_time()       # 结束时间
    run_time = end - start
    file_name = '测试报告' + (time.strftime("%Y-%m-%d %H-%M", time.localtime()))         # 测试报告名称，当前时间
    html.generate_html(file_name, run_time, case_num)
    # send_email.file_mail("TestReport", file_name, operation_json.get_config('email'))    # 发送邮件
