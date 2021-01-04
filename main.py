# coding:utf-8

import requests
import random
import datetime
import time
import json
import math


class Music:
    def __init__(self, uin, pwd, api, sc_key, country_code=86):
        self.uin = uin
        self.pwd = pwd
        self.country_code = country_code
        self.sc_key = sc_key
        self.api = api
        self.grade = [10, 40, 70, 130, 200, 400, 1000, 3000, 8000, 20000]
        self.ls = []
        self.check_api()

    """
    带上用户的cookie去发送数据
    url:完整的URL路径
    postJson:要以post方式发送的数据
    返回response
    """

    def get_response(self, url, post_json):
        response = requests.post(url, data=post_json, headers={'Content-Type': 'application/x-www-form-urlencoded'},
                                 cookies=self.cookies)
        return response

    """
    登录
    """

    def login(self):
        data = {"uin": self.uin, "pwd": self.pwd, "countrycode": self.country_code, "r": random.random()}
        if '@' in self.uin:
            url = self.api + '?do=email'
        else:
            url = self.api + '?do=login'
        response = requests.post(url, data=data, headers={'Content-Type': 'application/x-www-form-urlencoded'})
        code = json.loads(response.text)['code']
        self.name = json.loads(response.text)['profile']['nickname']
        self.uid = json.loads(response.text)['account']['id']
        if code == 200:
            self.error = ''
        else:
            self.error = '登录失败，请检查账号'
        self.cookies = response.cookies.get_dict()
        self.log('登录成功')

    """
    每日签到
    """

    def sign(self):
        url = self.api + '?do=sign'
        response = self.get_response(url, {"r": random.random()})
        data = json.loads(response.text)
        if data['code'] == 200:
            self.log('签到成功')
        else:
            self.log('重复签到')

    """
    每日打卡300首歌
    """

    def daka(self):
        url = self.api + '?do=daka'
        response = self.get_response(url, {"r": random.random()})
        self.log(response.text)

    """
    查询用户详情
    """

    def detail(self):
        url = self.api + '?do=detail'
        data = {"uid": self.uid, "r": random.random()}
        response = self.get_response(url, data)
        data = json.loads(response.text)
        self.level = data['level']
        self.listenSongs = data['listenSongs']
        self.log('获取用户详情成功')

    """
    Server推送
    """

    def server(self):
        if self.sc_key == '':
            return
        url = 'https://sc.ftqq.com/' + self.sc_key + '.send'
        self.diyText()  # 构造发送内容
        response = requests.get(url, params={"text": self.title, "desp": self.content})
        data = json.loads(response.text)
        if data['errno'] == 0:
            self.log('用户:' + self.name + '  Server酱推送成功')
        else:
            self.log('用户:' + self.name + '  Server酱推送失败,请检查sckey是否正确')

    """
    自定义要推送到微信的内容
    title:消息的标题
    content:消息的内容,支持MarkDown格式
    """

    def diyText(self):
        for count in self.grade:
            if self.level < 10:
                if self.listenSongs < 20000:
                    if self.listenSongs < count:
                        self.tip = '还需听歌' + str(count - self.listenSongs) + '首即可升级'
                        break
                else:
                    self.tip = '你已经听够20000首歌曲,如果登录天数达到800天即可满级'
            else:
                self.tip = '恭喜你已经满级!'
        if self.error == '':
            state = ("- 目前已完成签到\n"
                     "- 今日共打卡" + str(self.dakanum) + "次\n"
                                                     "- 今日共播放" + str(self.dakaSongs) + "首歌\n"
                                                                                       "- 还需要打卡" + str(self.day) + "天")
            self.title = ("网易云今日打卡" + str(self.dakaSongs) + "首，已播放" + str(self.listenSongs) + "首")
        else:
            state = self.error
            self.title = '网易云听歌任务出现问题！'
        self.content = (
                "------\n"
                "#### 账户信息\n"
                "- 用户名称：" + str(self.name) + "\n"
                                             "- 当前等级：" + str(self.level) + "级\n"
                                                                           "- 累计播放：" + str(self.listenSongs) + "首\n"
                                                                                                               "- 升级提示：" + self.tip + "\n\n"
                                                                                                                                      "------\n"
                                                                                                                                      "#### 任务状态\n" + str(
            state) + "\n\n"
                     "------\n"
                     "#### 注意事项\n- 网易云音乐等级数据每天下午2点更新 \n\n"
                     "------\n"
                     "#### 打卡日志\n" + self.dakaSongs_list + "\n\n")

    """
    打印日志
    """

    def log(self, text):
        time_stamp = datetime.datetime.now()
        print(time_stamp.strftime('%Y.%m.%d-%H:%M:%S') + '   ' + str(text))
        self.time = time_stamp.strftime('%H:%M:%S')
        self.ls.append("- [" + self.time + "]    " + str(text) + "\n\n")

    """
    开始执行
    """

    def start(self):
        try:
            self.ls.append("- 初始化完成\n\n")
            self.login()
            self.sign()
            self.detail()
            counter = self.listenSongs
            self.ls.append("- 开始打卡\n\n")
            for i in range(1, 10):
                self.daka()
                # self.log('用户:' + self.name + '  第' + str(i) + '次打卡成功,即将休眠30秒')
                self.log('第' + str(i) + '次打卡成功')
                time.sleep(10)
                self.dakanum = i
                self.detail()
                self.dakaSongs = self.listenSongs - counter
                self.log('今日已打卡' + str(self.dakaSongs) + '首')
                if self.dakaSongs == 300:
                    break

            if self.listenSongs >= 20000:
                self.day = 0
            else:
                self.day = math.ceil((20000 - self.listenSongs) / 300)

            self.ls.append("- 打卡结束\n\n")
            self.ls.append("- 消息推送\n\n")
            self.dakaSongs_list = ''.join(self.ls)
            self.server()
        except Exception as e:
            self.log('用户任务执行中断,请检查账号密码是否正确')
            self.log(e)
        else:
            self.log('用户:' + self.name + '  今日任务已完成')

    def check_api(self):
        url = self.api + '?do=check'
        response = requests.get(url)
        if response.status_code == 200:
            self.log('api测试正常')
            print('api测试正常')
        else:
            self.log('api测试正常')
            print('api测试异常')


if __name__ == '__main__':
    uin = input()
    pwd = input()
    api = input()
    sc_key = input()
    task = Music(uin, pwd, api, sc_key)
    task.start()
