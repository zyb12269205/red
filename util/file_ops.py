__author__ = 'zhanyingbo'

import json
import os

def save_file(content, file_path, force=False):
    if file_exist(file_path) and not force:
        return True
    try:
        f = open(file_path, 'w')
        f.write(json.dumps(content))
        f.close()
        return True
    except:
        return False

def read_file(file_path):
    try:
        f = open(file_path, 'r')
        result = json.loads(f.read())
        f.close()
        return result
    except:
        return NULL

def file_exist(file_path):
    if os.path.isfile(file_path):
        return True
    return False