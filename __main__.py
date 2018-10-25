import multiprocessing as mp
import numpy as np

import multiprocessing
import time
import json

from dateutil import parser


class Consumer(multiprocessing.Process):

    def __init__(self, task_queue, result_queue, func):
        multiprocessing.Process.__init__(self)
        self.task_queue = task_queue
        self.result_queue = result_queue
        self.func = func

    def run(self):
        proc_name = self.name
        while True:
            next_task = self.task_queue.get()
            if next_task is None:
                # Poison pill means shutdown
                print ('%s: Exiting' % proc_name)
                self.task_queue.task_done()
                break
            #print ('%s: %s' % (proc_name, next_task))
            #answer = next_task()
            answer = self.func(next_task.args)
            self.task_queue.task_done()
            self.result_queue.put(answer)
        return


class Task(object):
    def __init__(self, record):
        self.record = record

    def __call__(self):
        time.sleep(0.1)  # pretend to take some time to do the work

        for attribute in self.record:
            if 'date' in attribute:
                self.record[attribute] = parser.parse(self.record[attribute]).strftime('%Y-%m-%d %H:%M:%S %z')

        return self.record

    def __str__(self):
        return self.record


class Pool(object):

    def __init__(self, concurrency, func):
        self.tasks = multiprocessing.JoinableQueue()
        self.results = multiprocessing.Queue()
        self.consumers = [Consumer[self.tasks, self.results] for i in range(concurrency)]
        self.func = func

    def start(self):
        for consumer in self.consumers:
            consumer.start()

    def stop(self, focred=False):
        self.tasks.join()
        if focred:
            for consumer in consumers:
                consumer.join()

    def apply(self, func, msgs_bulk):
        for msg in msgs_bulk:
            self.tasks.put(msg)


if __name__ == '__main__':
    # Establish communication queues
    tasks = multiprocessing.JoinableQueue()
    results = multiprocessing.Queue()

    # Start consumers
    num_consumers = multiprocessing.cpu_count() * 2
    print
    ('Creating %d consumers' % num_consumers)
    consumers = [Consumer(tasks, results)
                 for i in range(num_consumers)]
    for consumer in consumers:
        consumer.start()

    # Enqueue jobs
    num_jobs = 10
    for i in range(num_jobs):
        json_string ="""
            {
                "date1": "2013/12/23 10:59:22",
                "aaadate1": "2015/12/23 12:59:22"
            }
            """
        record = json.loads(json_string)
        tasks.put(Task(record))



    # Add a poison pill for each consumer
    for i in range(num_consumers):
        tasks.put(None)

    # Wait for all of the tasks to finish
    tasks.join()

    # Start printing results
    while num_jobs:
        result = results.get()
        print('Result:', result)
        num_jobs -= 1