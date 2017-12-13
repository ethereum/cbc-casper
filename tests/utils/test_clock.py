from utils.clock import Clock


def test_new_clock():
    clock = Clock()
    assert clock.time == 0


def test_advance_time():
    clock = Clock()
    assert clock.time == 0

    clock.advance_time()
    assert clock.time == 1

    clock.advance_time(10)
    assert clock.time == 11


def test_set_time():
    clock = Clock()
    clock.set_time(10)
    assert clock.time == 10
    clock.set_time(202020)
    assert clock.time == 202020
