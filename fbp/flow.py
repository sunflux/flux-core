import os
import datetime
import json

from schedulers.timerscheduler import RepeatedTimer
from fbp.node import Node
from fbp.relationship import Relation
from fbp.relationship import RelationManager
from fbp import initiator, processor, distributednode
from nodes import *


class Flow(object):

    def __init__(self, flow_id, name, flow_config, broker):
        self.id = flow_id
        self.name = name
        self.flow_config = flow_config
        self.broker = broker

        self.nodes = []
        self.init_nodes(self.flow_config["nodes"])

        self.relations = []
        self.init_relations(self.flow_config["relations"])
        self.init_nodes_relations()

        self.timer = RepeatedTimer(3, self.store_status)

    def init_nodes(self, nodes_config):

        for node_config in nodes_config:
            node_type = node_config['type'].split('.')[0]
            constructor = getattr(globals()[node_type], node_config['type'].split('.')[1])
            node = constructor(node_config["node_id"], node_config["name"], node_config["concurrency"],
                               node_config["relations_config"], node_config, self.id, self.broker)
            self.nodes.append(node)

    def init_relations(self, relations_config):
        for relation_config in relations_config:
            relation = Relation(relation_config["relation_id"], relation_config["name"], relation_config["type"],
                                relation_config["events"],
                                relation_config["bulks_capacity"], relation_config["src_node_id"],
                                relation_config["dst_node_id"])
            self.relations.append(relation)

    def init_nodes_relations(self):
        for node in self.nodes:
            for relation_placeholder in node.relations_metadata:
                relation = self.__get_relation_by_id(relation_placeholder)[0]
                # The node is the source in this relationship
                if relation.src_node_id == node.id:
                    node.dst_relations.append(relation)
                    relation.src_node = node
                    print('')
                else:
                    # The node is the destination in this relationship
                    if relation.dst_node_id == node.id:
                        node.src_relations.append(relation)
                        relation.dst_node = node
                    # Something went wrong while loading relations
                    else:
                        print("ERROR")

    def start(self):
        # self.nodes[2].start()
        for node in self.nodes:
            node.start()
        self.timer.start()

    def __get_node_by_id(self, node_id):
        return next((node for node in self.nodes if node.id == node_id)), None

    def __get_relation_by_id(self, relation_id):
        return next((relation for relation in self.relations if relation.id == relation_id)), None

    def get_status(self):
        nodes_status = []
        for node in self.nodes:
            node_status = {'node': node.id, 'processing': node.q.qsize()}
            nodes_status.append(node_status)

        relations_status = []
        for relation in self.relations:
            relation_status = {'relation': relation.id, 'enqueued': relation.q.qsize()}
            relations_status.append(relation_status)

        status = {'nodes_status': nodes_status, 'relations_status': relations_status}

        return status

    def store_status(self):
        status = self.get_status()

        # % datetime.datetime.now().strftime('%Y-%m-%d_%H_%M_%S')
        status_path = os.path.join(self.flow_config['status_dir'], 'flow1-status.json')
        with open(status_path, 'w+') as status_file:
            json.dump(status, status_file)
            status_file.write('\n')
