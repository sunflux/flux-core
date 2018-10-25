import abc
import json
import threading
import queue
import uuid

from multiprocessing import Queue
from schedulers.timerscheduler import RepeatedTimer
from amqpcluster import amqppublisher
from amqpcluster import amqpconsumer


class Broker(object):

    def __init__(self, broker_id, name, broker_config, rpc_callback):
        self.id = broker_id
        self.name = name
        self._rpc_callback = rpc_callback
        self._broker_config = broker_config

        self.__pub_q = queue.Queue()
        self.__broker_q = Queue()

        self.__init_consumer(self._broker_config['consumer_config'])
        self.__init_publisher(self._broker_config['publisher_config'])

        self.pub_process = threading.Thread(target=self.publisher.run)
        self.consumer_process = threading.Thread(target=self.consumer.run)

        self.timer = RepeatedTimer(0, self.get_items_from_q)

    def __init_consumer(self, consumer_config):
        consumer_type = consumer_config['type'].split('.')[0]
        constructor = getattr(globals()[consumer_type], consumer_config['type'].split('.')[1])
        self.consumer = constructor(consumer_config, self.__broker_q)

    def __init_publisher(self, publisher_config):
        publisher_type = publisher_config['type'].split('.')[0]
        constructor = getattr(globals()[publisher_type], publisher_config['type'].split('.')[1])
        self.publisher = constructor(publisher_config, self.__pub_q)

    def rpc_call(self, request):
        self.__pub_q.put(request)

    def start(self):
        self.pub_process.start()
        self.consumer_process.start()
        self.timer.start()

    def stop(self):
        self.pub_process.join()
        self.consumer_process.join()
        self.timer.cancel()

    def get_items_from_q(self):
        if self.__broker_q.qsize() > 0:
            processed_bulk = json.loads(self.__broker_q.get())
            self._rpc_callback(processed_bulk)

