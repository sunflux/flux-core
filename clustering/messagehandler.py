import abc


class MessageHandler(object):

    def __init__(self, pool, handler_config):
        self.pool = pool
        self.handler_config = handler_config

    @abc.abstractmethod
    def handle_message(self, msg):
        return
