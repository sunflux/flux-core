import abc


class Consumer(object):

    def __init__(self, consumer_config, dst_q):
        self._consumer_config = consumer_config
        self.dst_q = dst_q

    def on_message_received(self, msg):
        self.dst_q.put(msg)

    @abc.abstractmethod
    def run(self):
        """Blocking function"""
        return

    @abc.abstractmethod
    def stop(self):
        return

    @abc.abstractmethod
    def join(self):
        return
