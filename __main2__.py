import threading
import multiprocessing as mp
import numpy as np

import multiprocessing
import time
import json
import threading

from datetime import datetime, timedelta
from dateutil import parser


def func(record):
    print('processing %s' % record)
    time.sleep(2)

    return record


def print_result(result):
    print('Result %s' % result)


def make_repeater(delay, fun, *a, **k):
    def wrapper(*a, **k):
        while True:
            fun(record)
            time.sleep(delay)
    return wrapper


if __name__ == '__main__':
    # Establish communication queues
    # Start consumers

    num_consumers = multiprocessing.cpu_count() * 2
    records = []
    json_string = """bla"""
    for i in range(100):
        #record = json.loads(json_string)
        record = json_string + str(i)
        records.append(record)

    pool = mp.Pool(processes=num_consumers)

    #results = [pool.apply_async(func, args=(record,)) for record in records]

    def run_pool():
        for i in range(5):
            print("starting again!")
            pool.map_async(func, records, callback=print_result)
            time.sleep(1)
    t1 = threading.Thread(target= run_pool)
    t1.start()

    t1.join()


#    results = [pool.map(func, args=(record,)) for record in records]


    pool.close()
    pool.join()

    #for result in results:
        #print('Result:', result)

