config = {
    'login_url':{
    'wire_ipv4': 'https://lgn.bjut.edu.cn/',
    'wire_ipv6': 'https://lgn6.bjut.edu.cn/',
    'wire_all': ['https://lgn6.bjut.edu.cn/V6?https://lgn.bjut.edu.cn', 'https://lgn.bjut.edu.cn/'],
    'wireless_ipv4': 'http://wlgn.bjut.edu.cn/drcom/login',
    'wireless_ipv6': 'https://lgn6.bjut.edu.cn',
    'wireless_all': ''
    },
    'logout_url':{
    'wire_ipv4': 'http://lgn.bjut.edu.cn/F.htm',
    'wire_ipv6': 'http://lgn6.bjut.edu.cn/F.htm',
    'wire_all': 'http://lgn.bjut.edu.cn/F.htm',
    'wireless_ipv4': 'http://wlgn.bjut.edu.cn/drcom/logout',
    'wireless_ipv6': 'http://lgn6.bjut.edu.cn/F.htm',
    'wireless_all': ''
    },
    'query_url': {
        'ipv4': 'http://lgn.bjut.edu.cn/',
        'ipv6': 'http://lgn6.bjut.edu.cn/',
        'all': 'http://lgn.bjut.edu.cn/'
    },
    'jfself_url': {
        'jf_login_index_url': 'https://jfself.bjut.edu.cn/nav_login',
        'jf_login_action_url': 'https://jfself.bjut.edu.cn/LoginAction.action',
        'jf_login_skin_url': 'https://jfself.bjut.edu.cn/getSkinList',
        'jf_login_randomcode_url': 'https://jfself.bjut.edu.cn/RandomCodeAction.action',
        'jf_myip_url': 'https://jfself.bjut.edu.cn/nav_offLine'
    },
    'project_url': 'https://github.com/Ilcyb/BJUTInternetLogin'
}


login_error_msg = {
    'Rad:userid error1': '账号不存在',
    'Rad:ldap auth error': '密码错误'
}

logout_error_msg = {
    'Logout Error(-1)': '没有登录，无法注销',
}

type_display = {
    'IPV4': ' IPv4 ',
    'IPV6': ' IPv6 ',
    'ALL': ' IPv4 及 IPv6 '
}

from sys import int_info
import requests
import json
import re
import time
import datetime
import signal
import random

from requests.exceptions import Timeout
from utils import exit_gracefully, my_ipv6
from bs4 import BeautifulSoup

class Login:

    def __init__(self, username, passwd, type) -> None:
        self.username = username
        self.passwd = passwd
        if type.upper() not in ['IPV4', 'IPV6', 'ALL']:
            raise ValueError('type must be IPv4, IPv6 or All.')
        self.login_url = config['login_url']['{}_{}'.format(self.__class__.__name__, type).lower()]
        self.logout_url = config['logout_url']['{}_{}'.format(self.__class__.__name__, type).lower()]
        self.type = type.upper()
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
                    # self.query_info()
                    return
                time = int(self.time_re.search(r.text).group(1))
                flow = int(self.flow_re.search(r.text).group(1))
                fee = int(self.fee_re.search(r.text).group(1))
                hours = int(time / 60)
                mins = int(time - (hours*60))
                Gbytes = int(flow/(1024*1024))
                Mbytes = int((flow-(Gbytes*1024*1024))/1024)
                fee = fee/10000
                print('\n账户信息：\n当前已用流量：{} GB {} MB\n当前已用时长：{} 小时 {} 分钟\n当前账户余额：{} 元'.format(Gbytes, Mbytes, hours, mins, fee))
                self.get_online_ip()
            except Exception as e:
                print(r)
                print(r.text)
                print('查询信息页面布局已发送改变，请更新程序')
        
    def is_login(self):
        r = requests.get(config['query_url'][self.type.lower()])
        r.raise_for_status()
        if '登录' in r.text:
            return False
        return True

    def keep_alive(self):
        minutes = 10
        loss_count = 2
        check_interval = 300
        self.login_attempt_record = []
        signal.signal(signal.SIGINT, exit_gracefully)
        print('Keep-Alive模式将会持续检测{}下的{}登录状态，如若检测到掉线则会自动重新登录。'.format(self.connect_method, self.type))
        print('{}分钟内连续掉线{}次以上将会判断为竞态登录，将会自动结束Keep-Alive模式，Ctrl+C手动退出'.format(minutes, loss_count))
        while True:
            is_login = self.is_login()
            if not is_login:
                now_time = time.time()
                if len(self.login_attempt_record) >= loss_count and now_time - self.login_attempt_record[-1*loss_count] < 60*minutes:
                    print('检测到{}分钟内连续掉线{}次以上，自动结束Keep-Alive模式'.format(minutes, loss_count))
                    break
                print('[{}]:当前为离线状态，自动重连'.format(datetime.datetime.fromtimestamp(now_time).isoformat(timespec='seconds')))
                self.login()
                self.login_attempt_record.append(now_time)
            # keep-alive模式会消耗流量？ 肯定是哪里有问题，暂且先把sleep时间变长
            time.sleep(check_interval)

    def get_online_ip(self):
        login_headers = {
            'Origin': 'https://jfself.bjut.edu.cn',
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        }
        session = requests.Session()

        try:
            login_index_response = session.get(url=config['jfself_url']['jf_login_index_url'], headers=login_headers)
            login_index_response.raise_for_status()

            checkcode_index_begin = login_index_response.text.find('checkcode=')+len('checkcode="')
            checkcode_index_end = login_index_response.text[checkcode_index_begin:].find('";') + checkcode_index_begin
            checkcode = login_index_response.text[checkcode_index_begin:checkcode_index_end]

            response = session.get(url=config['jfself_url']['jf_login_skin_url'], headers=login_headers)
            response.raise_for_status()
            response = session.get(url=config['jfself_url']['jf_login_randomcode_url'], headers=login_headers, params=dict(randomNum=random.random()))
            response.raise_for_status()

            login_raw_data = 'account={}&password={}&code=&checkcode={}&Submit=%E7%99%BB+%E5%BD%95'
            login_action_response = session.post(url=config['jfself_url']['jf_login_action_url'], data=login_raw_data.format(self.username, self.passwd, checkcode), headers=login_headers)
            login_action_response.raise_for_status()

            ip_reponse = session.get(url=config['jfself_url']['jf_myip_url'], headers=login_headers)
            ip_reponse.raise_for_status()

            struct_doc = BeautifulSoup(ip_reponse.text, features="html.parser")
            ip_table = struct_doc.tbody
            ip_tr_list = ip_table.find_all('tr')
            ips = []
            for ip_tr in ip_tr_list:
                ip_info = {}
                ipv4 = ip_tr.td.text
                ipv6 = ip_tr.find_all('td')[1].text

                if ipv4=='\xa0':
                    pass
                else:
                    ip = ipv4[:-1]
                    ip_info['IPv4'] = ip
                
                if ipv6=='\xa0':
                    pass
                else:
                    ip = ipv6[:-1]
                    ip_info['IPv6'] = ip
                
                ips.append(ip_info)
        
        except (requests.RequestException):
            print('无法查询在线IP，请检查网络连接')
        except Exception as e:
            print('无法查询在线IP，请更新程序或提交ISSUE:https://github.com/Ilcyb/BJUTInternetLogin/issues/new')
        else:
            print('当前在线终端:[{}/2]'.format(len(ips)))
            for idx in range(len(ips)):
                ip_info = ips[idx]
                s = '\t终端{} '.format(idx+1)
                if 'IPv4' in ip_info:
                    s += '\tIPv4:{}'.format(ip_info['IPv4'])
                if 'IPv6' in ip_info:
                    s += '\tIPv6:{}'.format(ip_info['IPv6'])
                print(s)


class Wire(Login):
    
    def __init__(self, username, passwd, type) -> None:
        super(Wire, self).__init__(username, passwd, type)
        self.connect_method = 'wire'
        self.init_login_request_data()
        self.init_logout_request_data()
    
    def init_login_request_data(self):
        if self.type == 'IPV4':
            datas = {
                'DDDDD': self.username,
                'upass': self.passwd,
                'v46s': 1,
                'v6ip': '',
                '0MKKey': ''
            }
        elif self.type == 'IPV6':
            datas = {
                'DDDDD': self.username,
                'upass': self.passwd,
                'v46s': 2,
                'v6ip': '',
                '0MKKey': ''
            }
        else:
            datas = [
                {
                    'DDDDD': self.username,
                    'upass': self.passwd,
                    'v46s': 0,
                    'v6ip': '',
                    'f4serip': '',
                    '0MKKey': ''
                },
                {
                    'DDDDD': self.username,
                    'upass': self.passwd,
                    '0MKKey': 'Login',
                    'v6ip': my_ipv6()
                }
            ]
        self.login_request_data = datas

    def init_logout_request_data(self):
        if self.type == 'IPV4':
            datas = {}
        else:
            datas = {}
        self.logout_request_data = datas

    def login(self):
        if self.type in ['IPV4', 'IPV6']:
            result = self.request(self.login_url, self.login_request_data, type='POST')
        elif self.type == 'ALL':
            result = self.request(self.login_url[0], self.login_request_data[0], type='POST')
            result = self.request(self.login_url[1], self.login_request_data[1], type='POST')
        result_text = result.text
        if result_text == None:
            print('有线网络{}登录失败!'.format(type_display[self.type]))
            return
        if '登录成功窗' in result_text:
                print('有线网络{}登录成功'.format(type_display[self.type]))
                self.query_info()
        elif '信息返回窗' in result_text:
            print('有线网络{}登录失败'.format(type_display[self.type]))
        else:
            print('有线网络{}登录数据结构发生变化，请更新程序'.format(type_display[self.type]))
    
    def logout(self):
        result = self.request(self.logout_url, self.logout_request_data)
        result_text = result.text
        if result_text == None:
            print('注销失败!')
            return
        if 'Logout Error(-1)' in result_text:
            print('无线网络{}注销失败，未登录无法注销！'.format(type_display[self.type]))
        else:
            print('无线网络{}注销成功'.format(type_display[self.type]))

class Wireless(Login):
    
    def __init__(self, username, passwd, type) -> None:
        super(Wireless, self).__init__(username, passwd, type)
        self.connect_method = 'wireless'
        self.init_login_request_data()
        self.init_logout_request_data()

    def init_login_request_data(self):
        if self.type=='IPV4':
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
        elif self.type=='IPV6':
            datas = {
                'DDDDD': self.username,
                'upass': self.passwd,
                'v46s': '2',
                'v6ip': '',
                '0MKKey':''
            }
        elif self.type=='ALL':
            # TODO support wireless all login
            datas = {}
        self.login_request_data = datas
    
    def init_logout_request_data(self):
        if self.type=='IPV4':
            datas = {
                'callback':'dr1002',
                'jsVersion':'4.1',
                'v':'869',
                'lang':'zh'
            }
        elif self.type=='IPV6':
            datas = {}
        elif self.type=='ALL':
            # TODO
            datas = {}
        self.logout_request_data = datas

    def login(self):
        if self.type == 'IPV4':
            result = self.request(self.login_url, self.login_request_data)
        elif self.type=='IPV6':
            result = self.request(self.login_url, self.login_request_data, type='POST')
        elif self.type=='ALL':
            # TODO
            print('无线网络登录暂不支持一次性同时登录IPv4与IPv6，请分别登录或访问 {} 提出issue'.format(config['project_url']))
            exit()
        result_text = result.text
        if result_text == None:
            print('无线网络{}登录失败!'.format(type_display[self.type]))
            return
        if self.type == 'IPV4':
            try:
                result_text = json.loads(result_text.strip()[7:][:-1])
                login_result = result_text['result']
                if login_result==1:
                    print('无线网络{}登录成功！'.format(type_display[self.type]))
                elif login_result==0:
                    msg = result_text['msga']
                    if msg in login_error_msg:
                        msg = login_error_msg[msg]
                    print('无线网络{}登录失败，{}'.format(type_display[self.type], msg))
            except Exception:
                print(result)
                print(result.text)
                print('无线{}登录数据结构发生变化，请更新程序'.format(type_display[self.type]))
            else:
                if login_result==1:
                    self.query_info()
        else:
            if '登录成功窗' in result_text:
                print('无线网络{}登录成功'.format(type_display[self.type]))
                self.query_info()
            elif '信息返回窗' in result_text:
                print('无线网络{}登录失败'.format(type_display[self.type]))
            else:
                print('无线网络{}登录数据结构发生变化，请更新程序'.format(type_display[self.type]))

    def logout(self):
        result = self.request(self.logout_url, self.logout_request_data)
        result_text = result.text
        if result_text == None:
            print('注销失败!')
            return
        if self.type == 'IPV4':
            try:
                result_text = json.loads(result_text.strip()[7:][:-1])
                login_result = result_text['result']
                if login_result==1:
                    print('无线网络{}注销成功！'.format(type_display[self.type]))
                elif login_result==0:
                    msg = result_text['msga']
                    if msg in logout_error_msg:
                        msg = logout_error_msg[msg]
                    print('无线网络{}注销失败，{}'.format(type_display[self.type], msg))
            except Exception:
                print(result)
                print(result.text)
                print('无线{}注销数据结构发生变化，请更新程序'.format(type_display[self.type]))
        elif self.type == 'IPV6':
            if 'Logout Error(-1)' in result_text:
                print('无线网络{}注销失败，未登录无法注销！'.format(type_display[self.type]))
            else:
                print('无线网络{}注销成功'.format(type_display[self.type]))
        elif self.type=='ALL':
            # TODO
            print('无线网络登录暂不支持一次性同时注销IPv4与IPv6，请分别注销或访问 {} 提出issue'.format(config['project_url']))
            exit()

