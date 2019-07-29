# coding=utf-8
import json


# 读取json
def get_config(conf):
    with open("../test_file/ApiTest/data_config.json", 'r', encoding='utf-8') as fp:
        data = json.load(fp)
    conf_data = data[conf]
    return conf_data


# 校验请求参数
def check_data(i):
    """
    请求参数直接写在用例表格中时，写在{}中，判断如字符首尾为{}时，
    将字符串转换为dict格式后直接返回，否则再去json文件中读取参数
    """
    data = i['请求数据']
    num = i['CaseId']
    if data:
        if data.startswith('{') and data.endswith('}'):   # 判断是否以{}开头和结尾
            sum_data = eval(data)
            return sum_data     #eval(data)                             # eval：将{}字符串转换为字典
        else:
            try:
                with open("../test_file/ApiTest/case/data_case.json", 'r', encoding='utf-8') as fp:
                    case = json.load(fp)        # dumps
                    # case = json.loads(fp)
                return case[data]
            except KeyError as e:
                print('%s:  ▇*******▇>> fail:  Error！请检查请求参数！ 你是这样写的：%s' % (num, e))
            except Exception as e:
                print(e, '%s:  ▇*******▇>> fail:  Error！请检查请求参数！参数：%s' % (num, data))
