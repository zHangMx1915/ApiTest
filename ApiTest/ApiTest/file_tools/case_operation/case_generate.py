# -*-coding:utf_8-*-
import collections
import random, string


class ProducCase:

    def suijishu(self):
        src_digits = string.digits  # string_数字
        src_uppercase = string.ascii_uppercase  # string_大写字母
        src_lowercase = string.ascii_lowercase  # string_小写字母
        count = 10  # 输入生成密码个数
        for i in range(count):
            # 随机生成数字、大写字母、小写字母的组成个数（可根据实际需要进行更改）
            digits_num = random.randint(1, 2)
            uppercase_num = random.randint(1, 4 - digits_num - 1)
            lowercase_num = 4 - (digits_num + uppercase_num)
            # 生成字符串
            password = random.sample(src_digits, digits_num) + \
                       random.sample(src_uppercase, uppercase_num) + \
                       random.sample(src_lowercase, lowercase_num)
            random.shuffle(password)  # 打乱字符串
            new_password = ''.join(password)  # 列表转字符串
            print(new_password.lower())

    def data_lack(self, case, data):
        data = collections.OrderedDict(data)
        sum = len(data)
        data_list = []
        case_id = case['CaseId']
        for n in range(sum):
            case_list, ms, i, name = [], {}, 0, None
            test = case.copy()
            for key, value in data.items():
                mk = '{"%s": "%s"}' % (key, value)
                if i != n:
                    ms.update(eval(mk))
                else:
                    name = case['名称'] + '--缺少参数：{"%s": "%s"}' % (key, value)
                i += 1
            new_id = case_id + '.%s' % n
            test['名称'] = name
            test['CaseId'] = new_id
            case_list.append(test)
            case_list.append(ms)
            data_list.append(case_list)
        return data_list

    def data_type(self):
        pass

    def value_size(self, case, data):
        data = collections.OrderedDict(data)
        sum = len(data)
        data_list = []
        case_id = case['CaseId']
        for n in range(sum):
            case_list, ms, i, name = [], {}, 0, None
            test = case.copy()
            for key, value in data.items():
                if i == n:
                    value = ''
                    name = case['名称'] + '--参数值变化：{"%s": "%s"}' % (key, value)
                mk = '{"%s": "%s"}' % (key, value)
                ms.update(eval(mk))
                i += 1
            new_id = case_id + '.%s' % (n + sum)
            test['名称'] = name
            test['CaseId'] = new_id
            case_list.append(test)
            case_list.append(ms)
            data_list.append(case_list)
        return data_list

    def case_cookie(self):
        pass


class ProduRun(ProducCase):

    def new_case(self, case, data):
        lack = self.data_lack(case, data)
        lack_size = self.value_size(case, data)
        lack.extend(lack_size)
        return lack
