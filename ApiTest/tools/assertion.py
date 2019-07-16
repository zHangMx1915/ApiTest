# -*-coding:utf_8-*-
# https://blog.csdn.net/qq_22795513/article/details/76187722


smn = None
def compare_json_data(A, B, xpath='.'):

    if isinstance(A, list) and isinstance(B, list):
        for i in range(len(A)):
            try:
                compare_json_data(A[i], B[i], xpath + '[%s]' % str(i))
            except:
                # print('▇▇▇▇▇ A中的%s[%s]未在B中找到' % (xpath, i))
                smn = '▇▇▇▇▇ A中的%s[%s]未在B中找到' % (xpath, i)
                return smn
    if isinstance(A, dict) and isinstance(B, dict):
        for i in A:
            try:
                B[i]
            except:
                # print('▇▇▇▇▇ A中的%s/%s 未在B中找到' % (xpath, i))
                smn = '▇▇▇▇▇ A中的%s/%s 未在B中找到' % (xpath, i)
                return smn
                # continue
            if not (isinstance(A.get(i), (list, dict)) or isinstance(B.get(i), (list, dict))):
                if type(A.get(i)) != type(B.get(i)):
                    # print('▇▇▇▇▇ 类型不同参数在[A]中的绝对路径:  %s/%s  ►►► A is %s, B is %s '% (xpath, i, type(A.get(i)), type(B.get(i))))
                    smn = '▇▇▇▇▇ 类型不同参数在[A]中的绝对路径:  %s/%s  ►►► A is %s, B is %s '% (xpath, i, type(A.get(i)), type(B.get(i)))
                    return smn
                elif A.get(i) != B.get(i):
                    # print('▇▇▇▇▇ 仅内容不同参数在[A]中的绝对路径:  %s/%s  ►►► A is %s, B is %s ' % (xpath, i, A.get(i), B.get(i)))
                    smn = '▇▇▇▇▇ 仅内容不同参数在[A]中的绝对路径:  %s/%s  ►►► A is %s, B is %s ' % (xpath, i, A.get(i), B.get(i))
                    return smn
                # continue
            compare_json_data(A.get(i), B.get(i), xpath + '/' + str(i))
        return
    if type(A) != type(B):
        # print('▇▇▇▇▇ 类型不同参数在[A]中的绝对路径:  %s  ►►► A is %s, B is %s ' % (xpath, type(A), type(B)))
        smn = '▇▇▇▇▇ 类型不同参数在[A]中的绝对路径:  %s  ►►► A is %s, B is %s ' % (xpath, type(A), type(B))
        return smn
    elif A != B and type(A) is not list:
        # print('▇▇▇▇▇ 仅内容不同参数在[A]中的绝对路径:  %s  ►►► A is %s, B is %s ' % (xpath, A, B))
        smn = '▇▇▇▇▇ 仅内容不同参数在[A]中的绝对路径:  %s  ►►► A is %s, B is %s ' % (xpath, A, B)
        return smn
    return True
# # 俩个字典，传进去，包含了多种情况。
# A = {'b':[1,2,5,8],'c':3,'d':2,'f':[1,2,3],'g':[1,2,3,[2,'2',2]],'h':'5','i':None,'j':False,'k':{'l':{'m':[{'n':12}]}}}
# B = {'b':[1,2,'3'],'c':2,'e':'4','f':[1,2,3,5],'g':[1,2,3,[1,2]],'h':[1,2],'i':None,'j':True,'k':{'l':{'m':[{'n':2}]}}}
#
# compare_json_data(A,B)