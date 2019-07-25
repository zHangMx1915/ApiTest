# coding=utf-8
from file_tools import operation_csv, operation_json
from core import runmethod
from test_report import html, Test_Html, send_email
import time
from tools import assertion


case_num = []


def get_rely_data_bak(re_value, key_name):
    # 返回所有符合规则的值的列表
    rely_value = []
    for key, value in re_value.items():
        if key == key_name:
            rely_value.append(value)
        elif type(value) is dict or key == key_name:
            rely_value.append(get_rely_data(value, key_name))
        elif type(value) is list or key == key_name:
            for i in value:
                rely_value.append(get_rely_data(i, key_name))
    return rely_value


def get_rely_data(re_value, key_name):
    """
    :param re_value: 依赖的接口返回的值
    :param key_name: 需要查找的值
    :return: 返回查找到的值
    """
    rely_value = None
    print(re_value)
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
            rely_value = get_rely_data(re_value.json(), rely_data)
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
    # re_sum.append(re_data['status'])
    try:
        re_sum.append(re_data['status'])
    except BaseException:
        re_sum.append(re_data.encoding)

    if smu is True:
        re_sum.append(re_data)
    else:
        re_sum.append(smu)
    re_sum.append(final)
    case_num.append(re_sum)


def report_yuanzu(smu, case_ji, case_run, case_error):
    if smu is True:
        i = 0
    else:
        i = 1


def get_case(file_name, url_name):
    case_list = operation_csv.read_csv(file_name)
    url = operation_json.get_config(url_name)
    for i in case_list:
        if i['run'] == 'yes':
            data = operation_json.check_data(i)
            if i['依赖id']:
                data = rely_api(case_list, i, url, i['依赖参数'])
            re_data = runmethod.run_url(i['请求类型'], url + i['api'], data, i['header'])
            try:
                re_data_sum = str(re_data.json())
            except:
                re_data_sum = re_data.text
            smu = assertion.re_requests(i['预期结果'].strip(), re_data_sum)
            # smu = assertion.compare_json_data(re_data_sum, i['预期结果'].strip())       #######       # """验证返回完整数据以及数据类型"""     # strip(): 首尾去空格
            if smu is True:
                report(i, re_data, 'pass', smu)
                print(i['CaseId'], smu)
            else:
                report(i, re_data, 'fail', smu)
                print(i['CaseId'], '▇▇▇预期：' + i['预期结果'].strip(), '-->>>实际：' + re_data_sum)


if __name__ == '__main__':
    start = time.process_time()     # 开始时间
    file_case = 'ApiCase.csv'
    url_case = "url_name"    # 'url_IP'  "url_name"
    get_case(file_case, url_case)
    end = time.process_time()       # 结束时间
    run_time = end - start
    file_name = '测试报告' + (time.strftime("%Y-%m-%d %H-%M", time.localtime()))         # 测试报告名称，当前时间
    html.generate_html(file_name, run_time, case_num)

    # 报告
    # report = '../test_file/ApiTest/log/创建用户测试报告%s.html' % time.strftime("%H-%M", time.localtime())
    # stdout = open(report, 'wb')
    # report = Test_Html.HTMLTestRunner(start, end, stdout, title='测试报告', description='用例执行情况')
    # report.run()
    # send_email.file_mail("TestReport", file_name, operation_json.get_config('email'))    # 发送邮件
