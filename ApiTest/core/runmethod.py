# coding=utf-8
import requests
import json
'''主流程，执行接口请求'''


def rely_post(rely_run, url, data, header):
    if header is None:
        return rely_run.post(url=url, data=data, verify=False)      # .json()
    else:
        return rely_run.post(url=url, data=data, headers=header, verify=False)


def rely_get(rely_run, url, data, header):
    if header is None:
        return rely_run.get(url, data)  # .json()
    else:
        return rely_run.get(url, data, headers=header, verify=False)


def post_main(url, data, header=None):
    """
    :param url: 接口地址
    :param data:  请求参数
    :param header:
    :return:
    """
    # requests.packages.urllib3.disable_warnings()   # 禁用HTTPS证书警告
    if header is None:
        return requests.post(url=url, data=data, verify=False)      # .json()
    else:
        return requests.post(url=url, data=data, headers=header, verify=False)      # .json()   # verify=False 忽略https


def get_mian(url, data=None, header=None):
    if header is None:
        return requests.get(url, data)     # .json()
    else:
        return requests.get(url, data, headers=header, verify=False)      # .json()


def run_url(rely_run, method, url, data=None, header=None, rely_data=None):
    if rely_data == 'cookie':
        try:
            if method == 'post':
                re = rely_post(rely_run, url, data, header)
            else:
                re = rely_get(rely_run, url, data, header)
            sre = re
        except json.decoder.JSONDecodeError as e:
            sre = '请检查接口URL及路径！' + 'json.decoder.JSONDecodeError:' + str(e) + '；URL:' + url
        except Exception as e:
            sre = e
        return sre
    else:
        try:
            if method == 'post':
                re = post_main(url, data, header)
            else:
                re = get_mian(url, data, header)
            # sre = json.dumps(re, ensure_ascii=False, sort_keys=True, indent=2)
            sre = re
        except json.decoder.JSONDecodeError as e:
            sre = '请检查接口URL及路径！' + 'json.decoder.JSONDecodeError:' + str(e) + '；URL:' + url
        except Exception as e:
            sre = e
        return sre

    # if method == 'post':
    #     return post_main(url, data, header)
    # else:
    #     return get_mian(url, data, header)
