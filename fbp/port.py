import multiprocessing


class Port(object):

    # dst_q == relation q
    def __init__(self, port_id, name, node_q, dst_q, port_config):
        self.id = port_id
        self.name = name

        self.port_config = port_config

        self.q = node_q
        self.dst_q = dst_q

    def enqueue(self, msgs_bulk):
        self.q.put(msgs_bulk)

    def deque(self):
        msgs_bulk = self.q.get()
        self.dst_q.put(msgs_bulk)
