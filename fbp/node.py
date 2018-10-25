import json
import abc
import multiprocessing
import redis
import uuid

from pathos import multiprocessing as pmp
from fbp.relationship import RelationManager
from itertools import islice
from fbp.scheduler import Scheduler
from functools import partial
from transform import funcs
from schedulers import *


class Node(object):

    def __init__(self, node_id, name, concurrency, relations_config, node_config, flow_id, broker):

        self.id = node_id
        self.name = name
        self.concurrency = concurrency
        self.node_config = node_config
        self.coords = self.node_config['coords']
        self.flow_id = flow_id

        self.net = RelationManager(['Success', 'Error', 'Failure'])

        # self.pool = multiprocessing.Pool(processes=self.concurrency)
        self.pool = pmp.Pool(processes=self.concurrency)
        self.q = multiprocessing.Queue()
        self.broker = broker

        # self.logger = node_config["logger"]

        # A placeholder for relations: [{"relation_id": ""}]
        self.relations_metadata = relations_config

        # inited from the Flow module ------ Actual relations
        self.src_relations = []
        self.dst_relations = []

        # init scheduler
        self.__init_scheduler(node_config["scheduler_config"])

        self.r = redis.Redis()

    def __init_scheduler(self, scheduler_config):
        scheduler_type = scheduler_config['name'].split('.')[0]
        constructor = getattr(globals()[scheduler_type], scheduler_config['name'].split('.')[1])
        self.scheduler = constructor(scheduler_config["scheduler_id"], scheduler_config["name"], self, scheduler_config)

    def enqueue(self, msgs_bulk):
        print(self.name + ' received ' + str(msgs_bulk))
        self.q.put(msgs_bulk)

    def log_process_msg_start(self, msg):
        print('abu daday')
        self.r.rpush(self.id, msg)
        print('yayo %s' % self.r.lrange(self.id, 0, 10))
        print('abu mamy')

    def log_process_msg_end(self, msg):
        print('remove %s' % msg)
        print('pree %s' % self.r.lrange(self.id, 0, 10))
        self.r.lrem(self.id, msg, 1)
        print('postt %s' % self.r.lrange(self.id, 0, 10))

    def get_node_content(self, start, end):
        contents = self.r.lrange(self.id, start, end)
        return contents

    # Blocking method
    @abc.abstractmethod
    def execute_node(self):
        return

    # process_results = {"success":[], "failed": {}}....
    def on_bulk_processed(self, process_results, msg_id):
        print(self.name + ' on_bulk_processed' + str(process_results))
        for result in process_results:
            relevant_relations = list(
                filter(lambda relation: result['status'] in relation.events, self.dst_relations))

            msgs_bulk = result["bulk"]

            for dst_relation in relevant_relations:
                if result["status"] not in dst_relation.events:
                    pass

                print('relation %s node %s msg %s' % (dst_relation.id, self.name, msgs_bulk))
                print(self.name + ' ' + str(msgs_bulk) + ' ' + str(dst_relation))
                print('Transfers bulk from %s to %s' % (self.id, dst_relation.id))
                # dst_relation.enqueue(msgs_bulk)
                dst_relation.enqueue(self.wrap_bulk_msg(msgs_bulk, msg_id))

        log_msg = {
            'msg_id': msg_id
        }
        self.log_process_msg_end(log_msg)
            # log about data in this relation
            # self.logger.debug(result_type)

    def start(self):
        self.pool = pmp.Pool(processes=self.concurrency, initargs=self.node_config)
        self.scheduler.start()

    def stop(self, forced=False):
        self.scheduler.stop()
        if forced:
            self.pool.terminate()
        else:
            self.pool.close()
            self.pool.join()

    def toJSON(self):
        self.node_config['coords'] = self.coords
        self.node_config['node_id'] = self.id
        return self.node_config

    def _get_msg_bulk(self):
        log_msg_id = str(uuid.uuid4())
        msgs_bulk = {
            'bulk': [],
            'msg_id': log_msg_id
        }

        if len(self.src_relations) > 0:
            if self.q.qsize() > 0:
                msgs_bulk = self.q.get()
                log_msg_id = msgs_bulk['msg_id']
                log_msg = {
                    'msg_id': log_msg_id,
                }
                self.log_process_msg_start(log_msg)
            else:
                return {
                    'bulk': None,
                    'msg_id': log_msg_id
                }
                # return None

        log_msg = {
            'msg_id': log_msg_id,
        }
        self.log_process_msg_start(log_msg)
        return msgs_bulk

    @staticmethod
    def wrap_bulk_msg(msgs_bulk, msg_id=None):
        if msg_id is None:
            msg_id: str(uuid.uuid4())
        return {
            'bulk': msgs_bulk,
            'msg_id': msg_id
        }