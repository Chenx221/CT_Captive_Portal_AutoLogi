import urllib.parse
import requests
import logging

# 日志
logger = logging.getLogger()
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
logger.addHandler(console_handler)
file_handler = logging.FileHandler('output.log')
file_handler.setLevel(logging.INFO)
logger.addHandler(file_handler)

# 登陆凭证
username = ''
password = ''

# 测试用途
JSESSIONID = ''
DEBUGINFO = 0

url = 'http://www.msftconnecttest.com/redirect'
headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'en-US,en;q=0.9',
    'Proxy-Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'
}

response = requests.get(url, headers=headers, verify=False)
if DEBUGINFO == 1:
    logger.info("初始化调试信息:" + response.text)

search_string = 'src="/style/enterprise/pc/index.jsp?paramStr='
if response.text.find(search_string) == -1:
    logger.info("看起来已经连接上了网络")
else:
    if JSESSIONID == '':
        JSESSIONID = response.cookies['JSESSIONID']
    logger.info("JSESSIONID:" + JSESSIONID)

    # Decode URL
    encoded_url = response.text.split(search_string)[1].split('"')[0]
    decoded_url = urllib.parse.unquote(encoded_url)
    logger.info("encoded_url:" + encoded_url)

    pre_login_url = "http://106.60.4.60:8016/style/enterprise/pc/index.jsp"
    pre_login_params = {
        "paramStr": encoded_url
    }
    pre_login_headers = {
        "Proxy-Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Referer": response.url,
        "Accept-Language": "en-US,en;q=0.9",
        "Cookie": f"JSESSIONID={JSESSIONID}",
    }
    pre_login_response = requests.get(pre_login_url, params=pre_login_params, headers=pre_login_headers)

    login_url = "http://106.60.4.60:8016/authServlet"
    login_headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "en-US,en;q=0.9",
        "Cache-Control": "max-age=0",
        "Proxy-Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": f"JSESSIONID={JSESSIONID}",
        "Origin": "http://106.60.4.60:8016",
        "Referer": pre_login_response.url,
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
    }

    login_data = {
        "UserType": "2",
        "province": "",
        "paramStr": decoded_url,
        "pwdType": "2",
        "UserName": username,
        "PassWord": password
    }

    login_response = requests.post(login_url, headers=login_headers, data=login_data)

    if DEBUGINFO == 1:
        logger.info("登录调试信息:" + login_response.text)

    # 检查响应状态码
    logger.info(login_response.status_code)
    if login_response.status_code == 200:
        if "login_fail.jsp" in login_response.url:
            logger.error("登录失败，请检查登陆凭证是否正确或账号是否异常")
        elif "logon.jsp" in login_response.url:
            logger.info("login success")
    else:
        logger.error(login_response.status_code)
