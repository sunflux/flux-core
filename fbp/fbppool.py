import  json
import fbp.node
import fbp.flow
import fbp.port
import fbp.scheduler
import fbp.relationship

from clustering.broker import Broker
import uuid
from fbp import initiator, processor, distributednode
from nodes import *


class App(object):

    def __init__(self, config_path, tasks_q, results_q):
        self.__load_config(config_path)

        self.__init_broker()

        self.flows = []
        self.__init_flows()

        self.default_nodes = []
        self.__init_default_node_values()

    def __init_default_node_values(self):
        default_nodes_conf = self.config['default_nodes']
        for default_node in default_nodes_conf:
            node_type = default_node['type'].split('.')[0]
            constructor = getattr(globals()[node_type], default_node['type'].split('.')[1])
            node = constructor("-1", default_node["name"], default_node["concurrency"],
                               default_node["relations_config"], default_node, 'NotAssocisated', self.broker)
            self.default_nodes.append(node)

    def __init_broker(self):
        broker_config = self.config['broker_config']
        self.broker = Broker(broker_config['broker_id'], broker_config['name'], broker_config, self.__on_msg_received)

    def __init_flows(self):
        flows_config = self.config["flows"]
        for flow_config in flows_config:
            flow = fbp.flow.Flow(flow_config["flow_id"], flow_config["name"], flow_config, self.broker)
            self.flows.append(flow)

    def __load_config(self, config_path):
        with open(config_path, 'r') as config_file:
            config = config_file.read()
            self.config = json.loads(config)

    def start_flows(self):
        self.broker.start()
        for flow in self.flows:
            flow.start()

    def __on_msg_received(self, msg):
        flow = next(flow for flow in self.flows if flow.id == msg['flow_id'])
        node = next(n for n in flow.nodes if n.id == msg['node_id'])
        node.on_bulk_processed(msg['result'], msg['msg_id'])

    def generate_node(self, flow_id, node_type):
        node = next((default_node for default_node in self.default_nodes if default_node.name == node_type['type']), None)
        selected_flow = next((flow for flow in self.flows if flow.id == flow_id), None)

        node.id = str(uuid.uuid4())
        selected_flow.nodes.append(node)
        node.flow_id = flow_id
        node.coords = node_type['coords']

        print(node.id)

        return node

    def get_node_content(self, node_id, start):
        for flow in self.flows:
            node = next((n for n in flow.nodes if n.id == node_id), None)
            if node is None:
                # later handle exception thrown by not finding the desired node
                return None
            contents = node.get_node_content(start, 10)
            # data = list(map(lambda c: c.decode('utf-8').replace("'", '"'), contents))
            data = list(map(lambda c: c.decode('utf-8').replace("'", '"').replace('"{', '{').replace('}"', '}'), contents))
            # j = json.loads(data)
            return data


