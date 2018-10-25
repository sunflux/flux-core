import uuid

from fbp.distributednode import DistributedNode


class FuncNode(DistributedNode):

    def __init__(self, node_id, name, concurrency, relations_config, node_config, flow_id, broker):
        DistributedNode.__init__(self, node_id, name, concurrency, relations_config, node_config, flow_id, broker)
        self.func = self.node_config["node_properties"]["func"]

    def request_bulk_partition(self, msgs_bulk_partition, log_msg_id):
        bulk_id = str(uuid.uuid4())
        request = {
            'func': self.func,
            'handler': self.node_config['node_properties']['handler'],
            'msgs_bulk': msgs_bulk_partition,
            'node_config': self.node_config['node_properties'],
            'bulk_id': bulk_id,
            'node_id': self.id,
            'flow_id': self.flow_id,
            'log_msg_id': log_msg_id
        }
        print(request)
        return request
