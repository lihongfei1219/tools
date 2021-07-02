# coding=utf-8
"""
@time: 2021-07-02
@author: 李飞飞
功能：
    实现了借助某度的API实现翻译功能
思路：
    1.通过抓包找到检测语言URL和执行翻译URL
    2.发现执行翻译的URL发送请求时携带的一个参数sign是动态生成的（重点！！！）
    3.去JS文件中全局搜索sign生成对应的函数
    4.前端断点调试，把对应的JS加密sign的方式保存到本地，然后进行测试
    5.执行翻译
"""

import re
import execjs
import requests

class TranslateMoudu:
    def __init__(self, keywords):
        """
        :param keywords:待检测语言
        """
        self.keywords = keywords
        self.url_root = 'http://fanyi.baidu.com/'  # 翻译根url
        self.url_langdetect = 'https://fanyi.baidu.com/langdetect'  # 检测语言url
        self.url_trans = 'https://fanyi.baidu.com/v2transapi'  # 执行翻译url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.81 Safari/537.36',
            'origin': 'https://fanyi.baidu.com',
            'referer': 'https://fanyi.baidu.com/?aldtype=16047'
        }
        self.data_langdetect = {
            'query': self.keywords
        }
        self.session = requests.session()
        self.session.headers = self.headers


    def langdetect(self):
        """
        发送请求,检测输入的语言类型
        :return: 正常:en:英文,zh:中文;异常:None
        """
        try:
            response = self.session.post(self.url_langdetect, data=self.data_langdetect)
            response_dict = response.json()  # {'error': 0, 'msg': 'success', 'lan': 'zh'}
            if response_dict.get('error') == 0:
                print(response_dict.get('lan'))
                return response_dict.get('lan')
        except Exception as e:
            print(e)

    def get_token_gtk(self):
        """
        获取token
        :return:(token)
        """
        response = self.session.get(self.url_root)
        response_str = response.content.decode()
        # 注意双引号问题
        token = re.findall(r"token: '(.*?)'", response_str)[0]
        return token


    def translate(self, lan):
        """
        翻译功能
        :param lan:
        :return:
        """
        token = self.get_token_gtk()
        data = {
            'from': lan,
            'to': 'en' if lan == 'zh' else 'zh',
            'query': self.keywords,
            'transtype': 'translang',
            'simple_means_flag': 3,
            'sign': self.get_sign(),  # 此参数需破解,是主角
            'token': token

        }
        response = self.session.post(self.url_trans, data=data)
        response_dict = response.json()
        ret = response_dict['trans_result']['data'][0]['dst']
        return ret

    def get_sign(self):
        with open("code.js", "r") as fp:
            js_data = fp.read()
        sign = execjs.compile(js_data).call("e", self.keywords)
        return sign


    def run(self):
        # 1.检测输入的语言类型
        lan = self.langdetect()
        if lan is None:
            return
        # 2.翻译
        ret = self.translate(lan)
        print('%s ==> %s' % (self.keywords, ret))  # 中国-->China

def main():
    while True:
        keywords = input('please input the keywords:')
        if keywords == "0":
            break
        baidu_fanyi = TranslateMoudu(keywords)
        baidu_fanyi.run()

if __name__ == '__main__':
    main()