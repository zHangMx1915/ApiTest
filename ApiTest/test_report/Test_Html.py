#coding=utf-8


"""
A TestRunner for use with the Python unit testing framework. It
generates a HTML report to show the result at a glance.

The simplest way to use this is to invoke its main method. E.g.

    import unittest
    import HTMLTestRunner

    ... define your tests ...

    if __name__ == '__main__':
        HTMLTestRunner.main()


For more customization options, instantiates a HTMLTestRunner object.
HTMLTestRunner is a counterpart to unittest's TextTestRunner. E.g.

    # output to a file
    fp = file('my_report.html', 'wb')
    runner = HTMLTestRunner.HTMLTestRunner(
                stream=fp,
                title='My unit test',
                description='This demonstrates the report output by HTMLTestRunner.'
                )

    # Use an external stylesheet.
    # See the Template_mixin class for more customizable options
    runner.STYLESHEET_TMPL = '<link rel="stylesheet" href="my_stylesheet.css" type="text/css">'

    # run the test
    runner.run(my_test_suite)


------------------------------------------------------------------------
Copyright (c) 2004-2007, Wai Yip Tung
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

* Redistributions of source code must retain the above copyright notice,
  this list of conditions and the following disclaimer.
* Redistributions in binary form must reproduce the above copyright
  notice, this list of conditions and the following disclaimer in the
  documentation and/or other materials provided with the distribution.
* Neither the name Wai Yip Tung nor the names of its contributors may be
  used to endorse or promote products derived from this software without
  specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER
OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

# URL: http://tungwaiyip.info/software/HTMLTestRunner.html


__author__ = "Wai Yip Tung,  Findyou"
__version__ = "0.8.2.2"


"""
Change History
Version 0.8.2.1 -Findyou
* 改为支持python3

Version 0.8.2.1 -Findyou
* 支持中文，汉化
* 调整样式，美化（需要连入网络，使用的百度的Bootstrap.js）
* 增加 通过分类显示、测试人员、通过率的展示
* 优化“详细”与“收起”状态的变换
* 增加返回顶部的锚点

Version 0.8.2
* Show output inline instead of popup window (Viorel Lupu).

Version in 0.8.1
* Validated XHTML (Wolfgang Borgert).
* Added description of test classes and test cases.

Version in 0.8.0
* Define Template_mixin class for customization.
* Workaround a IE 6 bug that it does not treat <script> block as CDATA.

Version in 0.7.1
* Back port to Python 2.3 (Frank Horowitz).
* Fix missing scroll bars in detail log (Podi).
"""

# TODO: color stderr
# TODO: simplify javascript using ,ore than 1 class in the class attribute?

import datetime
import io
import sys
import time
import unittest
from xml.sax import saxutils
import sys
import re


# ------------------------------------------------------------------------
# The redirectors below are used to capture output during testing. Output
# sent to sys.stdout and sys.stderr are automatically captured. However
# in some cases sys.stdout is already cached before HTMLTestRunner is
# invoked (e.g. calling logging.basicConfig). In order to capture those
# output, use the redirectors for the cached stream.
#
# e.g.
#   >>> logging.basicConfig(stream=HTMLTestRunner.stdout_redirector)
#   >>>


class OutputRedirector(object):
    """ Wrapper to redirect stdout or stderr """

    def __init__(self, fp):
        self.fp = fp

    def write(self, s):
        self.fp.write(s)

    def writelines(self, lines):
        self.fp.writelines(lines)

    def flush(self):
        self.fp.flush()

stdout_redirector = OutputRedirector(sys.stdout)
stderr_redirector = OutputRedirector(sys.stderr)

# ----------------------------------------------------------------------
# Template


class Template_mixin(object):
    """
    Define a HTML template for report customerization and generation.

    Overall structure of an HTML report

    HTML
    +------------------------+
    |<html>                  |
    |  <head>                |
    |                        |
    |   STYLESHEET           |
    |   +----------------+   |
    |   |                |   |
    |   +----------------+   |
    |                        |
    |  </head>               |
    |                        |
    |  <body>                |
    |                        |
    |   HEADING              |
    |   +----------------+   |
    |   |                |   |
    |   +----------------+   |
    |                        |
    |   REPORT               |
    |   +----------------+   |
    |   |                |   |
    |   +----------------+   |
    |                        |
    |   ENDING               |
    |   +----------------+   |
    |   |                |   |
    |   +----------------+   |
    |                        |
    |  </body>               |
    |</html>                 |
    +------------------------+
    """

    STATUS = {
                0: '通过',
                1: '失败',
                2: '错误',
                }

    DEFAULT_TITLE = '单元测试报告'
    DEFAULT_DESCRIPTION = ''
    DEFAULT_TESTER='测试人'

    # ------------------------------------------------------------------------
    # HTML Template

    HTML_TMPL = r"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <title>%(title)s</title>
    <meta name="generator" content="%(generator)s"/>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
    <link href="http://libs.baidu.com/bootstrap/3.0.3/css/bootstrap.min.css" rel="stylesheet">
    <script src="http://libs.baidu.com/jquery/2.0.0/jquery.min.js"></script>
    <script src="http://libs.baidu.com/bootstrap/3.0.3/js/bootstrap.min.js"></script>
    <script src="http://echarts.baidu.com/gallery/vendors/echarts/echarts-all-3.js?_v_=1497515835475"></script>
    %(stylesheet)s
</head>
<body >
<script language="javascript" type="text/javascript">
output_list = Array();

/*
 *  查找页面内容（同Ctrl + F）
 *  **************************** START ****************************
*/
function encode(s) {
            return s.replace(/&/g, "&").replace(/</g, "<").replace(/>/g, ">").replace(/([\\\.\*\[\]\(\)\$\^])/g, "\\$1");
        }

        function decode(s) {
            return s.replace(/\\([\\\.\*\[\]\(\)\$\^])/g, "$1").replace(/>/g, ">").replace(/</g, "<").replace(/&/g, "&");
        }
        //外部调用函数
        function highlight() {
            var s = document.getElementById('keyword').value.trim();
            if (s.length == 0) {
                //复位
               $('.errorCase').parent().attr('class','');
               $('.passCase').parent().attr('class','');
               $('.failCase').parent().attr('class','');
                return false;
            }
            s = encode(s);
            /*var obj = document.getElementsByTagName("body")[0];
            var objArr = document.getElementsByClassName('testcase');
            for(p in objArr){
                objArr[p].parentElement.parentElement.setAttribute('class','');
            }
            for(p in objArr){
                if(!objArr[p].innerHTML.match(s)){
                    document.getElementsByClassName('testcase')[0].parentElement.parentElement.setAttribute('class','hiddenRow');
                } else{
                   t = objArr[p].innerHTML.replace(/<span\s+class=.?highlight.?>([^<>]*)<\/span>/gi, "$1")
                   objArr[p].innerHTML = t;
                   t = objArr[p].innerHTML;
                   var r = /{searchHL}(({(?!\/searchHL})|[^{])*){\/searchHL}/g;
                   t = t.replace(r, "<span class='highlight'>$1</span>");
                   obj.innerHTML = t;
                }
            }*/
            var errorArr = $('.errorCase');
            errorArr.parent().attr('class','');
            errorArr.each(function(){
            var self = $(this);
            if(!self.text().match(s)){
            self.parent().addClass('hiddenRow');
            }else{
            t = self.text().replace(/<span\s+class=.?highlight.?>([^<>]*)<\/span>/gi, "$1")
                   self.children().html(t);
                   t = self.text();
                   var r = /{searchHL}(({(?!\/searchHL})|[^{])*){\/searchHL}/g;
                   t = t.replace(r, "<span class='highlight'>$1</span>");
                    self.children().html(t);
            }
            })

            var failArr = $('.failCase');
            failArr.parent().attr('class','');
            failArr.each(function(){
            var self = $(this);
            if(!self.text().match(s)){
            self.parent().addClass('hiddenRow');
            }else{
            t = self.text().replace(/<span\s+class=.?highlight.?>([^<>]*)<\/span>/gi, "$1")
                   self.children().html(t);
                   t = self.text();
                   var r = /{searchHL}(({(?!\/searchHL})|[^{])*){\/searchHL}/g;
                   t = t.replace(r, "<span class='highlight'>$1</span>");
                    self.children().html(t);
            }
            })

            var passArr = $('.passCase');
            passArr.parent().attr('class','');
            passArr.each(function(){
            var self = $(this);
            if(!self.text().match(s)){
            self.parent().addClass('hiddenRow');
            }else{
            t = self.text().replace(/<span\s+class=.?highlight.?>([^<>]*)<\/span>/gi, "$1")
                   self.children().html(t);
                   t = self.text();
                   var r = /{searchHL}(({(?!\/searchHL})|[^{])*){\/searchHL}/g;
                   t = t.replace(r, "<span class='highlight'>$1</span>");
                    self.children().html(t);
            }
            })

            //var t = obj.innerHTML.replace(/<span\s+class=.?highlight.?>([^<>]*)<\/span>/gi, "$1");
            //obj.innerHTML = t;
            //var cnt = loopSearch(s, obj);
            //t = obj.innerHTML
            //var r = /{searchHL}(({(?!\/searchHL})|[^{])*){\/searchHL}/g
            //t = t.replace(r, "<span class='highlight'>$1</span>");
            //obj.innerHTML = t;
            //document.getElementById('resultNum').innerHTML = "搜索到关键词共" + cnt + "处";
        }

        function highlight13(e){
            if(e.keyCode == 13){
                highlight();
            }
        }

        function loopSearch(s, obj) {
            var cnt = 0;
            if (obj.nodeType == 3) {
                cnt = replace(s, obj);
                return cnt;
            }
            for (var i = 0, c; c = obj.childNodes[i]; i++) {
                if (!c.className || c.className != "highlight")
                    cnt += loopSearch(s, c);
            }
            return cnt;
        }

        function replace(s, dest) {
            var r = new RegExp(s, "g");
            var tm = null;
            var t = dest.nodeValue;
            var cnt = 0;
            if (tm = t.match(r)) {
                cnt = tm.length;
                t = t.replace(r, "{searchHL}" + decode(s) + "{/searchHL}")
                dest.nodeValue = t;
            }
            return cnt;
        }
        
/*
 *  查找页面内容（同Ctrl + F）
 *  **************************** END ****************************
*/

/*level 调整增加只显示通过用例的分类 --Findyou
0:Summary //all hiddenRow
1:Failed  //pt hiddenRow, ft none
2:Pass    //pt none, ft hiddenRow
3:All     //pt none, ft none
*/
function showCase(level) {
    trs = document.getElementsByTagName("tr");
    for (var i = 0; i < trs.length; i++) {
        tr = trs[i];
        id = tr.id;
        if (id.substr(0,2) == 'ft') {
            if (level == 2 || level == 0 ) {
                tr.className = 'hiddenRow';
            }
            else {
                tr.className = '';
            }
        }
        if (id.substr(0,2) == 'pt') {
            if (level < 2) {
                tr.className = 'hiddenRow';
            }
            else {
                tr.className = '';
            }
        }
    }

    //加入【详细】切换文字变化 --Findyou
    detail_class=document.getElementsByClassName('detail');
	//console.log(detail_class.length)
	if (level == 3) {
		for (var i = 0; i < detail_class.length; i++){
			detail_class[i].innerHTML="收起"
		}
	}
	else{
			for (var i = 0; i < detail_class.length; i++){
			detail_class[i].innerHTML="详细"
		}
	}
}

function showClassDetail(cid, count) {
    var id_list = Array(count);
    var toHide = 1;
    for (var i = 0; i < count; i++) {
        //ID修改 点 为 下划线 -Findyou
        tid0 = 't' + cid.substr(1) + '_' + (i+1);
        tid = 'f' + tid0;
        tr = document.getElementById(tid);
        if (!tr) {
            tid = 'p' + tid0;
            tr = document.getElementById(tid);
        }
        id_list[i] = tid;
        if (tr.className) {
            toHide = 0;
        }
    }
    for (var i = 0; i < count; i++) {
        tid = id_list[i];
        //修改点击无法收起的BUG，加入【详细】切换文字变化 --Findyou
        if (toHide) {
            document.getElementById(tid).className = 'hiddenRow';
            document.getElementById(cid).innerText = "详细"
        }
        else {
            document.getElementById(tid).className = '';
            document.getElementById(cid).innerText = "收起"
        }
    }
}

function html_escape(s) {
    s = s.replace(/&/g,'&amp;');
    s = s.replace(/</g,'&lt;');
    s = s.replace(/>/g,'&gt;');
    return s;
}
</script>
%(heading)s
%(report)s
%(ending)s

</body>
</html>
"""
    # variables: (title, generator, stylesheet, heading, report, ending)
    # ------------------------------------------------------------------------
    # Stylesheet
    #
    # alternatively use a <link> for external style sheet, e.g.
    #   <link rel="stylesheet" href="$url" type="text/css">

    STYLESHEET_TMPL = """
<style type="text/css" media="screen">
body        { font-family: Microsoft YaHei,Tahoma,arial,helvetica,sans-serif;padding: 20px; font-size: 80%; }
table       { font-size: 100%; }

/* -- heading ---------------------------------------------------------------------- */
.heading {
    margin-top: 0ex;
    margin-bottom: 1ex;
}

.heading .description {
    margin-top: 4ex;
    margin-bottom: 6ex;
}

/* -- report ------------------------------------------------------------------------ */
#total_row  { font-weight: bold; }
.passCase   { color: #00CD66; }
.failCase   { color: #d9534f; font-weight: bold; }
.errorCase  { color: #f0ad4e; font-weight: bold; }
.hiddenRow  { display: none; }
.testcase   { margin-left: 2em; }
</style>
"""

    # ------------------------------------------------------------------------
    # Heading
    #

    HEADING_TMPL = """<div class='heading'>
<div   id="main" style="width: 300px;height:300px; float:right;margin-right:300px;margin-top:-80px"></div>
<h1 style="font-family: Microsoft YaHei">%(title)s</h1>
%(parameters)s
<p class='description'>%(description)s</p>
</div>

""" # variables: (title, parameters, description)

    HEADING_ATTRIBUTE_TMPL = """<p class='attribute'><strong>%(name)s : </strong> %(value)s</p>
""" # variables: (name, value)



    # ------------------------------------------------------------------------
    # Report
    #
    # 汉化,加美化效果 --Findyou
    REPORT_TMPL = """
<p id='show_detail_line'>
<a class="btn btn-primary" href='javascript:showCase(0)'>概要{ %(passrate)s }</a>
<a class="btn btn-danger" href='javascript:showCase(1)'>失败{ %(fail)s }</a>
<a class="btn btn-success" href='javascript:showCase(2)'>通过{ %(Pass)s }</a>
<a class="btn btn-info" href='javascript:showCase(3)'>所有{ %(count)s }</a>
<a class="btn btn-info" style="float:right;" onclick="highlight()">查询</a>
<input id='fail' type="hidden" value="%(fail)s"/>
<input id='error' type="hidden" value="%(error)s"/>
<input id='Pass' type="hidden" value="%(Pass)s"/>
<input type="search" id="keyword" onkeyup="highlight13(event)" class="form-control" style="float:right;width:200px;margin-right:10px;">
<span id="resultNum" style="float:right;font-size: 16px;"></span>
</p>
<table id='result_table' class="table table-condensed table-bordered table-hover">
<colgroup>
<col align='left' />
<col align='right' />
<col align='right' />
<col align='right' />
<col align='right' />
<col align='right' />
</colgroup>
<tr id='header_row' class="text-center success" style="font-weight: bold;font-size: 14px;">
    <td>用例集/测试用例</td>
    <td>总计</td>
    <td>通过</td>
    <td>失败</td>
    <td>错误</td>
    <td>详细</td>
</tr>
%(test_list)s
<tr id='total_row' class="text-center active">
    <td>总计</td>
    <td>%(count)s</td>
    <td>%(Pass)s</td>
    <td>%(fail)s</td>
    <td>%(error)s</td>
    <td>通过率：%(passrate)s</td>
</tr>
</table>
""" # variables: (test_list, count, Pass, fail, error ,passrate)

    REPORT_CLASS_TMPL = r"""
<tr class='%(style)s warning'>
    <td>%(desc)s</td>
    <td class="text-center">%(count)s</td>
    <td class="text-center">%(Pass)s</td>
    <td class="text-center">%(fail)s</td>
    <td class="text-center">%(error)s</td>
    <td class="text-center"><a href="javascript:showClassDetail('%(cid)s',%(count)s)" class="detail" id='%(cid)s'>详细</a></td>
</tr>
""" # variables: (style, desc, count, Pass, fail, error, cid)

    #失败 的样式，去掉原来JS效果，美化展示效果  -Findyou
    REPORT_TEST_WITH_OUTPUT_TMPL = r"""
<tr id='%(tid)s' class='%(Class)s'>
    <td class='%(style)s'><div class='testcase'>%(desc)s</div></td>
    <td colspan='5' align='center'>
    <!--默认收起错误信息 -Findyou
    <button id='btn_%(tid)s' type="button"  class="btn btn-danger btn-xs collapsed" data-toggle="collapse" data-target='#div_%(tid)s'>%(status)s</button>
    <div id='div_%(tid)s' class="collapse"  align='left'>  -->

    <!-- 默认展开错误信息 -Findyou -->
    <button id='btn_%(tid)s' type="button"  class="btn btn-danger btn-xs" data-toggle="collapse" data-target='#div_%(tid)s'>%(status)s</button>
    <div id='div_%(tid)s' class="collapse in"  align='left'>
    <pre>
    %(script)s
    </pre>
    </div>
    </td>
</tr>
""" # variables: (tid, Class, style, desc, status)

    # 通过 的样式，加标签效果  -Findyou
    REPORT_TEST_NO_OUTPUT_TMPL = r"""
<tr id='%(tid)s' class='%(Class)s'>
    <td class='%(style)s'><div class='testcase'>%(desc)s</div></td>
    <td colspan='5' align='center'><span class="label label-success success">%(status)s</span></td>
</tr>
""" # variables: (tid, Class, style, desc, status)

    REPORT_TEST_OUTPUT_TMPL = r"""
%(id)s: %(output)s
""" # variables: (id, output)

    # ------------------------------------------------------------------------
    # ENDING
    #
    # 增加返回顶部按钮  --Findyou
    ENDING_TMPL = """<div id='ending'>&nbsp;</div>
    <div style=" position:fixed;right:50px; bottom:30px; width:20px; height:20px;cursor:pointer">
    <a href="#"><span class="glyphicon glyphicon-eject" style = "font-size:30px;" aria-hidden="true">
    </span></a></div>
    <script type="text/javascript">
        // 基于准备好的dom，初始化echarts实例
        var myChart = echarts.init(document.getElementById('main'));
        var fail= document.getElementById('fail').value;
        var error=document.getElementById('error').value;
        var Pass=document.getElementById('Pass').value;

        // 指定图表的配置项和数据
        option = {
            color:[ 'rgb(237,156,40)', 'rgb(217,83,79)','rgb(92,184,92)'],
            tooltip : {
                trigger: 'item',
                formatter: "{a} <br/>{b} : {c} ({d}%)"
            },
            legend: {
                orient: 'vertical',
                left: 'left'
             
            },
            series : [
                {
                    name: '访问来源',
                    type: 'pie',
                    radius : '50%',
                    center: ['50%', '50%'],
                    data:[
                        {value:fail, name:'失败'},
                        {value:error, name:'错误'},
                        {value:Pass, name:'通过'}
                    ],
                    itemStyle: {
                        emphasis: {
                            shadowBlur: 10,
                            shadowOffsetX: 0,
                            shadowColor: 'rgba(0, 0, 0, 0.5)'
                        }
                    }
                }
            ]
        };

        // 使用刚指定的配置项和数据显示图表。
        myChart.setOption(option);
    </script>
    """

# -------------------- The end of the Template class -------------------


TestResult = unittest.TestResult


class _TestResult(TestResult):
    # note: _TestResult is a pure representation of results.
    # It lacks the output and reporting ability compares to unittest._TextTestResult.

    def __init__(self, verbosity=1):
        TestResult.__init__(self)
        self.stdout0 = None
        self.stderr0 = None
        self.success_count = 0
        self.failure_count = 0
        self.error_count = 0
        self.verbosity = verbosity

        # result is a list of result in 4 tuple
        # (
        #   result code (0: success; 1: fail; 2: error),
        #   TestCase object,
        #   Test output (byte string),
        #   stack trace,
        # )
        self.result = []
        #增加一个测试通过率 --Findyou
        self.passrate=float(0)

    def startTest(self, test):
        TestResult.startTest(self, test)
        # just one buffer for both stdout and stderr
        self.outputBuffer = io.StringIO()
        stdout_redirector.fp = self.outputBuffer
        stderr_redirector.fp = self.outputBuffer
        self.stdout0 = sys.stdout
        self.stderr0 = sys.stderr
        sys.stdout = stdout_redirector
        sys.stderr = stderr_redirector

    def complete_output(self):
        """
        Disconnect output redirection and return buffer.
        Safe to call multiple times.
        """
        if self.stdout0:
            sys.stdout = self.stdout0
            sys.stderr = self.stderr0
            self.stdout0 = None
            self.stderr0 = None
        return self.outputBuffer.getvalue()

    def stopTest(self, test):
        # Usually one of addSuccess, addError or addFailure would have been called.
        # But there are some path in unittest that would bypass this.
        # We must disconnect stdout in stopTest(), which is guaranteed to be called.
        self.complete_output()

    def addSuccess(self, test):
        self.success_count += 1
        TestResult.addSuccess(self, test)
        output = self.complete_output()
        self.result.append((0, test, output, ''))
        if self.verbosity > 1:
            sys.stderr.write('ok ')
            sys.stderr.write(str(test))
            sys.stderr.write('\n')
        else:
            sys.stderr.write('.')

    def addError(self, test, err):
        self.error_count += 1
        TestResult.addError(self, test, err)
        _, _exc_str = self.errors[-1]
        output = self.complete_output()
        self.result.append((2, test, output, _exc_str))
        if self.verbosity > 1:
            sys.stderr.write('E  ')
            sys.stderr.write(str(test))
            sys.stderr.write('\n')
        else:
            sys.stderr.write('E')

    def addFailure(self, test, err):
        self.failure_count += 1
        TestResult.addFailure(self, test, err)
        _, _exc_str = self.failures[-1]
        output = self.complete_output()
        self.result.append((1, test, output, _exc_str))
        if self.verbosity > 1:
            sys.stderr.write('F  ')
            sys.stderr.write(str(test))
            sys.stderr.write('\n')
        else:
            sys.stderr.write('F')


class HTMLTestRunner(Template_mixin):

    def __init__(self,start, end, stream=sys. stdout, verbosity=1, title=None, description=None, tester=None):
        self.startTime = start
        self.stopTime = end
        self.stream = stream
        self.verbosity = verbosity
        if title is None:
            self.title = self.DEFAULT_TITLE
        else:
            self.title = title
        if description is None:
            self.description = self.DEFAULT_DESCRIPTION
        else:
            self.description = description
        if tester is None:
            self.tester = self.DEFAULT_TESTER
        else:
            self.tester = tester

    def run(self, result):
        # "Run the given test case or test suite."
        self.generateReport(result)
        return result

    def sortResult(self, result_list):
        # unittest does not seems to run in any particular order.
        # Here at least we want to group them together by class.
        rmap = {}
        classes = []
        for n, t, o, e in result_list:
            cls = t.split(',')[0]
            t = t.split(',')[1]
            if cls not in rmap:
                rmap[cls] = []
                classes.append(cls)
            rmap[cls].append((n,t,o,e))      # n为用例执行状态（0：通过，1失败，2错误），e为用例名称，o为返回结果，e为错误信息
        r = [(cls, rmap[cls]) for cls in classes]
        return r

    # 替换测试结果status为通过率 --Findyou
    def getReportAttributes(self, result):
        """
        Return report attributes as a list of (name, value).
        Override this to add custom attributes.
        """
        startTime = str(self.startTime)[:19]
        duration = str(self.stopTime - self.startTime)
        status = []
        sortedResult = self.sortResult(result)
        # for cid, (cls, cls_results) in enumerate(sortedResult):
        np = nf = ne = 0
        for cid, (cls, cls_results) in enumerate(sortedResult):
            for n, t, o, e in cls_results:
                if n == 0:
                    np += 1
                elif n == 1:
                    nf += 1
                else:
                    ne += 1
            doc = cls.__doc__ and cls.__doc__.split("\n")[0] or ""
            # desc = doc and '%s: %s' % (name, doc) or name
            desc = cls

            row = self.REPORT_CLASS_TMPL % dict(
                style=ne > 0 and 'errorClass' or nf > 0 and 'failClass' or 'passClass',
                desc=desc,
                count=np + nf + ne,
                Pass=np,
                fail=nf,
                error=ne,
                cid='c%s' % (cid + 1)
        )

        status.append('共 %s' % (np + nf + ne))
        if np: status.append('通过 %s' % np)
        if nf: status.append('失败 %s' % nf)
        if ne: status.append('错误 %s' % ne)
        if status:
            status = '，'.join(status)
            self.passrate = str("%.2f%%" % (float(np) / float(np + nf + ne) * 100))
        else:
            status = 'none'
        return [
            ('测试人员', '测试人'),
            ('开始时间', startTime),
            ('合计耗时', duration),
            ('测试结果', status + "，通过率= "+self.passrate),
        ]

    def generateReport(self, result):
        report_attrs = self.getReportAttributes(result)
        generator = 'HTMLTestRunner %s' % __version__
        stylesheet = self._generate_stylesheet()
        heading = self._generate_heading(report_attrs)
        report = self._generate_report(result)
        ending = self._generate_ending()
        output = self.HTML_TMPL % dict(
            title = saxutils.escape(self.title),
            generator = generator,
            stylesheet = stylesheet,
            heading = heading,
            report = report,
            ending = ending,
        )

        self.stream.write(output.encode('utf8'))

    def _generate_stylesheet(self):
        return self.STYLESHEET_TMPL

    # 增加Tester显示 -Findyou
    def _generate_heading(self, report_attrs):
        a_lines = []
        for name, value in report_attrs:
            line = self.HEADING_ATTRIBUTE_TMPL % dict(
                    name = saxutils.escape(name),
                    value = saxutils.escape(value),
                )
            a_lines.append(line)
        heading = self.HEADING_TMPL % dict(
            title = saxutils.escape(self.title),
            parameters = ''.join(a_lines),
            description = saxutils.escape(self.description),
            tester= saxutils.escape(self.tester)
        )
        return heading

    # 生成报告  --Findyou添加注释
    def _generate_report(self, result):
        rows = []
        sortedResult = self.sortResult(result)
        np1 = nf1 = ne1 = 0
        for cid, (cls, cls_results) in enumerate(sortedResult):
            np = nf = ne = 0
            for n,t,o,e in cls_results:
                if n == 0: np += 1
                elif n == 1: nf += 1
                else: ne += 1
            doc = cls.__doc__ and cls.__doc__.split("\n")[0] or ""
            desc = cls
            np1 +=  np
            nf1 += nf
            ne1 += ne
            row = self.REPORT_CLASS_TMPL % dict(
                style = ne > 0 and 'errorClass' or nf > 0 and 'failClass' or 'passClass',
                desc = desc,
                count = np+nf+ne,
                Pass = np,
                fail = nf,
                error = ne,
                cid = 'c%s' % (cid+1)
            )
            # rows.append(row)，为用例概括，表格第二行
            rows.append(row)
            for tid, (n,t,o,e) in enumerate(cls_results):
                self._generate_report_test(rows, cid, tid, n, t, o, e)
        report = self.REPORT_TMPL % dict(
            test_list=''.join(rows),
            count=str(np1+nf1+ne1),
            Pass=str(np1),
            fail=str(nf1),
            error=str(ne1),
            passrate=self.passrate
        )
        return report

    def _generate_report_test(self, rows, cid, tid, n, t, o, e):
        has_output = bool(o or e)
        # ID修改点为下划线,支持Bootstrap折叠展开特效 - Findyou
        tid = (n == 0 and 'p' or 'f') + 't%s_%s' % (cid+1, tid+1)
        desc = t
        tmpl = has_output and self.REPORT_TEST_WITH_OUTPUT_TMPL or self.REPORT_TEST_NO_OUTPUT_TMPL
        if isinstance(o, str):
            # TODO: some problem with 'string_escape': it escape \n and mess up formating
            uo = o
        else:
            uo = o
        if isinstance(e, str):
            # TODO: some problem with 'string_escape': it escape \n and mess up formating
            ue = e
        else:
            ue = e

        script = self.REPORT_TEST_OUTPUT_TMPL % dict(
            id = tid,
            output = saxutils.escape(uo+ue)
        )

        row = tmpl % dict(
            tid = tid,
            Class = (n == 0 and 'hiddenRow' or 'none'),
            style = n == 2 and 'errorCase' or (n == 1 and 'failCase' or 'passCase'),
            desc = desc,
            script = script,
            status = self.STATUS[n]
        )
        rows.append(row)
        if not has_output:
            return

    def _generate_ending(self):
        return self.ENDING_TMPL


##############################################################################
# Facilities for running tests from the command line
##############################################################################

# Note: Reuse unittest.TestProgram to launch test. In the future we may
# build our own launcher to support more specific command line
# parameters like test title, CSS, etc.


class TestProgram(unittest.TestProgram):
    """
    A variation of the unittest.TestProgram. Please refer to the base
    class for command line parameters.
    """
    def runTests(self):
        # Pick HTMLTestRunner as the default test runner.
        # base class's testRunner parameter is not useful because it means
        # we have to instantiate HTMLTestRunner before we know self.verbosity.
        if self.testRunner is None:
            self.testRunner = HTMLTestRunner(verbosity=self.verbosity)
        unittest.TestProgram.runTests(self)


main = TestProgram

##############################################################################
# Executing this module from the command line
##############################################################################


if __name__ == "__main__":
    start = datetime.datetime.now()

    time.sleep(1)
    end = datetime.datetime.now()

    mx = time.strftime("%H-%M", time.localtime())

    report = '../../test_file/ApiTest/log/创建用户测试报告%s.html' % mx
    fq = open(report, 'wb')
   # suite1 = '<unittest.suite.TestSuite tests=[<longin.test_login.Test_longin testMethod=test_001>, <longin.test_login.Test_longin testMethod=test_0010>, <longin.test_login.Test_longin testMethod=test_002>'
    runner = HTMLTestRunner(start = start,
                            end = end,
                            stream=fq,
                            title=u'创建用户测试报告',
                            description=u'用例执行情况')
    test = [(1, 'nwe_user.test_newuser.Test_user testMethod=test_0011', "<html><meta charset='utf-8'/><style>body{background:white}</style><script>alert"
                "('『用户名』已经有『zhangsan2』这条记录了。如果您确定该记录已删除，请到后台管理-回收站还原。"
                "。\\n')\n</script>\n<html><meta charset='utf-8'/><style>body{background:white}</style><script>"
                "if(window.parent) window.parent.document.body.click();\n</script>\n\n这条记录了。"
                "如果您确定该记录已删除，请到后台管理-回收站还原\n", ''),
                (2, 'nwe_user.test_newuser.Test_user testMethod=test_0012', "<html><meta charset='utf-8'/><style>body{background:white}</style><script>alert"
                "('『用户名』不能为空。\\n『用户名』已经有『』这条记录了。如果您确定该记录已删除，请到后台管理-回收站还原。。"
                "\\n『用户名』应当为合法的用户名。\\n')\n</script>\n<html><meta charset='utf-8'/>"
                "<style>body{background:white}</style><script>if(window.parent) window.parent.document.body.click();"
                "\n</script>\n\n这条记录了。如果您确定该记录已删除，请到后台管理-回收站还原\n", ''),
                (0,'nwe_user.test_newuser.Test_user testMethod=test_0013', "<html><meta charset='utf-8'/>"
               "<style>body{background:white}</style><script>alert('『真实姓名』不能为空。"
               "\\n『用户名』已经有『zhangsan6』这条记录了。如果您确定该记录已删除，请到后台管理-回收站还原。。"
               "\\n')\n</script>\n<html><meta charset='utf-8'/><style>body{background:white}</style>"
               "<script>if(window.parent) window.parent.document.body.click();\n</script>\n\n这条记录了。"
               "如果您确定该记录已删除，请到后台管理-回收站还原\n", ''),
                (0, 'nwe_user.test_newuser.Test_user testMethod=test_0015', "<html><meta charset='utf-8'/><style>body{background:white}</style><script>alert"
                "('『密码』不能为空。\\n')\n</script>\n<html><meta charset='utf-8'/><style>body{background:white}"
                "</style><script>if(window.parent) window.parent.document.body.click();\n</script>\n\n『密码』不能为空。"
                "\n", ''),(0, 'nwe_user.test_newuser.Test_user testMethod=test_0011',
                           "<html><meta charset='utf-8'/><style>body{background:white}</style><script>alert"
                           "('『用户名』已经有『zhangsan2』这条记录了。如果您确定该记录已删除，请到后台管理-回收站还原。。"
                           "\\n')\n</script>\n<html><meta charset='utf-8'/><style>body{background:white}</style>"
                           "<script>if(window.parent) window.parent.document.body.click();\n</script>\n\n这条记录了。"
                           "如果您确定该记录已删除，请到后台管理-回收站还原\n", ''),
            (1, 'longin.test_login.Test_longin testMethod=test_001', "{'account': 'admin', 'password': 'e10adc3949ba59abbe56e057f20f883e', "
             "'referer': 'http://127.0.0.1/zentao/my/'}\nhttp://127.0.0.1/zentao/user-login.html\n<html><meta charset='utf-8'/>"
             "<style>body{background:white}</style><script>parent.location='http://127.0.0.1/zentao/my/';"
             "\n\n</script>\n\nTrue\n", ''),(2, 'longin.test_login.Test_longin testMethod=test_002',
            "{'account': 'admin', 'password': 'e10adc3949ba59abbe56e057f20f883e', 'referer': 'http://127.0.0.1/zentao/my/'}"
            "\nhttp://127.0.0.1/zentao/user-login.html\n<html><meta charset='utf-8'/><style>body{background:white}</style>"
            "<script>parent.location='http://127.0.0.1/zentao/my/';\n\n</script>\n\nTrue\n", ''),
            (0, 'longin.test_login.Test_longin testMethod=test_004', "{'account': 'admin', 'password': 'e10adc3949ba59abbe56e057f20f883e', 'referer': 'http://127.0.0.1/zentao/my/'}"
             "\nhttp://127.0.0.1/zentao/user-login.html\n<html><meta charset='utf-8'/><style>body{background:white}</style>"
             "<script>parent.location='http://127.0.0.1/zentao/my/';\n\n</script>\n\nTrue\n", ''),
            (1, 'longin.test_login.Test_longin testMethod=test_003', "{'account': 'admin', 'password': 'e10adc3949ba59abbe56e057f20f883e', 'referer': 'http://127.0.0.1/zentao/my/'}"
             "\nhttp://127.0.0.1/zentao/user-login.html\n<html><meta charset='utf-8'/><style>body{background:white}</style>"
             "<script>parent.location='http://127.0.0.1/zentao/my/';\n\n</script>\n\nTrue\n", '')]

    #test1 = [(0, 'nwe_user.test_newuser.Test_user testMethod=test_0011', "<html><meta charset='utf-8'/><style>body{background:white}</style><script>alert('『用户名』已经有『zhangsan2』这条记录了。如果您确定该记录已删除，请到后台管理-回收站还原。。\\n')\n</script>\n<html><meta charset='utf-8'/><style>body{background:white}</style><script>if(window.parent) window.parent.document.body.click();\n</script>\n\n这条记录了。如果您确定该记录已删除，请到后台管理-回收站还原\n", '')],[(0, 'nwe_user.test_newuser.Test_user testMethod=test_0011', "<html><meta charset='utf-8'/><style>body{background:white}</style><script>alert('『用户名』已经有『zhangsan2』这条记录了。如果您确定该记录已删除，请到后台管理-回收站还原。。\\n')\n</script>\n<html><meta charset='utf-8'/><style>body{background:white}</style><script>if(window.parent) window.parent.document.body.click();\n</script>\n\n这条记录了。如果您确定该记录已删除，请到后台管理-回收站还原\n", '')]
    runner.run(test)

    report = '../comm/创建用户测试报告.html'

