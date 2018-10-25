import inspect
from clustering import messagecreator

from clustering.messagehandler import MessageHandler
from functools import partial
from transform import funcs


class FuncHandler(MessageHandler):

    def __init__(self, pool, handler_config):
        MessageHandler.__init__(self, pool, handler_config)
        self._init_funcs()

    def _init_funcs(self):
        self.funcs = []
        self.funcs = inspect.getmembers(funcs, inspect.isfunction)

    def handle_message(self, msg):
        f = next(filter(lambda f: f[0] == msg['func'], self.funcs))[1]
        func = partial(f, msg['node_config'])

        msgs_bulk = msg['msgs_bulk']
        if len(msgs_bulk) > 0:
            processed_bulk = self.pool.map(func, msgs_bulk)
        else:
            processed_bulk = self.pool.apply(func)
        return processed_bulk
