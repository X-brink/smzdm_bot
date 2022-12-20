"""
什么值得买自动签到脚本
使用github actions 定时执行
@author : stark modify : brink
"""
import requests,os,time,json
from sys import argv

import config
from utils.serverchan_push import push_to_wechat

class SMZDM_Bot(object):
    def __init__(self):
        self.session = requests.Session()
        # 添加 headers
        self.session.headers = config.DEFAULT_HEADERS

    def __json_check(self, msg):
        """
        对请求返回的数据进行进行检查
        1.判断是否 json 形式
        """
        try:
            result = msg.json()
            #print(result)
            return True
        except Exception as e:
            #print(f'Error : {e}')            
            return False

    def load_cookie_str(self, cookies):
        """
        起一个什么值得买的，带cookie的session
        cookie 为浏览器复制来的字符串
        :param cookie: 登录过的社区网站 cookie
        """
        self.session.headers['Cookie'] = cookies

    def checkin(self):
        """
        签到函数
        """
        try:
            url = os.environ["URL"]
        except KeyError:
            if config.URL:
                url = config.URL
            else:
                url = 'https://zhiyou.smzdm.com/user/checkin/jsonp_checkin'
        params = {
            "callback": "myCalback",
            "_": int(time.time()*1000)
        }
        msg = self.session.get(url, params=params)
        if self.__json_check(msg):
            return msg.json()
        msg.raise_for_status()
        msg.encoding = msg.apparent_encoding
        content = msg.text
        data = json.loads(content[content.find("{"):content.rfind(")")])
        if data.get("error_code") == 0:
            res = "张大妈签到成功！！！总签到天数：" + str(data.get("data").get("checkin_num"))
            summary_res = "success, " + str(data.get("data").get("checkin_num")) + " days"
        else:
            res = "签到失败，原因：" + data.get("error_msg")
            summary_res = "failed"
        return res, summary_res


def push_res_to_server(SERVERCHAN_SECRETKEY, res, summary_res):
    if SERVERCHAN_SECRETKEY:
        print('sc_key: ', SERVERCHAN_SECRETKEY)
        if isinstance(SERVERCHAN_SECRETKEY,str) and len(SERVERCHAN_SECRETKEY)>0:
            print('检测到 SCKEY， 准备推送')
            this_text = "什么值得买每日签到" + summary_res
            push_to_wechat(text = this_text,
                            desp = str(res),
                            secretKey = SERVERCHAN_SECRETKEY)

if __name__ == '__main__':
    sb = SMZDM_Bot()
    try:
        cookies = os.environ["COOKIES"]
    except KeyError:
        if config.TEST_COOKIE:
            cookies = config.TEST_COOKIE
    if cookies:
        sb.load_cookie_str(cookies)
        res, summary_res = sb.checkin()
        print(res)
    else:
        res = "缺少cookie,stop"
        print(res)
    try:
        SERVERCHAN_SECRETKEY = os.environ["SERVERCHAN_SECRETKEY"]
    except KeyError:
        if config.SERVERCHAN_SECRETKEY:
            SERVERCHAN_SECRETKEY = config.SERVERCHAN_SECRETKEY
    if SERVERCHAN_SECRETKEY:
        push_res_to_server(SERVERCHAN_SECRETKEY, res, summary_res)
