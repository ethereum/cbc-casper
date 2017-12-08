from queue import PriorityQueue as PQ


class PriorityQueue(PQ):
    def peek(self):
        return self.queue[0]
