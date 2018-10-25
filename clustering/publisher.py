import abc

from schedulers.timerscheduler import RepeatedTimer


class Publisher(object):

    def __init__(self, publisher_config, src_q):
        self.publisher_config = publisher_config
        self.src_q = src_q

        self.timer = RepeatedTimer(0, self.schedule_msg)

    @abc.abstractmethod
    def publish_message(self, msg):
        return

    def run(self):
        """When implemented override this function and call it at the beginning,
         DO NOTE: Implementation must be a Blocking function"""
        return

    def on_ready(self):
        print('datatatata')
        self.timer.start()

    def stop(self):
        self.timer.cancel()

    def schedule_msg(self):
        if self.src_q.qsize() > 0:
            msg = self.src_q.get(1)
        else:
            return
        if msg is None:
            return
        print(msg)
        self.publish_message(msg)
