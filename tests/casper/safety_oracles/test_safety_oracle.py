"""The safety oracle testing module ... """
from casper.protocol import Protocol
from simulations.network_delay import no_delay
from simulations.exe_str_generator import generate_rrob_execution


def test_round_robin_safety(so_protocol_instantiated, oracle_class):
    execution_str, _ = generate_rrob_execution(5, 10, no_delay)
    for token in execution_str.split():
        _, _, first_message, _ = Protocol.parse_token(token)
        break
    so_protocol_instantiated.execute(execution_str)

    message = so_protocol_instantiated.messages[first_message]
    validator_set = so_protocol_instantiated.global_validator_set

    for validator in validator_set:
        oracle = oracle_class(message, validator.view, validator_set)
        fault_tolerance, _ = oracle.check_estimate_safety()

        assert fault_tolerance > 0


def test_majority_fork_safe(so_protocol_creator, oracle_class):
    protocol = so_protocol_creator([7, 6, 5])
    # create a fork with the majority of validators
    execution_str = (
        'M-0-A SJ-1-A M-1-B SJ-0-B M-0-C SJ-1-C M-1-D SJ-0-D '
        'M-0-E SJ-1-E M-1-F SJ-0-F M-0-G SJ-1-G M-1-H SJ-0-H '
        'M-0-I SJ-1-I M-1-J SJ-0-J M-0-K SJ-1-K M-1-L SJ-0-L '
    )
    protocol.execute(execution_str)

    message = protocol.messages['A']

    for validator in protocol.global_validator_set.get_validators_by_names([0, 1]):
        oracle = oracle_class(message, validator.view, protocol.global_validator_set)
        fault_tolerance, _ = oracle.check_estimate_safety()

        assert fault_tolerance > 0


def test_no_majority_fork_unsafe(so_protocol_creator, oracle_class):
    protocol = so_protocol_creator([5, 4.5, 6, 4, 5.25])
    test_string = (
        # create right hand side of fork and check for no safety
        'M-2-A SJ-1-A M-1-L0 SJ-0-L0 M-0-L1 SJ-1-L1 M-1-L2 SJ-0-L2 '
        'M-0-L3 SJ-1-L3 M-1-L4 SJ-0-L4 '
        # now, left hand side as well. should still have no safety
        'SJ-3-A M-3-R0 SJ-4-R0 M-4-R1 SJ-3-R1 M-3-R2 SJ-4-R2 M-4-R3 '
        'SJ-3-R3 M-3-R4 SJ-4-R4'
    )
    protocol.execute(test_string)
    validator_set = protocol.global_validator_set

    # left hand side of fork
    for validator in validator_set.get_validators_by_names([0, 1]):
        message = protocol.messages['L0']

        oracle = oracle_class(message, validator.view, validator_set)
        fault_tolerance, _ = oracle.check_estimate_safety()

        assert fault_tolerance == 0

    # right hand side of fork
    for validator in validator_set.get_validators_by_names([2, 3]):
        message = protocol.messages['R0']

        oracle = oracle_class(message, validator.view, validator_set)
        fault_tolerance, _ = oracle.check_estimate_safety()

        assert fault_tolerance == 0


def test_no_majority_fork_safe_after_union(so_protocol_creator, oracle_class):
    protocol = so_protocol_creator([5, 4.5, 6, 4, 5.25])
    test_string = (
        # create right hand side of fork and check for no safety
        'M-2-A SJ-1-A M-1-L0 SJ-0-L0 M-0-L1 SJ-1-L1 M-1-L2 SJ-0-L2 '
        'M-0-L3 SJ-1-L3 M-1-L4 SJ-0-L4 '
        # now, left hand side as well. should still have no safety
        'SJ-3-A M-3-R0 SJ-4-R0 M-4-R1 SJ-3-R1 M-3-R2 SJ-4-R2 M-4-R3 '
        'SJ-3-R3 M-3-R4 SJ-4-R4'
    )
    protocol.execute(test_string)
    validator_set = protocol.global_validator_set

    # left hand side of fork
    for validator in validator_set.get_validators_by_names([0, 1]):
        message = protocol.messages['L0']

        oracle = oracle_class(message, validator.view, validator_set)
        fault_tolerance, _ = oracle.check_estimate_safety()

        assert fault_tolerance == 0

    # right hand side of fork
    for validator in validator_set.get_validators_by_names([2, 3]):
        message = protocol.messages['R0']

        oracle = oracle_class(message, validator.view, validator_set)
        fault_tolerance, _ = oracle.check_estimate_safety()

        assert fault_tolerance == 0

    test_string = (
        # show all validators all messages
        'SJ-0-R4 SJ-1-R4 SJ-2-R4 SJ-2-L4 SJ-3-L4 SJ-4-L4 '
        # two rounds of round robin, check have safety on the correct fork
        'M-0-J0 SJ-1-J0 M-1-J1 SJ-2-J1 M-2-J2 SJ-3-J2 M-3-J3 SJ-4-J3 M-4-J4 SJ-0-J4 '
        'M-0-J01 SJ-1-J01 M-1-J11 SJ-2-J11 M-2-J21 SJ-3-J21 M-3-J31 SJ-4-J31 M-4-J41 SJ-0-J41'
    )
    protocol.execute(test_string)

    validator = validator_set.get_validator_by_name(0)
    message = protocol.messages['L0']

    oracle = oracle_class(message, validator.view, validator_set)
    fault_tolerance, _ = oracle.check_estimate_safety()

    assert fault_tolerance > 0
