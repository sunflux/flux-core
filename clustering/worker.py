import threading
import json
import socket

from schedulers.timerscheduler import RepeatedTimer
from multiprocessing import Queue
from pathos import multiprocessing as pmp
from clustering import messagecreator, messagehandler
from messagehandlers import funchandler, recipehandler

from amqpcluster import amqppublisher
from amqpcluster import amqpconsumer


class Worker(object):

    def __init__(self, worker_id, name, worker_config):
        self.id = worker_id
        self.name = name
        self.worker_config = worker_config

        self.consumer_q = Queue()
        self.processed_q = Queue()
        self.pool = pmp.Pool(processes=self.worker_config['concurrency'])

        self.__init_consumer(self.worker_config['consumer_config'])
        self.__init_publisher(self.worker_config['publisher_config'])

        self.timer = RepeatedTimer(worker_config['refresh_interval'], self.invoke_func)

        self.pub_process = threading.Thread(target=self.publisher.run)
        self.consumer_process = threading.Thread(target=self.consumer.run)

        self.__init_handlers()

    def __init_handlers(self):
        self.handlers = []
        self.handlers.append({'name': 'recipe', 'op': recipehandler.RecipeHandler(self.pool, {})})
        self.handlers.append({'name': 'func', 'op': funchandler.FuncHandler(self.pool, {})})

    def __init_consumer(self, consumer_config):
        consumer_type = consumer_config['type'].split('.')[0]
        constructor = getattr(globals()[consumer_type], consumer_config['type'].split('.')[1])
        self.consumer = constructor(consumer_config, self.consumer_q)

    def __init_publisher(self, publisher_config):
        publisher_type = publisher_config['type'].split('.')[0]
        constructor = getattr(globals()[publisher_type], publisher_config['type'].split('.')[1])
        self.publisher = constructor(publisher_config, self.processed_q)

    def join(self):
        self.pool.join()

    def start(self):
        self.pool = pmp.Pool(processes=self.worker_config['concurrency'])
        self.pub_process.start()
        self.consumer_process.start()
        self.timer.start()

    def stop(self):
        self.pub_process.join()
        self.consumer_process.join()
        self.timer.cancel()

    def invoke_func(self):
        if self.consumer_q.qsize() == 0:
            return
        q_msg = (self.consumer_q.get())
        msg = json.loads(q_msg)

        print('worker %s is doing %s, %s' % (self.id, msg, msg))

        handler_name = msg['handler']
        handler = next(filter(lambda h: h['name'] == handler_name, self.handlers))
        print('%s is the handler chosen for bulk %s ' % (handler, msg['bulk_id']))
        processed_bulk = handler['op'].handle_message(msg)
        result = messagecreator.rpc_wrapped_result(processed_bulk, msg['node_id'], msg['flow_id'], msg['log_msg_id'])

        self.processed_q.put(result)


if __name__ == '__main__':
    worker = Worker('%s-worker' % socket.gethostname(), 'node_worker',
                    {
                        "refresh_interval": 0,
                        "concurrency": 6,
                        "consumer_config": {
                            "type": "amqpconsumer.AsyncConsumer",
                            "exchange": "flashapp",
                            "exchange_type": "direct",
                            "queue": "flash1",
                            "routing_key": "flash1.slave1",
                            "amqp_url": "amqp://user:123@alpha:5672/%2F?connection_attempts=3&heartbeat_interval=3600"
                        },
                        "publisher_config": {
                            "type": "amqppublisher.AsyncPublisher",
                            "exchange": "flashapp",
                            "exchange_type": "direct",
                            "queue": "flash1callback",
                            "routing_key": "flash1.callback",
                            "amqp_url": "amqp://user:123@alpha:5672/%2F?connection_attempts=3&heartbeat_interval=3600"
                        }
                    })
    worker.start()

