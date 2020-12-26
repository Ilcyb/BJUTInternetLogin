config = {
    'login_url':{
    'wire_ipv4': '',
    'wire_ipv6': '',
    'wireless_ipv4': 'http://wlgn.bjut.edu.cn/drcom/login',
    'wireless_ipv6': 'https://lgn6.bjut.edu.cn'
    },
    'logout_url':{
    'wire_ipv4': '',
    'wire_ipv6': '',
    'wireless_ipv4': 'http://wlgn.bjut.edu.cn/drcom/logout',
    'wireless_ipv6': 'http://lgn6.bjut.edu.cn/F.htm'
    },
    'query_url': {
        'ipv4': 'http://lgn.bjut.edu.cn/',
        'ipv6': 'http://lgn6.bjut.edu.cn/'
    }
}


login_error_msg = {
    'Rad:userid error1': '账号不存在',
    'Rad:ldap auth error': '密码错误'
}

logout_error_msg = {
    'Logout Error(-1)': '没有登录，无法注销',
}


import requests
import json
import re

from requests.exceptions import Timeout

class Login:

    def __init__(self, username, passwd, type) -> None:
        self.username = username
        self.passwd = passwd
        if type not in ['IPv4', 'IPv6']:
            raise ValueError('type must be IPv4 or IPv6.')
        self.login_url = config['login_url']['{}_{}'.format(self.__class__.__name__, type).lower()]
        self.logout_url = config['logout_url']['{}_{}'.format(self.__class__.__name__, type).lower()]
        self.type = type
        self.time_re = re.compile(r"time='([0-9]+)")
        self.flow_re = re.compile(r"flow='([0-9]+)")
        self.fee_re = re.compile(r"fee='([0-9]+)")
    
    def request(self, url, data, type='GET'):
        try:
            if type == 'GET':
                r = requests.get(url, params=data, timeout=10)
            else:
                r = requests.post(url, data=data, timeout=10)
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print('HTTP Error:{}'.format(e))
            return None
        except requests.exceptions.Timeout as e:
            print('连接登录服务器超时')
            return None
        except requests.exceptions.ConnectionError as e:
            print('连接登录服务器失败，请检查网络连接')
            return None
        except requests.exceptions.RequestException as e:
            print('未经处理的连接错误:{}'.format(e))
            return None
        else:
            return r

    def query_info(self):
        try:
            r = requests.get(config['query_url'][self.type.lower()])
            r.raise_for_status()
        except requests.exceptions.RequestException as e:
            print('connection error:{}'.format(e))
            print('查询账户信息失败!')
            return
        else:
            try:
                if '登录' in r.text:
                    print('处于未登录状态，因此先进行登录再查询信息')
                    self.login()
                    self.query_info()
                    return
                time = int(self.time_re.search(r.text).group(1))
                flow = int(self.flow_re.search(r.text).group(1))
                fee = int(self.fee_re.search(r.text).group(1))
                hours = int(time / 60)
                mins = int(time - (hours*60))
                Gbytes = int(flow/(1024*1024))
                Mbytes = int((flow-(Gbytes*1024*1024))/1024)
                fee = fee/10000
                print('账户信息：\n当前已用流量：{} GB {} MB\n当前已用时长：{} 小时 {} 分钟\n当前账户余额：{} 元'.format(Gbytes, Mbytes, hours, mins, fee))
            except Exception as e:
                print(r)
                print(r.text)
                print('查询信息页面布局已发送改变，请更新程序')
        
        

class Wire(Login):
    
    def __init__(self, username, passwd, type) -> None:
        super(Wire, self).__init__(username, passwd, type)

    

class Wireless(Login):
    
    def __init__(self, username, passwd, type) -> None:
        super(Wireless, self).__init__(username, passwd, type)
        self.init_login_request_data()
        self.init_logout_request_data()

    def init_login_request_data(self):
        if self.type=='IPv4':
            datas = {
                'callback': 'dr1003',
                'DDDDD': self.username,
                'upass': self.passwd,
                '0MKKey': '123456',
                'R1': '0',
                'R2': '',
                'R3': '0',
                'R6': '0',
                'para': '00',
                'v6ip': '',
                'terminal_type': '1',
                'lang': 'zh-cn',
                'jsVersion': '4.1',
                'v': '8809',
                'lang': 'zh',
            }
        else:
            datas = {
                'DDDDD': self.username,
                'upass': self.passwd,
                'v46s': '2',
                'v6ip': '',
                '0MKKey':''
            }
        self.login_request_data = datas
    
    def init_logout_request_data(self):
        if self.type=='IPv4':
            datas = {
                'callback':'dr1002',
                'jsVersion':'4.1',
                'v':'869',
                'lang':'zh'
            }
        else:
            datas = {}
        self.logout_request_data = datas

    def login(self):
        if self.type == 'IPv4':
            result = self.request(self.login_url, self.login_request_data)
        else:
            result = self.request(self.login_url, self.login_request_data, type='POST')
        result_text = result.text
        if result_text == None:
            print('无线网络{}登录失败!'.format(self.type))
            return
        if self.type == 'IPv4':
            try:
                result_text = json.loads(result_text.strip()[7:][:-1])
                login_result = result_text['result']
                if login_result==1:
                    print('无线网络{}登录成功！'.format(self.type))
                elif login_result==0:
                    msg = result_text['msga']
                    if msg in login_error_msg:
                        msg = login_error_msg[msg]
                    print('无线网络{}登录失败，{}'.format(self.type, msg))
            except Exception:
                print(result)
                print(result.text)
                print('无线{}登录数据结构发生变化，请更新程序'.format(self.type))
            else:
                if login_result==1:
                    self.query_info()
        else:
            if '登录成功窗' in result_text:
                print('无线网络{}登录成功'.format(self.type))
                self.query_info()
            elif '信息返回窗' in result_text:
                print('无线网络{}登录失败'.format(self.type))
            else:
                print(result_text)
                print('无线网络{}登录数据结构发生变化，请更新程序'.format(self.type))

    def logout(self):
        result = self.request(self.logout_url, self.logout_request_data)
        result_text = result.text
        if result_text == None:
            print('注销失败!')
            return
        if self.type == 'IPv4':
            try:
                result_text = json.loads(result_text.strip()[7:][:-1])
                login_result = result_text['result']
                if login_result==1:
                    print('无线网络{}注销成功！'.format(self.type))
                elif login_result==0:
                    msg = result_text['msga']
                    if msg in logout_error_msg:
                        msg = logout_error_msg[msg]
                    print('无线网络{}注销失败，{}'.format(self.type, msg))
            except Exception:
                print(result)
                print(result.text)
                print('无线{}注销数据结构发生变化，请更新程序'.format(self.type))
        elif self.type == 'IPv6':
            if 'Logout Error(-1)' in result_text:
                print('无线网络{}注销失败，未登录无法注销！'.format(self.type))
            else:
                print('无线网络{}注销成功'.format(self.type))

