import abc


class Scheduler(object):

    def __init__(self, scheduler_id, name, node, scheduler_config):
        self.id = scheduler_id
        self.name = name
        self.node = node
        self.scheduler_config = scheduler_config

        self.enabled = False

    def enable(self):
        self.enabled = True
        self.start()

    def start(self):
        return

    def disable(self):
        self.enabled = False
        self.stop()

    @abc.abstractmethod
    def schedule(self):
        return

    @abc.abstractmethod
    def stop(self):
        return
