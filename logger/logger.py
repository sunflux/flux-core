import abc


class Logger(object):

    def __init__(self):
        return

    @abc.abstractmethod
    def info(self, msg):
        return

    @abc.abstractmethod
    def warn(self, msg):
        return

    @abc.abstractmethod
    def error(self, msg):
        return

    @abc.abstractmethod
    def fatal(self, msg):
        return

    @abc.abstractmethod
    def debug(self, msg):
        return

