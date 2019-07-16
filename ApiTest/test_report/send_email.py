import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
"""发送邮件"""


# 发送邮件（纯文本格式）
def send_email(sub, content, user_mail):
    """
    :param user_mail: 收件人邮箱
    :param sub:     主题
    :param content:     内容
    :return:
    """
    send_users = user_mail['']
    passwords = user_mail['']
    user_list = user_mail['']
    email_host = 'smtp.' + send_users.split('@')[-1]     # 根据邮箱账号获取不同厂家SMTP服务器地址
    user = 'zhangXin' + '<' + send_users + '>'
    message = MIMEText(content, _subtype='plain', _charset='utf-8')
    message['Subject'] = sub
    message['From'] = user
    message['To'] = ';'.join(user_list)
    server = smtplib.SMTP()
    server.connect(host=email_host)
    server.login(send_users, passwords)
    server.sendmail(user, user_list, message.as_string())
    server.close()


# 发送带有附件的邮件
def file_mail(content, file_name, user_mail):       # file_name: 邮件附件路径 + 文件名
    send_users = user_mail['send_user']
    passwords = user_mail['password']
    user_list = user_mail['Receipt']
    file_path = '../test_file/ApiTest/log/' + file_name + '.html'
    # 创建一个带附件的实例
    user = 'zhang' + '<' + send_users + '>'
    message = MIMEMultipart()
    message.attach(MIMEText(content, _subtype='plain', _charset='utf-8'))  # 邮件正文内容
    message['Subject'] = '测试报告'
    message['From'] = user
    message['To'] = ';'.join(user_list)
    # 构造附件
    att1 = MIMEText(open(file_path, 'rb').read(), 'base64', 'utf-8')
    att1["Content-Type"] = 'application/octet-stream'
    att1.add_header('Content-Disposition', 'attachment', filename=file_name + '.html')
    message.attach(att1)
    try:
        # 使用非本地服务器，需要建立ssl连接
        email_host = 'smtp.' + send_users.split('@')[-1]
        smtpObj = smtplib.SMTP_SSL(email_host, 465)
        smtpObj.login(send_users, passwords)
        smtpObj.sendmail(send_users, user_list, message.as_string())
        print("邮件发送成功")
    except smtplib.SMTPException as se:
        print(f"Error: 无法发送邮件.Case:{se}")
