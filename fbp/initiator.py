from fbp.node import Node


class Initiator(Node):

    def __init__(self, node_id, name, concurrency, relations_config, node_config):
        Node.__init__(self, node_id, name, concurrency, relations_config, node_config)

    def execute_node(self):
        processed_bulk = self.pool.apply(self.func)
        self.on_bulk_processed(processed_bulk)

