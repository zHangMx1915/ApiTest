# coding=utf-8
import time


file_name = ''


# 创建log文件
def logfile():
    global file_name
    path = '../test_file/appiumFile/log'
    test_time = (time.strftime("%Y-%m-%d %H-%M-%S", time.localtime()))
    file_name = (path + '/' + test_time + ".txt")
    open(file_name, 'a', encoding='utf-8')                                   # 创建log的txt文件


# 写入日志
def mylog(log, va=None):
    global file_name
    test_time = (time.strftime("%Y-%m-%d %H-%M-%S", time.localtime()))       # 系统当前时间
    with open(file_name, "a", encoding='utf-8') as f:
        if not va:
            f.write("\n%s :   %s" % (test_time, log))                       # 写入txt
        else:
            f.write("\n%s :   %s" % (test_time, log + ',  ' + va))          # appium执行的语句


# 读取当前log文件中全部内容
def log_all():
    global file_name
    with open(file_name, 'r', encoding='utf-8') as f:
        log_text = f.read()
    return log_text
