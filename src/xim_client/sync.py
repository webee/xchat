from contextlib import contextmanager
import threading


class RWLock(object):

    def __init__(self):
        self.__monitor = threading.Lock()
        self.__exclude = threading.Lock()
        self.readers = 0

    @property
    @contextmanager
    def rlock(self):
        with self.__monitor:
            self.readers += 1
            if self.readers == 1:
                self.__exclude.acquire()
        yield

        with self.__monitor:
            self.readers -= 1
            if self.readers == 0:
                self.__exclude.release()

    @property
    @contextmanager
    def lock(self):
        with self.__exclude:
            yield
