# coding=utf-8
import time


class TemplateMixin:
    """html报告"""

    HTML_TMPL = """
                    <!DOCTYPE html>
                    <html lang="en">
                    <head>
                        <meta charset="UTF-8">
                        <title>自动化测试报告</title>
                        <link href="http://libs.baidu.com/bootstrap/3.0.3/css/bootstrap.min.css" rel="stylesheet">
                        <h1 style="font-family: Microsoft YaHei">%(xmmc)s</h1>
                        <p <h2 class='attribute'><strong>测试人员 : </strong> 测试人 </h2></p>
                        <p <h3 class='attribute'><strong>耗时 : </strong>%(hs)ss</h3></p>
                        <p <h3 class='attribute'><strong>报告生成时间 : </strong>%(cssj)s</h3></p>
                        <p class='attribute'><strong>测试结果 : </strong> %(value)s</p>
                        <style type="text/css" media="screen">
                    body  { font-family: Microsoft YaHei,Tahoma,arial,helvetica,sans-serif;padding: 20px;}
                    </style>
                    </head>
                    <body>
                        <table id='result_table' class="table table-condensed table-bordered table-hover"  >
                            <colgroup>
                                <col align='left' />
                                <col align='right' />
                                <col align='right' />
                                <col align='right' />
                                <col align='right' />
                                <col align='right' />
                                <col align='right' />
                                <col align='right' />
                                <col align='right' />
                            </colgroup>
                            <tr id='header_row' class="text-center success" style="font-weight: bold;font-size: 14px;">
                                <th>CaseID</th>
                                <th>用例名称</th>
                                <th>api</th>
                                <th>请求类型</th>
                                <th>请求参数</th>
                                <th>依赖接口</th>
                                <th>状态码</th>
                                <th>执行结果</th>
                                <th>结果</th>
                            %(table_tr)s
                        </table>
                    </body>
                    </html>
                """
    TABLE_TMPL = """
                    <tr class='failClass warning'>
                        <td >%(id)s</td>
                        <td >%(case_name)s</td>
                        <td >%(case_api)s</td>
                        <td >%(request_method)s</td>
                        <td >%(request_data)s</td>
                        <td >%(rely_api)s</td>
                        <td >%(status_code)s</td>
                        <td >%(return_result)s</td>
                        <td >%(final)s</td>
                    </tr>
                """


def generate_html(report_name, time_consuming, data):
    table_tr0, table, jg, b = '', [], [], []
    numfail = len(data)
    for i in range(len(data)):
        if data[i][8] == 'fail':
            jg.append(data[i][8])
    numsucc = len(jg)
    html = TemplateMixin()
    for i in range(len(data)):
        table.append(i)
    for i in range(len(data)):
        table_td = html.TABLE_TMPL % dict(
                                            id=data[i][0],
                                            case_name=data[i][1],
                                            case_api=data[i][2],
                                            request_method=data[i][3],
                                            request_data=data[i][4],
                                            rely_api=data[i][5],
                                            status_code=data[i][6],
                                            return_result=data[i][7],
                                            final=data[i][8]
                                        )
        b.append(table_td)
    for i in b:
        table_tr0 += i
    total_str = '共 %s，通过 %s，失败 %s，通过率 %.2f%s' % \
                (numfail, numfail - numsucc, numsucc, (numfail - numsucc) / numfail * 100, '%')
    output = html.HTML_TMPL % dict(xmmc=report_name,
                                   hs=time_consuming,
                                   cssj=time.strftime("%b-%d-%Y %H:%M:%S", time.localtime()),
                                   value=total_str,
                                   table_tr=table_tr0,
                                   )
    # 生成html报告
    with open("../test_file/ApiTest/log/%s.html" % report_name, 'wb') as f:
        f.write(output.encode('utf-8'))
