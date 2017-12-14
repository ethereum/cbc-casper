from threading import Thread, Event
from time import sleep
from utils.clock import Clock


class ValidatorClient(Thread, Clock):
    """Validator client software that makes decisions about when
    to make and send new messages"""
    def __init__(self, validator, network):
        Thread.__init__(self)
        Clock.__init__(self)
        self.validator = validator
        self.network = network
        self._stop_event = Event()

    def stop(self):
        self._stop_event.set()

    @property
    def stopped(self):
        return self._stop_event.is_set()

    def run(self):
        print("validator {}:\trunning".format(self.validator.name))

        while(True):
            self.advance_process_time()
            self.retrieve_messages()
            self.make_and_propagate_message()
            self.wait_on_new_message()
            if self.stopped:
                print("validator {}:\tshutting down".format(self.validator.name))
                break

    def wait_on_new_message(self):
        print("validator {}:\twaiting...". format(self.validator.name))
        sleep(1)
        # self.network.message_events[self.validator].wait(1)
        print("validator {}:\tawake".format(self.validator.name))

    def should_make_new_message(self):
        pass

    def make_new_message(self):
        if self.should_make_new_message():
            return self.validator.make_new_message()

    def retrieve_messages(self):
        messages = self.network.receive_all_available(self.validator)
        self.validator.receive_messages(set(messages))
        return messages

    def propagate_message(self, message):
        """ could change this out to send to only peers """
        self.network.send_to_all(message)

    def make_and_propagate_message(self):
        message = self.make_new_message()
        if message:
            print("validator {}:\tmade new message".format(self.validator.name))
            self.propagate_message(message)
        return message
