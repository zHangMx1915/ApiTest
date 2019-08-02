# -*-coding:utf_8-*-
import re


def re_requests(a_str, b_str):
    if len(re.findall(str(a_str), str(b_str))) is not 0:
        return True


def compare_json_data(a_str, b_str, xpath='.'):
    """
        https://blog.csdn.net/qq_22795513/article/details/76187722
    """
    if isinstance(a_str, list) and isinstance(b_str, list):
        for i in range(len(a_str)):
            try:
                compare_json_data(a_str[i], b_str[i], xpath + '[%s]' % str(i))
            except Exception as e:
                smn = '▇▇▇▇▇ A中的%s[%s]未在B中找到' % (xpath, i)
                return smn
    if isinstance(a_str, dict) and isinstance(b_str, dict):
        for i in a_str:
            try:
                b_str[i]
            except Exception:
                smn = '▇▇▇▇▇ A中的%s/%s 未在B中找到' % (xpath, i)
                return smn
                # continue
            if not (isinstance(a_str.get(i), (list, dict)) or isinstance(b_str.get(i), (list, dict))):
                if type(a_str.get(i)) != type(b_str.get(i)):
                    smn = '▇▇▇▇▇ 类型不同参数在[A]中的绝对路径:  %s/%s  ►►► A is %s, B is %s ' % (xpath, i, type(a_str.get(i)), type(b_str.get(i)))
                    return smn
                elif a_str.get(i) != b_str.get(i):
                    smn = '▇▇▇▇▇ 仅内容不同参数在[A]中的绝对路径:  %s/%s  ►►► A is %s, B is %s ' % (xpath, i, a_str.get(i), b_str.get(i))
                    return smn
                # continue
            compare_json_data(a_str.get(i), b_str.get(i), xpath + '/' + str(i))
        return
    if type(a_str) != type(b_str):
        smn = '▇▇▇▇▇ 类型不同参数在[A]中的绝对路径:  %s  ►►► A is %s, B is %s ' % (xpath, type(a_str), type(b_str))
        return smn
    elif a_str != b_str and type(a_str) is not list:
        smn = '▇▇▇▇▇ 仅内容不同参数在[A]中的绝对路径:  %s  ►►► A is %s, B is %s ' % (xpath, a_str, b_str)
        return smn
    return True


# # 俩个字典，传进去，包含了多种情况。
# A = {'b':[1,2,5,8],'c':3,'d':2,'f':[1,2,3],'g':[1,2,3,[2,'2',2]],'h':'5','i':None,'j':False,'k':{'l':{'m':[{'n':12}]}}}
# B = {'b':[1,2,'3'],'c':2,'e':'4','f':[1,2,3,5],'g':[1,2,3,[1,2]],'h':[1,2],'i':None,'j':True,'k':{'l':{'m':[{'n':2}]}}}
#
# compare_json_data(A,B)
