import re
import requests
import json




url = "https://bbs.deepin.org/home.php"

querystring = {"mod":"space","do":"notice","view":"mypost"}

headers = {
    'User-Agent': "PostmanRuntime/7.15.0",
    'Accept': "*/*",
    'Cache-Control': "no-cache",
    'Postman-Token': "208da1f7-c8fd-4b00-973f-36574cf732f1,b71acf09-8863-4eb9-a446-f083ba45e8b7",
    'Host': "bbs.deepin.org",
    'cookie': "IjNk_2132_saltkey=WxAHHySQ; IjNk_2132_lastvisit=1563857564; IjNk_2132_sid=oh2L2t; IjNk_2132_lastact=1563868873%09home.php%09space",
    'accept-encoding': "gzip, deflate",
    'Connection': "keep-alive",
    'cache-control': "no-cache"
    }

# response = requests.request("GET", url, headers=headers, params=querystring)

# print(response.text)
# print(response.text)
# print(response.cookies)
# print(response.status_code)
# print(response.headers)
# print(response.raw)
# print(response.url)
# print(response.encoding)
# print(response.history)
# print(response.reason)
# print(response.elapsed)
# print(response.request)
# print(response.text)


urls = 'http://192.168.1.109:8080/login/dologin'
data = {
        'username': '60088',
        'password': '123'
}

data = str(data)

print(type(data))

data = json.dumps(data)
print(type(data))
