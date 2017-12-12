"""The safety oracle testing module ... """


def test_round_robin_safety(test_lang_runner):
    test_string = (
        'P M0-A SJ1-A RR1-B RR1-C RR1-D RR1-E SJ2-E '
        'SJ3-E SJ4-E CE0-E CE1-E CE2-E CE3-E CE4-E CS0-A '
        'CS1-A CS2-A CS3-A CS4-A P'
    )
    weights = {0: 9.3, 1: 8.2, 2: 7.1, 3: 6, 4: 5}
    test_lang_runner(test_string, weights)


def test_majority_fork_safe(test_lang_runner):
    test_string = (
        # create right hand side of fork and check for safety
        'P M1-A SJ0-A M0-L0 SJ1-L0 M1-L1 SJ0-L1 M0-L2 SJ1-L2 '
        'M1-L3 SJ0-L3 M0-L4 SJ1-L4 CE1-L4 CS1-L0 CE0-L4 CS0-L0 P '
        # other fork shows safe fork blocks, but they remain stuck
        'SJ2-A M2-R0 SJ0-R0 CE0-L4 SJ1-R0 CE0-L4 P'
    )
    weights = {0: 5, 1: 6, 2: 7}
    test_lang_runner(test_string, weights)


def test_no_majority_fork_unsafe(test_lang_runner):
    test_string = (
        # create right hand side of fork and check for no safety
        'P M2-A SJ1-A M1-L0 S0-L0 M0-L1 SJ1-L1 M1-L2 SJ0-L2 '
        'M0-L3 SJ1-L3 M1-L4 SJ0-L4 CE0-L4 CU0-L0 CE1-L4 CU1-L0 P '
        # now, left hand side as well. still no safety
        'SJ3-A M3-R0 SJ4-R0 M4-R1 SJ3-R1 M3-R2 SJ4-R2 M4-R3 '
        'SJ3-R3 M3-R4 SJ4-R4 CE4-R4 CU4-R0 CE3-R4 CU3-R0 P'
    )
    weights = {0: 5, 1: 4.5, 2: 6, 3: 4, 4: 5.25}
    test_lang_runner(test_string, weights)


def test_no_majority_fork_safe_after_union(test_lang_runner):
    test_string = (
        # generate both sides of an extended fork
        'P M2-A SJ1-A M1-L0 SJ0-L0 M0-L1 SJ1-L1 M1-L2 SJ0-L2 '
        'M0-L3 SJ1-L3 M1-L4 SJ0-L4 CE0-L4 CU0-L0 CE1-L4 CU1-L0 P '
        'SJ3-A M3-R0 SJ4-R0 M4-R1 SJ3-R1 M3-R2 SJ4-R2 M4-R3 '
        'SJ3-R3 M3-R4 SJ4-R4 CE4-R4 CU4-R0 CE3-R4 CU3-R0 P '
        # show all validators all blocks
        'SJ0-R4 SJ1-R4 SJ2-R4 SJ2-L4 SJ3-L4 SJ4-L4 '
        # check all have correct forkchoice
        'CE0-L4 CE1-L4 CE2-L4 CE3-L4 CE4-L4 '
        # two rounds of round robin, check have safety on the correct fork
        'RR0-J0 RR0-J1 CS0-L0 P'
    )
    weights = {0: 5, 1: 4.5, 2: 6, 3: 4, 4: 5.25}
    test_lang_runner(test_string, weights)
