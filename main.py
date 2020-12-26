from login import Wireless, Wire
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="BJUT Login command line tools.")
    parser.add_argument('--username', '-u', type=str, default=None, help='校园网账号')
    parser.add_argument('--password', '-p', type=str, default=None, help='校园网密码')
    parser.add_argument('--login', action ='store_true', help='登录')
    parser.add_argument('--logout', action ='store_true', help='注销')
    parser.add_argument('--type', '-t', type=str, help='IPv4 or IPv6', default='IPv4')
    parser.add_argument('--wire', action ='store_true', help='有线连接')
    parser.add_argument('--wireless', action ='store_true', help='无线连接')
    parser.add_argument('--query', '-q', action='store_true', help='查询校园网账户信息')

    args = parser.parse_args()

    action = None
    login_type = args.type
    network_type = None


    if not args.login and not args.logout and not args.query:
        print('没有指定操作，默认为登录操作')
        action = 'login'
    elif args.login:
        action = 'login'
    elif args.logout:
        action = 'logout'
    elif args.query:
        action = 'query_info'

    if not args.wire and not args.wireless:
        print('没有指定网络类型，默认为有线连接')
        network_type = 'wire'
    elif args.wire:
        network_type = 'wire'
    else:
        network_type = 'wireless'

    login_object = Wire(args.username, args.password, login_type) if network_type == 'wire' else Wireless(args.username, args.password, login_type)
    getattr(login_object, action)() 
    