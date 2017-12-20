import time


class Clock(object):
    def __init__(self):
        self._start_process_time = time.process_time()
        self._current_time = 0

    @property
    def time(self):
        return self._current_time

    def advance_time(self, amount=1):
        self._current_time += amount

    def set_time(self, time):
        self._current_time = time

    def advance_process_time(self):
        self._current_time = time.process_time() - self._start_process_time
