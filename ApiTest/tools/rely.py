# -*-coding:utf_8-*-
from file_tools import operation_json
from core import runmethod


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
    for key, value in re_value.items():
        if key == key_name:
            rely_value = value
        elif type(value) is dict:   #  or key == key_name
            rely_value = get_rely_data(value, key_name)
        elif type(value) is list:   #  or key == key_name
            for i in value:
                rely_value = get_rely_data(i, key_name)
    return rely_value


def rely_api(case_list, rely_case, url, rely_data):
    """
    :param case_list: 用例文件
    :param rely_case: 有依赖的的用例
    :param url:
    :param rely_data: 依赖的关键字
    :param rely_runin:
    :return: 从依赖接口返回的数据中查找到需要的值
    """
    datas = {}
    if rely_case['依赖参数'] == 'cookie':
        for i in case_list:
            if i['CaseId'] == rely_case['依赖id']:
                data = operation_json.check_data(i)
                re_data, cookie = runmethod.run_url(i['请求类型'], url + i['api'], data, i['header'], rely_case['依赖参数'])
                for key, value in cookie.items():
                    cookie = {'cookie': "%s=%s" % (key, value)}
                return re_data, cookie
    else:
        # datas = {}
        for i in case_list:
            if i['CaseId'] == rely_case['依赖id']:
                data = operation_json.check_data(i)
                re_value, cookie = runmethod.run_url(i['请求类型'], url + i['api'], data, i['header'])
                rely_value = get_rely_data(re_value.json(), rely_data)
                datas[rely_data] = rely_value
                return datas, cookie
