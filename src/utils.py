import os
import json
import socket
from packaging import version
from bs4 import BeautifulSoup
import requests

os.path.expanduser('~')

def get_working_file(working_name):
    home_directory = os.path.expanduser('~')
    working_file = os.path.join(home_directory, working_name)
    if not os.path.exists(working_file):
        with open(working_file, 'w'): pass
    return working_file

def write_info_2_working_file(working_file, info):
    with open(working_file, 'w', encoding='utf-8') as f:
        json.dump(info, f)

def read_info_from_working_file(working_file):
    with open(working_file, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.decoder.JSONDecodeError:
            return {}

def exit_gracefully(signum, frame):
    print('退出Keep-Alive模式')
    exit()

def parse_internet_type(type):
    if type in ['4', 'ipv4', 'IPV4', 'IPv4', 'v4']:
        return 'IPv4'
    elif type in ['6', 'ipv6', 'IPV6', 'IPv6', 'v6', 'Ipv6']:
        return 'IPv6'
    elif type.upper() in ['A', 'ALL']:
        return 'All'
    return type

def parse_action_type(**kwargs):
    login = kwargs['login']
    logout = kwargs['logout']
    query_info = kwargs['query_info']
    keep_alive = kwargs['keep_alive']

    if login:
        return 'login'
    elif logout:
        return 'logout'
    elif query_info:
        return 'query_info'
    elif keep_alive:
        return 'keep_alive'
    
    return 'login'

# 获取本机IPv4地址
def my_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('192.0.0.8', 1027))
    except socket.error:
        return None
    return s.getsockname()[0]

# 获取本机IPv6地址
def my_ipv6():
    s = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
    try:
        s.connect(('2001:db8::', 1027))
    except socket.error:
        return None
    return s.getsockname()[0]

# 检查是否有可更新的新版本
def check_version(current_version):
    r = requests.get('https://pypi.org/project/bjut-internet-login-tool/', timeout=2)
    project_doc = BeautifulSoup(r.text, features="html.parser")
    project_name = project_doc.find('h1', {'class':'package-header__name'}).text.strip(' \n')
    version_index = project_name.find(' ')
    latest_version = project_name[version_index+1:]

    if version.parse(latest_version) > version.parse(current_version):
        return True, latest_version
    else:
        return False, None
