"""The safety oracle testing module ... """


def test_round_robin_safety(oracle_class, test_lang_creator):
    test_lang = test_lang_creator({0: 9.3, 1: 8.2, 2: 7.1, 3: 6, 4: 5})
    test_string = (
        'P M0-A SJ1-A RR1-B RR1-C RR1-D RR1-E SJ2-E '
        'SJ3-E SJ4-E'
    )

    test_lang.parse(test_string)

    message = test_lang.messages['A']

    for validator in test_lang.validator_set:
        oracle = oracle_class(message, validator.view, test_lang.validator_set)
        fault_tolerance, _ = oracle.check_estimate_safety()

        assert fault_tolerance > 0


def test_majority_fork_safe(oracle_class, test_lang_creator):
    test_lang = test_lang_creator({0: 5, 1: 6, 2: 7})
    test_string = (
        # create right hand side of fork and check for safety
        'P M1-A SJ0-A M0-L0 SJ1-L0 M1-L1 SJ0-L1 M0-L2 SJ1-L2 '
        'M1-L3 SJ0-L3 M0-L4 SJ1-L4'
    )
    test_lang.parse(test_string)

    message = test_lang.messages['L0']

    for validator in test_lang.validator_set.get_validators_by_names([0, 1]):
        oracle = oracle_class(message, validator.view, test_lang.validator_set)
        fault_tolerance, _ = oracle.check_estimate_safety()

        assert fault_tolerance > 0


def test_no_majority_fork_unsafe(oracle_class, test_lang_creator):
    test_lang = test_lang_creator({0: 5, 1: 4.5, 2: 6, 3: 4, 4: 5.25})
    test_string = (
        # create right hand side of fork and check for no safety
        'M2-A SJ1-A M1-L0 SJ0-L0 M0-L1 SJ1-L1 M1-L2 SJ0-L2 '
        'M0-L3 SJ1-L3 M1-L4 SJ0-L4 '
        # now, left hand side as well. should still have no safety
        'SJ3-A M3-R0 SJ4-R0 M4-R1 SJ3-R1 M3-R2 SJ4-R2 M4-R3 '
        'SJ3-R3 M3-R4 SJ4-R4'
    )
    test_lang.parse(test_string)

    # left hand side of fork
    for validator in test_lang.validator_set.get_validators_by_names([0, 1]):
        message = test_lang.messages['L0']

        oracle = oracle_class(message, validator.view, test_lang.validator_set)
        fault_tolerance, _ = oracle.check_estimate_safety()

        assert fault_tolerance == 0

    # right hand side of fork
    for validator in test_lang.validator_set.get_validators_by_names([2, 3]):
        message = test_lang.messages['R0']

        oracle = oracle_class(message, validator.view, test_lang.validator_set)
        fault_tolerance, _ = oracle.check_estimate_safety()

        assert fault_tolerance == 0


def test_no_majority_fork_safe_after_union(oracle_class, test_lang_creator):
    test_lang = test_lang_creator({0: 5, 1: 4.5, 2: 6, 3: 4, 4: 5.25})
    test_string = (
        # generate both sides of an extended fork
        'M2-A SJ1-A M1-L0 SJ0-L0 M0-L1 SJ1-L1 M1-L2 SJ0-L2 '
        'M0-L3 SJ1-L3 M1-L4 SJ0-L4 '
        'SJ3-A M3-R0 SJ4-R0 M4-R1 SJ3-R1 M3-R2 SJ4-R2 M4-R3 '
        'SJ3-R3 M3-R4 SJ4-R4'
    )
    test_lang.parse(test_string)

    # left hand side of fork
    for validator in test_lang.validator_set.get_validators_by_names([0, 1]):
        message = test_lang.messages['L0']

        oracle = oracle_class(message, validator.view, test_lang.validator_set)
        fault_tolerance, _ = oracle.check_estimate_safety()

        assert fault_tolerance == 0

    # right hand side of fork
    for validator in test_lang.validator_set.get_validators_by_names([2, 3]):
        message = test_lang.messages['R0']

        oracle = oracle_class(message, validator.view, test_lang.validator_set)
        fault_tolerance, _ = oracle.check_estimate_safety()

        assert fault_tolerance == 0

    test_string = (
        # show all validators all messages
        'SJ0-R4 SJ1-R4 SJ2-R4 SJ2-L4 SJ3-L4 SJ4-L4 '
        # two rounds of round robin, check have safety on the correct fork
        'RR0-J0 RR0-J1'
    )
    test_lang.parse(test_string)

    validator = test_lang.validator_set.get_validator_by_name(0)
    message = test_lang.messages['L0']

    oracle = oracle_class(message, validator.view, test_lang.validator_set)
    fault_tolerance, _ = oracle.check_estimate_safety()

    assert fault_tolerance > 0
