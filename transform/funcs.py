import uuid
import os
import datetime

from dateutil import parser as da_parser
from clustering import messagecreator


def list_file(config):
    files = os.listdir(config['dir_path'])
    bulk = []
    for file in files:
        res = {'file': file}
        bulk.append(res)
    return [messagecreator.rpc_func_result("Success", bulk)]


def add_time_stamp(config, msg):
    msg['timestamp'] = datetime.datetime.now().strftime('%y-%m-%d %H:%M:%S')
    return msg


def add_id(config, msg):
    msg['id'] = str(uuid.uuid4())
    return msg
    #return messagecreator.rpc_func_result("Success", msg)


def results_printer(results_printer_config, msg):
    print('printing %s ' % msg)
    return messagecreator.rpc_func_result("Success", msg)


def error_handler(error_handler_config, msg):
    return messagecreator.rpc_func_result("Error", msg)
