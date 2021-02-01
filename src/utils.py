import os
import json

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