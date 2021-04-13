import sys
import os
curPath = os.path.abspath(os.path.dirname(__file__))
sys.path.append(curPath)

from login import Wireless, Wire
from utils import *

import argparse

action_name = {
    'login': '登录',
    'query_info': '查询信息',
    'logout': '注销'
}

require_account_actions = ['login', 'query_info', 'keep_alive']

APP_NAME = '.bjutInternet'
CONFIG_FILE = get_working_file(APP_NAME)

def main():
    parser = argparse.ArgumentParser(prog='bjutlogin', description="BJUT Login command line tools.")
    parser.add_argument('--username', '-u', type=str, default=None, help='校园网账号')
    parser.add_argument('--password', '-p', type=str, default=None, help='校园网密码')
    parser.add_argument('--type', '-t', type=str, help='IPv4(4)、IPv6(6) or All 默认为同时登录v4与v6', default='All')
    action_group = parser.add_mutually_exclusive_group()
    action_group.add_argument('--login', action ='store_true', help='登录')
    action_group.add_argument('--logout', action ='store_true', help='注销')
    action_group.add_argument('--keep-alive', '-k', action='store_true', help='保持登录状态，掉线后自动重连')
    action_group.add_argument('--query', '-q', action='store_true', help='查询校园网账户信息')
    parser.add_argument('--remember', action='store_true', help='记住账号密码')
    connection_group = parser.add_mutually_exclusive_group()
    connection_group.add_argument('--wire', action ='store_true', help='有线连接')
    connection_group.add_argument('--wireless', action ='store_true', help='无线连接')

    args = parser.parse_args()

    action = None
    login_type = parse_internet_type(args.type)
    network_type = None

    action = parse_action_type(**dict(login=args.login, logout=args.logout, query_info=args.query, keep_alive=args.keep_alive))

    if (action in require_account_actions) and (args.username is None or args.password is None):
        saved_info = read_info_from_working_file(CONFIG_FILE)
        if saved_info.get('username', None) is not None and saved_info.get('password', None) is not None:
            args.username = saved_info['username']
            args.password = saved_info['password']
            print('使用已保存的密码')
        else:
            print('{}操作需要输入账号与密码'.format(action_name[action]))
            exit(-1)

    if not args.wire and not args.wireless:
        print('没有指定网络类型，默认为有线连接')
        network_type = 'wire'
    elif args.wire:
        network_type = 'wire'
    else:
        network_type = 'wireless'

    if args.remember:
        save_info = {
            'username' : args.username,
            'password' : args.password
        }
        write_info_2_working_file(CONFIG_FILE, save_info)

    login_object = Wire(args.username, args.password, login_type) if network_type == 'wire' else Wireless(args.username, args.password, login_type)
    getattr(login_object, action)() 

if __name__ == '__main__':
    main()