from fbp.node import Node


class Processor(Node):

    def __init__(self, node_id, name, concurrency, relations_config, node_config):
        Node.__init__(self, node_id, name, concurrency, relations_config, node_config)

    def execute_node(self):
        print('Processing %s' % self.name)
        msgs_bulk = []
        if len(self.src_relations) > 0:
            if self.q.qsize() > 0:
                print(self.q.qsize())
                msgs_bulk = self.q.get()
                if msgs_bulk is None:
                    print("None")
                    return
            else:
                return

        print('Found bulk %s' % msgs_bulk)

        # self.pool.map_async(self.func, msgs_bulk, self.on_bulk_processed)
        processed_bulk = self.pool.map(self.func, msgs_bulk)
        self.on_bulk_processed(processed_bulk)
