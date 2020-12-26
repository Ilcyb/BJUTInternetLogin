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
