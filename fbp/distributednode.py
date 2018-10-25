import abc

from fbp.node import Node
from clustering.broker import Broker


class DistributedNode(Node):

    def __init__(self, node_id, name, concurrency, relations_config, node_config, flow_id, broker):
        Node.__init__(self, node_id, name, concurrency, relations_config, node_config, flow_id, broker)
        #self.__init_broker(node_config['broker_config'])

    #def __init_broker(self, broker_config):
        #self.broker = Broker(broker_config['broker_id'], broker_config['name'], broker_config, self.on_bulk_processed)

    def execute_node(self):
        msg = self._get_msg_bulk()

        msgs_bulk = msg['bulk']

        if msgs_bulk is None:
            return

        if len(msgs_bulk) > 0:
            for request in self._distribute_request_bulk(msgs_bulk, msg['msg_id']):
                self.broker.rpc_call(request)
        else:
            request = self.request_bulk_partition(msgs_bulk, msg['msg_id'])
            print('calling %s args %s' % (request, msgs_bulk))
            self.broker.rpc_call(request)

    def _distribute_request_bulk(self, msgs_bulk, log_msg_id):
        max_batch_size = self.node_config['batch_size']
        print('yoo %s ' % msgs_bulk)
        split_num = (len(msgs_bulk) // max_batch_size) + 1
        try:
            for i in range(split_num):
                request = self.request_bulk_partition(msgs_bulk[i * max_batch_size:(i + 1) * max_batch_size], log_msg_id)
                yield request
        except TypeError as t:

            raise t

    @abc.abstractmethod
    def request_bulk_partition(self, msgs_bulk_partition, log_msg_id):
        return

    def start(self):
        #self.broker.start()
        self.scheduler.start()

