import time

from fbp.scheduler import Scheduler
from extensions.timer import RepeatedTimer


class TimerScheduler(Scheduler):

    def __init__(self, scheduler_id, name, node_id, scheduler_config):
        Scheduler.__init__(self, scheduler_id, name, node_id, scheduler_config)
        self.timer = RepeatedTimer(self.scheduler_config['interval'], self.schedule)

    def schedule(self):
        print("schedule raised for node %s" % self.node.name)
        time.sleep(0.05)
        self.node.execute_node()
        return

    def start(self):
        print("starting node %s" % self.node.name)
        self.timer.start()

    def stop(self):
        self.timer.cancel()
